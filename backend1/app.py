import eventlet
# 1. 必须放在最第一行！打补丁以支持协程
eventlet.monkey_patch()

from flask import Flask, make_response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time
import datetime
from scheduler import Scheduler

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bupt_hotel_secret'
CORS(app)
# 2. 明确指定 async_mode 为 eventlet
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 初始化调度器
scheduler = Scheduler()

# === 全局配置与统计数据 ===
global_stats = {
    "today_checkins": 0,    # 今日累计入住
    "total_income": 0.0,    # 历史总结账收入
    "total_energy": 0.0     # 总能耗
}

system_config = {
    "mode": "cool",         # 工作模式: cool / heat
    "maxServices": 3,       # 最大同时服务数 (y)
    "baseRate": 1.0,        # 费率倍数
    "timeSlice": 120,       # 时间片 (S)
    "tempLimit": {"min": 18, "max": 30}
}

# === 房间数据库初始化 (内存) ===
rooms = []
# 初始化 5 个房间
for i in [101, 102, 103, 104, 201]:
    rooms.append({
        "id": str(i), 
        "status": "free",       # free / occupied
        "temp": 28.0,           # 当前温度 (初始值)
        "target": 25.0,         # 目标温度
        "speed": "low",         # 风速
        "currentCost": 0.0,     # 当前总费用 (空调费)
        "isOn": False,          # 面板开关 (用户意愿)
        "isRunning": False,     # 实际运行 (调度结果)
        "guest": None,          # 住户信息 {name, idCard...}
        "request": None,        # 入住请求暂存
        "checkout_pending": False, # 是否正在请求结账
        "details": [],          # 历史详单列表
        "active_log": None,     # 当前正在进行的详单片段
        "ac_cycles": 0,         # 开关机次数 (用于计算房费: 1次=1天)
        "last_update_time": time.time(), # 上次物理更新时间 (用于回温计算)
        "last_request_time": time.time() # 上次请求时间
    })

# 辅助函数: 根据ID获取房间对象
def get_room(room_id):
    return next((r for r in rooms if r['id'] == str(room_id)), None)

# 辅助函数: 获取格式化时间
def get_time_str(timestamp=None):
    if timestamp is None: timestamp = time.time()
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

# 辅助函数: 归档当前的详单记录
def archive_log(room):
    if room['active_log']:
        log = room['active_log']
        log['end_time_str'] = get_time_str()
        log['duration'] = int(time.time() - log['start_timestamp'])
        
        # 记录这一段结束时的累积费用快照
        log['cumulative_fee'] = room['currentCost'] 
        
        # 防止 0 秒记录
        if log['duration'] == 0: log['duration'] = 1
        
        # 插入到列表头部 (最新的在前)
        room['details'].insert(0, log)
        room['active_log'] = None

# === 核心物理模拟循环 (后台线程) ===
def simulation_loop():
    print(">>> 后台物理引擎已启动 (每秒刷新)")
    while True:
        # 使用 socketio.sleep 避免阻塞协程
        socketio.sleep(1)
        
        # 1. 检查时间片轮转 (公平调度)
        scheduler.check_time_slice()
        
        # 获取当前被调度器批准送风的房间ID列表
        running_ids = scheduler.get_running_rooms()
        
        updated = False
        current_time = time.time()
        
        for room in rooms:
            is_running_now = room['id'] in running_ids
            
            # --- A. 自动温控逻辑 (到达目标停机 / 温差重启) ---
            if room['status'] == 'occupied' and room['isOn']:
                restart_diff = 1.0 # 重启温差阈值
                
                # 制冷模式
                if system_config['mode'] == 'cool':
                    # 运行中 && 温度已降至目标 -> 自动待机 (释放资源)
                    if is_running_now and room['temp'] <= room['target']:
                        scheduler.stop_service(room['id'])
                    # 待机中 && 温度回升超过1度 -> 自动唤醒
                    elif not is_running_now and room['temp'] >= (room['target'] + restart_diff):
                        scheduler.request_service(room['id'], room['speed'])
                
                # 制热模式
                elif system_config['mode'] == 'heat':
                    # 运行中 && 温度已升至目标 -> 自动待机
                    if is_running_now and room['temp'] >= room['target']:
                        scheduler.stop_service(room['id'])
                    # 待机中 && 温度掉落超过1度 -> 自动唤醒
                    elif not is_running_now and room['temp'] <= (room['target'] - restart_diff):
                        scheduler.request_service(room['id'], room['speed'])

            # --- B. 状态同步与详单切片 ---
            if room['isRunning'] != is_running_now:
                # 状态发生变化，先归档旧日志
                if room['active_log']: archive_log(room)
                
                # 如果变成了运行状态，开启新日志
                if is_running_now:
                    room['active_log'] = {
                        'request_time_str': get_time_str(room.get('last_request_time', time.time())),
                        'start_time_str': get_time_str(),
                        'start_timestamp': time.time(),
                        'end_time_str': '-',
                        'speed': room['speed'],
                        'rate': 0,          # 费率 (稍后计算)
                        'current_fee': 0.0, # 本段费用
                        'cumulative_fee': 0.0,
                        'duration': 0
                    }
                
                room['isRunning'] = is_running_now
                updated = True

            # --- C. 计费与物理变化 (仅运行状态) ---
            if is_running_now:
                updated = True
                # 费率配置
                base_rate = system_config['baseRate']
                rate_map = {'high': 1.0 * base_rate, 'medium': 0.5 * base_rate, 'low': 0.333 * base_rate}
                # 能耗配置 (kWh/s)
                energy_map = {'high': 0.05, 'medium': 0.03, 'low': 0.01}

                # 计算本秒增量
                cost = rate_map.get(room['speed'], 0.333)
                energy = energy_map.get(room['speed'], 0.01)
                
                # 更新全局统计
                global_stats['total_energy'] += energy
                
                # 更新当前日志
                if room['active_log']:
                    room['active_log']['cost'] = room['active_log'].get('cost', 0.0) + cost
                    room['active_log']['energy'] = room['active_log'].get('energy', 0.0) + energy
                    room['active_log']['rate'] = cost # 记录当前费率

                # 模拟温度变化 (每秒)
                step = 0.2 # 变温速率
                if system_config['mode'] == 'cool':
                    if room['temp'] > room['target']: room['temp'] -= step
                else:
                    if room['temp'] < room['target']: room['temp'] += step

            # --- D. 房间回温逻辑 (非运行状态) ---
            elif not is_running_now:
                # 累计时间差，每 10 秒回温一次
                time_diff = current_time - room['last_update_time']
                
                if time_diff >= 10.0:
                    room['last_update_time'] = current_time # 重置计时器
                    
                    recover_step = 0.5 # 回温幅度
                    env_temp = 30.0 if system_config['mode'] == 'cool' else 10.0
                    
                    if system_config['mode'] == 'cool':
                        # 制冷模式下，温度回升，但不超过环境温度
                        if room['temp'] < env_temp:
                            room['temp'] += recover_step
                            updated = True
                    else:
                        # 制热模式下，温度下降
                        if room['temp'] > env_temp:
                            room['temp'] -= recover_step
                            updated = True
            
            # 如果正在运行，持续更新时间戳，防止关机瞬间触发回温
            if is_running_now:
                room['last_update_time'] = current_time 

            # --- E. 强制对账与精度修正 ---
            # 总费用 = 历史详单总和 + 当前活跃详单费用
            history_total = sum(item.get('cost', 0) for item in room['details'])
            active_total = room['active_log'].get('cost', 0) if room['active_log'] else 0.0
            
            # 更新房间总费用
            room['currentCost'] = round(history_total + active_total, 2)
            room['temp'] = round(room['temp'], 2)
            
            if room['active_log']:
                room['active_log']['current_fee'] = round(active_total, 2)

        # 广播数据更新
        if updated:
            socketio.emit('sync_data', {'rooms': rooms, 'stats': global_stats})

# 启动后台任务
socketio.start_background_task(simulation_loop)

# === 文件导出接口 ===

# 1. 导出账单 (TXT)
@app.route('/export/bill/<room_id>')
def export_bill(room_id):
    room = get_room(room_id)
    if not room or not room['guest']: return "无数据", 404
    
    # 住宿费规则: 开关机次数 = 天数
    stay_days = room['ac_cycles'] if room['ac_cycles'] > 0 else 1
    accom_fee = stay_days * 100.0
    total_fee = room['currentCost'] + accom_fee
    
    content = "=== 波普特酒店 - 结账单 ===\n"
    content += f"打印时间: {get_time_str()}\n"
    content += "------------------------------\n"
    content += f"房间号  : {room['id']}\n"
    content += f"住户姓名: {room['guest']['name']}\n"
    content += f"入住时间: {get_time_str(float(room['guest']['checkInTime']))}\n"
    content += f"离开时间: {get_time_str()}\n"
    content += "------------------------------\n"
    content += f"空调费用: {room['currentCost']:.2f} 元\n"
    content += f"住宿天数: {stay_days} 天 (按服务次数)\n"
    content += f"住宿费用: {accom_fee:.2f} 元\n"
    content += "------------------------------\n"
    content += f"总计应收: {total_fee:.2f} 元\n"
    
    response = make_response(content)
    response.headers["Content-Disposition"] = f"attachment; filename=Bill_Room{room_id}.txt"
    response.mimetype = 'text/plain'
    return response

# 2. 导出详单 (CSV)
@app.route('/export/detail/<room_id>')
def export_detail(room_id):
    room = get_room(room_id)
    if not room: return "无数据", 404
    
    content = "房间号,请求时间,服务开始时间,服务结束时间,服务时长(秒),风速,本段费用(元),累积费用(元)\n"
    
    # 构建完整日志列表 (历史 + 当前)
    all_logs = list(room['details'])
    if room['active_log']:
        t = room['active_log'].copy()
        t['end_time_str'] = '运行中'
        t['duration'] = int(time.time() - t['start_timestamp'])
        t['cumulative_fee'] = room['currentCost']
        all_logs.insert(0, t)
    
    # 倒序输出 (最新的在最前)
    for log in all_logs: # 或者 reversed(all_logs) 看你需求
        line = f"{room['id']},{log['request_time_str']},{log['start_time_str']},{log['end_time_str']},{log['duration']},{log['speed']},{log.get('current_fee', 0):.2f},{log.get('cumulative_fee', 0):.2f}\n"
        content += line
        
    response = make_response(content)
    response.headers["Content-Disposition"] = f"attachment; filename=Detail_Room{room_id}.csv"
    response.mimetype = 'text/csv'
    return response

# === WebSocket 事件处理 ===

@socketio.on('connect')
def handle_connect():
    # 连接时发送所有状态
    emit('sync_data', {'rooms': rooms, 'config': system_config, 'stats': global_stats})

@socketio.on('client_action')
def handle_action(data):
    room_id = data.get('roomId')
    action = data.get('action')
    value = data.get('value')
    
    # --- 处理系统设置更新 ---
    if action == 'update_settings':
        print(f"[设置] 更新配置: {value}")
        system_config.update(value)
        
        # 同步更新调度器参数
        if 'maxServices' in value:
            scheduler.max_service_count = int(value['maxServices'])
            # [重要] 参数变小后，立即执行重平衡
            scheduler.rebalance()
            
        if 'timeSlice' in value:
            scheduler.time_slice = int(value['timeSlice'])
            
        # 广播新配置和房间状态
        emit('sync_data', {'config': system_config}, broadcast=True)
        emit('sync_data', {'rooms': rooms}, broadcast=True)
        return

    room = get_room(room_id)
    if not room: return

    # --- 1. 入住流程 ---
    if action == 'submit_checkin':
        print(f"[入住] 房间 {room_id} 提交申请")
        room['request'] = value

    elif action == 'approve_checkin':
        if room['request']:
            print(f"[入住] 房间 {room_id} 批准入住")
            room['status'] = 'occupied'
            room['guest'] = {
                "name": room['request']['name'],
                "idCard": room['request']['idCard'],
                "checkInTime": str(time.time())
            }
            # 重置所有状态
            room['request'] = None
            room['isOn'] = False
            room['currentCost'] = 0.0
            room['details'] = []
            room['ac_cycles'] = 0
            room['checkout_pending'] = False
            
            global_stats['today_checkins'] += 1
            emit('sync_data', {'stats': global_stats}, broadcast=True)

    # --- 2. 结账流程 ---
    elif action == 'request_checkout':
        print(f"[结账] 房间 {room_id} 发起结账")
        room['checkout_pending'] = True
        room['isOn'] = False
        scheduler.stop_service(room_id) # 停止调度
        if room['active_log']: archive_log(room) # 归档日志

    elif action == 'confirm_checkout':
        print(f"[结账] 房间 {room_id} 确认完成")
        stay_days = room['ac_cycles'] if room['ac_cycles'] > 0 else 1
        total_bill = room['currentCost'] + (stay_days * 100.0)
        
        global_stats['total_income'] += total_bill
        
        # 重置为空闲
        room.update({
            'status': 'free', 'guest': None, 'request': None, 'checkout_pending': False,
            'isOn': False, 'currentCost': 0.0, 'details': [], 'active_log': None, 'ac_cycles': 0,
            'temp': 28.0 # 重置室温
        })
        scheduler.stop_service(room_id)
        emit('sync_data', {'stats': global_stats}, broadcast=True)

    # --- 3. 空调控制流程 ---
    elif action == 'power':
        print(f"[控制] 房间 {room_id} 开关: {value}")
        room['isOn'] = value
        if value:
            room['last_request_time'] = time.time()
            room['ac_cycles'] += 1 # 增加住宿天数计数
            scheduler.request_service(room_id, room['speed'])
        else:
            scheduler.stop_service(room_id)
            
    elif action == 'speed':
        print(f"[控制] 房间 {room_id} 调速: {value}")
        room['speed'] = value
        if room['isOn']:
            room['last_request_time'] = time.time()
            # 调速可能触发抢占
            scheduler.request_service(room_id, value)
            
    elif action == 'temp':
        print(f"[控制] 房间 {room_id} 调温: {value}")
        room['target'] = float(value)
        # 如果开机中，调温被视为新请求（可选，这里简化为只更新参数，不重新排队）
        # 如果需要调温也重新排队，可以取消下面的注释：
        # if room['isOn']:
        #      room['last_request_time'] = time.time()
        #      scheduler.request_service(room_id, room['speed'])

    # 广播最新状态
    emit('sync_data', {'rooms': rooms}, broadcast=True)

if __name__ == '__main__':
    print(">>> 波普特酒店后端服务已就绪 (Port: 5000)")
    # host='0.0.0.0' 允许局域网访问
    socketio.run(app, host='0.0.0.0', port=5000)