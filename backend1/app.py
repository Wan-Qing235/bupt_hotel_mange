import eventlet
eventlet.monkey_patch()

from flask import Flask, make_response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time
import datetime
# 确保你目录下有一个修复好的 scheduler.py
from scheduler import Scheduler 

class HotelServer:
    def __init__(self):
        # 1. 初始化 Flask 和 SocketIO
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'bupt_hotel_secret'
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='eventlet')
        
        # 2. 初始化调度器
        self.scheduler = Scheduler()

        # 3. 初始化全局数据
        self.global_stats = {
            "today_checkins": 0,
            "total_income": 0.0,
            "total_energy": 0.0
        }

        self.system_config = {
            "mode": "cool",
            "maxServices": 3,
            "baseRate": 1.0,
            "timeSlice": 20, # 建议设为 15-20 之间以配合测试脚本
            "tempLimit": {"min": 18, "max": 25}
        }

        self.recent_logs = []
        self.rooms = self._init_rooms()

        # 4. 注册路由和事件
        self._register_routes()
        self._register_socket_events()

        # 5. 启动后台物理模拟任务
        self.socketio.start_background_task(self.simulation_loop)

    def _init_rooms(self):
        """初始化房间数据"""
        rooms = []
        room_configs = [
            {"id": "101", "temp": 32.0, "rate": 100.0},
            {"id": "102", "temp": 28.0, "rate": 125.0},
            {"id": "103", "temp": 30.0, "rate": 150.0},
            {"id": "104", "temp": 29.0, "rate": 200.0},
            {"id": "201", "temp": 35.0, "rate": 100.0}
        ]
        
        for config in room_configs:
            rooms.append({
                "id": config["id"], 
                "status": "free",
                "temp": config["temp"],
                "initial_temp": config["temp"],
                "room_rate": config["rate"],
                "target": 25.0,
                "speed": "medium",
                "currentCost": 0.0,
                "isOn": False,
                "isRunning": False,
                "guest": None,
                "request": None,
                "checkout_pending": False,
                "details": [],
                "active_log": None,
                "ac_cycles": 0,
                "last_update_time": time.time(),
                "last_request_time": time.time()
            })
        return rooms

    def get_room(self, room_id):
        return next((r for r in self.rooms if r['id'] == str(room_id)), None)

    @staticmethod
    def get_time_str(timestamp=None):
        if timestamp is None: timestamp = time.time()
        return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    def archive_log(self, room):
        if room['active_log']:
            log = room['active_log']
            log['end_time_str'] = self.get_time_str()
            log['duration'] = int(time.time() - log['start_timestamp'])
            log['cumulative_fee'] = room['currentCost'] 
            if log['duration'] == 0: log['duration'] = 1
            room['details'].insert(0, log)
            room['active_log'] = None

    def push_log(self, log_type, title, desc):
        """推送日志"""
        time_str = datetime.datetime.now().strftime("%H:%M")
        log_payload = {
            "type": log_type,
            "title": title,
            "desc": desc,
            "time": time_str
        }
        self.recent_logs.insert(0, log_payload)
        if len(self.recent_logs) > 20: 
            self.recent_logs.pop()
            
        print(f"--- [LOG PUSH] {title} ---")
        self.socketio.emit('new_log', log_payload)

    def _register_routes(self):
        """注册 Flask 路由"""
        @self.app.route('/export/bill/<room_id>')
        def export_bill(room_id):
            room = self.get_room(room_id)
            if not room or not room['guest']: return "无数据", 404
            
            stay_days = room['ac_cycles'] if room['ac_cycles'] > 0 else 1
            room_rate = room.get('room_rate', 100.0)
            accom_fee = stay_days * room_rate
            total_fee = room['currentCost'] + accom_fee
            
            content = "=== 波普特酒店 - 结账单 ===\n"
            content += f"打印时间: {self.get_time_str()}\n"
            content += "------------------------------\n"
            content += f"房间号  : {room['id']}\n"
            content += f"住户姓名: {room['guest']['name']}\n"
            content += f"入住时间: {self.get_time_str(float(room['guest']['checkInTime']))}\n"
            content += "------------------------------\n"
            content += f"空调费用: {room['currentCost']:.2f} 元\n"
            content += f"住宿费用: {accom_fee:.2f} 元 ({room_rate}元/天 x {stay_days})\n"
            content += "------------------------------\n"
            content += f"总计应收: {total_fee:.2f} 元\n"
            
            response = make_response(content)
            response.headers["Content-Disposition"] = f"attachment; filename=Bill_Room{room_id}.txt"
            response.mimetype = 'text/plain'
            return response

        @self.app.route('/export/detail/<room_id>')
        def export_detail(room_id):
            room = self.get_room(room_id)
            if not room: return "无数据", 404
            
            content = "房间号,请求时间,服务开始时间,服务结束时间,服务时长(秒),风速,本段费用(元),累积费用(元)\n"
            all_logs = list(room['details'])
            if room['active_log']:
                t = room['active_log'].copy()
                t['end_time_str'] = '运行中'
                t['duration'] = int(time.time() - t['start_timestamp'])
                t['cumulative_fee'] = room['currentCost']
                all_logs.insert(0, t)
            
            for log in all_logs:
                line = f"{room['id']},{log['request_time_str']},{log['start_time_str']},{log['end_time_str']},{log['duration']},{log['speed']},{log.get('current_fee', 0):.2f},{log.get('cumulative_fee', 0):.2f}\n"
                content += line
            
            response = make_response(content)
            response.headers["Content-Disposition"] = f"attachment; filename=Detail_Room{room_id}.csv"
            response.mimetype = 'text/csv'
            return response

    def _register_socket_events(self):
        """注册 SocketIO 事件"""
        @self.socketio.on('connect')
        def handle_connect():
            emit('sync_data', {
                'rooms': self.rooms, 
                'config': self.system_config, 
                'stats': self.global_stats
            })
            emit('log_history', self.recent_logs)

        @self.socketio.on('client_action')
        def handle_action(data):
            self.process_client_action(data)

    def process_client_action(self, data):
        """处理具体的客户端指令"""
        room_id = data.get('roomId')
        action = data.get('action')
        value = data.get('value')
        
        # 1. 系统设置更新
        if action == 'update_settings':
            print(f"[设置] 更新配置: {value}")
            self.system_config.update(value)
            if 'maxServices' in value:
                self.scheduler.max_service_count = int(value['maxServices'])
                self.scheduler.rebalance()
            if 'timeSlice' in value:
                self.scheduler.time_slice = int(value['timeSlice'])
            
            self.socketio.emit('sync_data', {'config': self.system_config})
            self.socketio.emit('sync_data', {'rooms': self.rooms})
            self.push_log('system', '系统参数更新', '管理员修改了调度配置')
            return

        room = self.get_room(room_id)
        if not room: return

        # 2. 入住申请
        if action == 'submit_checkin':
            print(f"[入住] 房间 {room_id} 提交申请")
            room['request'] = value
            self.push_log('request', f'{room_id} 入住申请', f'住户: {value["name"]}')

        # 3. 批准入住
        elif action == 'approve_checkin':
            if room['request']:
                print(f"[入住] 房间 {room_id} 批准入住")
                guest_name = room['request']['name']
                room['status'] = 'occupied'
                room['guest'] = {
                    "name": guest_name,
                    "idCard": room['request']['idCard'],
                    "checkInTime": str(time.time())
                }
                room['request'] = None
                room['isOn'] = False
                room['currentCost'] = 0.0
                room['details'] = []
                room['ac_cycles'] = 0
                room['checkout_pending'] = False
                room['temp'] = room['initial_temp']
                
                self.global_stats['today_checkins'] += 1
                self.socketio.emit('sync_data', {'stats': self.global_stats})
                self.push_log('checkin', f'{room_id} 办理入住成功', f'欢迎 {guest_name}')

        # 4. 结账申请
        elif action == 'request_checkout':
            print(f"[结账] 房间 {room_id} 发起结账")
            room['checkout_pending'] = True
            room['isOn'] = False
            self.scheduler.stop_service(room_id)
            if room['active_log']: self.archive_log(room)
            self.push_log('request', f'{room_id} 发起结账请求', '请前台及时处理')

        # 5. 确认退房
        elif action == 'confirm_checkout':
            print(f"[结账] 房间 {room_id} 确认完成")
            stay_days = room['ac_cycles'] if room['ac_cycles'] > 0 else 1
            room_rate = room.get('room_rate', 100.0)
            total_bill = room['currentCost'] + (stay_days * room_rate)
            self.global_stats['total_income'] += total_bill
            
            room.update({
                'status': 'free', 'guest': None, 'request': None, 'checkout_pending': False,
                'isOn': False, 'currentCost': 0.0, 'details': [], 'active_log': None, 'ac_cycles': 0,
                'temp': room['initial_temp'],
                'speed': 'medium'
            })
            
            self.scheduler.stop_service(room_id)
            self.socketio.emit('sync_data', {'stats': self.global_stats})
            self.push_log('checkout', f'{room_id} 退房完成', f'收入: ¥{total_bill:.2f}')

        # 6. 空调控制
        elif action == 'power':
            print(f"[控制] 房间 {room_id} 开关: {value}")
            room['isOn'] = value
            if value:
                room['last_request_time'] = time.time()
                room['ac_cycles'] += 1
                # [修正] 开机默认重置为目标25度，中风
                room['target'] = 25.0
                room['speed'] = 'medium'
                self.scheduler.request_service(room_id, room['speed'])
            else:
                self.scheduler.stop_service(room_id)
                
        elif action == 'speed':
            # [优化] 如果风速没变，不发请求，减少日志刷屏
            if room['speed'] != value:
                room['speed'] = value
                if room['isOn']:
                    room['last_request_time'] = time.time()
                    self.scheduler.request_service(room_id, value)
                
        elif action == 'temp':
            target_temp = float(value)
            min_temp = self.system_config['tempLimit']['min']
            max_temp = self.system_config['tempLimit']['max']
            if min_temp <= target_temp <= max_temp:
                room['target'] = target_temp
            else:
                print(f"[警告] 非法温度设置: {target_temp}")

        # 广播更新
        self.socketio.emit('sync_data', {'rooms': self.rooms})

    # ==================================================
    # [补丁] 简单的状态打印，防止报错
    # ==================================================
    def print_queue_status(self, trigger_action="Unknown"):
        running_len = len(self.scheduler.service_queue)
        waiting_len = len(self.scheduler.wait_queue)
        # 如果觉得控制台太吵，可以注释掉下面这行
        print(f"--- [触发: {trigger_action}] 服务中: {running_len}, 等待中: {waiting_len} ---")

    # ==================================================
    # [核心] 后台物理引擎 (每秒刷新)
    # ==================================================
    def simulation_loop(self):
        print(">>> 后台物理引擎已启动 (每秒刷新)")
        while True:
            # 1. 心跳 (每秒一次)
            self.socketio.sleep(1)
            
            # 2. 调度器检查时间片
            self.scheduler.check_time_slice()
            
            # 3. 获取队列状态 (用于避免死循环请求)
            running_ids = self.scheduler.get_running_rooms()
            # 确保 scheduler.py 里有 get_waiting_rooms 方法，或者直接访问
            try:
                waiting_ids = self.scheduler.get_waiting_rooms()
            except:
                waiting_ids = [r['room_id'] for r in self.scheduler.wait_queue]
            
            updated = False
            current_time = time.time()
            
            for room in self.rooms:
                old_temp = room['temp']
                is_running_now = room['id'] in running_ids
                is_waiting_now = room['id'] in waiting_ids 
                
                # --- A. 自动温控逻辑 (到达目标停机 / 偏离目标开机) ---
                if room['status'] == 'occupied' and room['isOn']:
                    restart_diff = 1.0
                    
                    if self.system_config['mode'] == 'cool':
                        if is_running_now and room['temp'] <= room['target']:
                            self.scheduler.stop_service(room['id'])
                            self.print_queue_status(f"Auto Stop {room['id']}")
                        
                        # [关键] 只有当既没运行、也没排队时，才重新请求
                        elif not is_running_now and not is_waiting_now and room['temp'] >= (room['target'] + restart_diff):
                            self.scheduler.request_service(room['id'], room['speed'])
                            self.print_queue_status(f"Auto Start {room['id']}")

                    elif self.system_config['mode'] == 'heat':
                        if is_running_now and room['temp'] >= room['target']:
                            self.scheduler.stop_service(room['id'])
                            self.print_queue_status(f"Auto Stop {room['id']}")
                        
                        elif not is_running_now and not is_waiting_now and room['temp'] <= (room['target'] - restart_diff):
                            self.scheduler.request_service(room['id'], room['speed'])
                            self.print_queue_status(f"Auto Start {room['id']}")

                # --- B. 状态同步 (归档旧日志，开启新日志) ---
                if room['isRunning'] != is_running_now:
                    if room['active_log']: self.archive_log(room)
                    if is_running_now:
                        room['active_log'] = {
                            'request_time_str': self.get_time_str(time.time()),
                            'start_time_str': self.get_time_str(),
                            'start_timestamp': time.time(),
                            'end_time_str': '-',
                            'speed': room['speed'],
                            'rate': 0, 'current_fee': 0.0, 'cumulative_fee': 0.0, 'duration': 0
                        }
                    room['isRunning'] = is_running_now
                    updated = True

                # --- C. 物理变温 (运行与回温) ---
                if is_running_now:
                    # === 1. 运行中 ===
                    updated = True
                    # 只要在运行，就更新时间锚点
                    room['last_update_time'] = current_time 
                    
                    # 计费 (每秒 1/10 的基础费率)
                    base_rate = self.system_config['baseRate']
                    rate_map = {'high': 1.0, 'medium': 0.5, 'low': 0.333}
                    cost = (rate_map.get(room['speed'], 0.5) * base_rate) / 10.0
                    
                    room['currentCost'] += cost
                    self.global_stats['total_energy'] += 0.01 # 简单模拟耗能
                    
                    if room['active_log']:
                        room['active_log']['cost'] = room['active_log'].get('cost', 0.0) + cost
                        room['active_log']['rate'] = cost

                    # 变温 (根据风速)
                    temp_step_map = {'high': 0.1, 'medium': 0.05, 'low': 0.033}
                    step = temp_step_map.get(room['speed'], 0.05)
                
                    if self.system_config['mode'] == 'cool':
                        if room['temp'] > room['target']: 
                            room['temp'] = max(room['target'], room['temp'] - step)
                    else:
                        if room['temp'] < room['target']: 
                            room['temp'] = min(room['target'], room['temp'] + step)

                else:
                    # === 2. 回温 (关机/排队) ===
                    # [关键修改] 使用平滑回温：每秒 0.05度 (即 10秒 0.5度)
                    # 这样测试脚本无论何时截图都能看到变化
                    recover_step = 0.05 
                    env_temp = room['initial_temp']
                    
                    if self.system_config['mode'] == 'cool':
                        if room['temp'] < env_temp:
                            room['temp'] = min(env_temp, room['temp'] + recover_step)
                            updated = True
                    else:
                        if room['temp'] > env_temp:
                            room['temp'] = max(env_temp, room['temp'] - recover_step)
                            updated = True
                
                # --- E. 数据格式化 ---
                room['currentCost'] = round(room['currentCost'], 2)
                room['temp'] = round(room['temp'], 2) 
                if room['active_log']:
                    room['active_log']['current_fee'] = round(room['active_log'].get('cost',0), 2)

            if updated:
                self.socketio.emit('sync_data', {'rooms': self.rooms, 'stats': self.global_stats})

    def run(self):
        print(">>> 波普特酒店后端服务已就绪 (OOP版) (Port: 5000)")
        self.socketio.run(self.app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    server = HotelServer()
    server.run()