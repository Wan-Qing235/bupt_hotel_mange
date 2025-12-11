import eventlet
# 1. 必须放在最第一行！打补丁以支持协程
eventlet.monkey_patch()

from flask import Flask, make_response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time
import datetime
from scheduler import Scheduler

class HotelServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'bupt_hotel_secret'
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='eventlet')
        
        self.scheduler = Scheduler()

        self.global_stats = {
            "today_checkins": 0,
            "total_income": 0.0,
            "total_energy": 0.0
        }

        self.system_config = {
            "mode": "cool",         # 默认制冷
            "maxServices": 3,
            "baseRate": 1.0,
            "timeSlice": 120,
            "tempLimit": {"min": 18, "max": 25}
        }

        self.recent_logs = []
        self.rooms = self._init_rooms()

        self._register_routes()
        self._register_socket_events()
        self.socketio.start_background_task(self.simulation_loop)

    def _init_rooms(self):
        """初始化房间数据"""
        rooms = []
        room_configs = [
            {"id": "101", "cool_temp": 32.0, "heat_temp": 10.0, "rate": 100.0},
            {"id": "102", "cool_temp": 28.0, "heat_temp": 15.0, "rate": 125.0},
            {"id": "103", "cool_temp": 30.0, "heat_temp": 18.0, "rate": 150.0},
            {"id": "104", "cool_temp": 29.0, "heat_temp": 12.0, "rate": 200.0},
            {"id": "201", "cool_temp": 35.0, "heat_temp": 14.0, "rate": 100.0}
        ]
        
        current_mode = self.system_config['mode']

        for config in room_configs:
            init_temp = config["cool_temp"] if current_mode == 'cool' else config["heat_temp"]
            init_target = 25.0 if current_mode == 'cool' else 23.0
            
            rooms.append({
                "id": config["id"], 
                "status": "free",
                "cool_init_temp": config["cool_temp"],
                "heat_init_temp": config["heat_temp"],
                "initial_temp": init_temp,
                "temp": init_temp,
                "room_rate": config["rate"],
                "target": init_target,
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
        room_id = data.get('roomId')
        action = data.get('action')
        value = data.get('value')
        
        # 1. 系统设置更新
        if action == 'update_settings':
            print(f"[设置] 更新配置: {value}")
            old_mode = self.system_config['mode']
            self.system_config.update(value)
            new_mode = self.system_config['mode']
            
            if old_mode != new_mode:
                print(f"[系统] 模式切换: {old_mode} -> {new_mode}, 重置所有房间温度")
                for r in self.rooms:
                    r['initial_temp'] = r['cool_init_temp'] if new_mode == 'cool' else r['heat_init_temp']
                    if not r['isOn']:
                        r['temp'] = r['initial_temp']
                    r['target'] = 25.0 if new_mode == 'cool' else 22.0
            
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

        # [新增] 处理打印请求
        if action == 'request_print_detail':
            print(f"[请求] 房间 {room_id} 请求打印详单")
            self.push_log('request', f'{room_id} 请求打印详单', '住户申请获取纸质报表')
            return

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
                
                room['speed'] = 'medium'
                room['target'] = 25.0 if self.system_config['mode'] == 'cool' else 22.0
                
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
                
                room['target'] = 25.0 if self.system_config['mode'] == 'cool' else 22.0
                room['speed'] = 'medium'
                
                self.scheduler.request_service(room_id, room['speed'])
            else:
                self.scheduler.stop_service(room_id)
                
        elif action == 'speed':
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

        self.socketio.emit('sync_data', {'rooms': self.rooms})

    def simulation_loop(self):
        print(">>> 后台物理引擎已启动 (每秒刷新)")
        while True:
            self.socketio.sleep(1)
            self.scheduler.check_time_slice()
            running_ids = self.scheduler.get_running_rooms()
            
            try:
                waiting_ids = self.scheduler.get_waiting_rooms()
            except:
                waiting_ids = [r['room_id'] for r in self.scheduler.wait_queue]
            
            updated = False
            current_time = time.time()
            
            for room in self.rooms:
                is_running_now = room['id'] in running_ids
                is_waiting_now = room['id'] in waiting_ids 
                
                # --- A. 自动温控逻辑 ---
                if room['status'] == 'occupied' and room['isOn']:
                    restart_diff = 1.0
                    
                    if self.system_config['mode'] == 'cool':
                        if is_running_now and room['temp'] <= room['target']:
                            self.scheduler.stop_service(room['id'])
                        elif not is_running_now and not is_waiting_now and room['temp'] >= (room['target'] + restart_diff):
                            self.scheduler.request_service(room['id'], room['speed'])
                    
                    elif self.system_config['mode'] == 'heat':
                        if is_running_now and room['temp'] >= room['target']:
                            self.scheduler.stop_service(room['id'])
                        elif not is_running_now and not is_waiting_now and room['temp'] <= (room['target'] - restart_diff):
                            self.scheduler.request_service(room['id'], room['speed'])

                # --- B. 状态同步 ---
                if room['isRunning'] != is_running_now:
                    if room['active_log']: self.archive_log(room)
                    if is_running_now:
                        room['active_log'] = {
                            'request_time_str': self.get_time_str(room.get('last_request_time', time.time())),
                            'start_time_str': self.get_time_str(),
                            'start_timestamp': time.time(),
                            'end_time_str': '-',
                            'speed': room['speed'],
                            'rate': 0,
                            'current_fee': 0.0,
                            'cumulative_fee': 0.0,
                            'duration': 0
                        }
                    room['isRunning'] = is_running_now
                    updated = True

                # --- C. 计费与物理变化 ---
                if is_running_now:
                    updated = True
                    base_rate = self.system_config['baseRate']
                    rate_map = {'high': (1.0 * base_rate) / 10.0, 'medium': (0.5 * base_rate) / 10.0, 'low': (0.333 * base_rate) / 10.0}
                    energy_map = {'high': 0.05, 'medium': 0.03, 'low': 0.01}

                    cost = rate_map.get(room['speed'], 0.333 / 10.0)
                    energy = energy_map.get(room['speed'], 0.01)
                    
                    self.global_stats['total_energy'] += energy
                    
                    if room['active_log']:
                        room['active_log']['cost'] = room['active_log'].get('cost', 0.0) + cost
                        room['active_log']['energy'] = room['active_log'].get('energy', 0.0) + energy
                        room['active_log']['rate'] = cost

                    temp_step_map = {'high': 0.1, 'medium': 0.05, 'low': 0.033}
                    step = temp_step_map.get(room['speed'], 0.05)
                    
                    if self.system_config['mode'] == 'cool':
                        if room['temp'] > room['target']: 
                            room['temp'] = max(room['target'], room['temp'] - step)
                    else:
                        if room['temp'] < room['target']: 
                            room['temp'] = min(room['target'], room['temp'] + step)

                # --- D. 回温逻辑 (线性平滑) ---
                elif not is_running_now:
                    time_diff = current_time - room['last_update_time']
                    
                    if time_diff >= 2.0:
                        room['last_update_time'] = current_time
                        recover_step = 0.1 
                        
                        if self.system_config['mode'] == 'cool':
                            env_temp = room['cool_init_temp']
                            if room['temp'] < env_temp:
                                room['temp'] = min(env_temp, room['temp'] + recover_step)
                                updated = True
                        else:
                            env_temp = room['heat_init_temp']
                            if room['temp'] > env_temp:
                                room['temp'] = max(env_temp, room['temp'] - recover_step)
                                updated = True
                
                if is_running_now:
                    room['last_update_time'] = current_time 

                # --- E. 强制对账 ---
                history_total = sum(item.get('cost', 0) for item in room['details'])
                active_total = room['active_log'].get('cost', 0) if room['active_log'] else 0.0
                room['currentCost'] = round(history_total + active_total, 2)
                room['temp'] = round(room['temp'], 2)
                if room['active_log']:
                    room['active_log']['current_fee'] = round(active_total, 2)

            if updated:
                self.socketio.emit('sync_data', {'rooms': self.rooms, 'stats': self.global_stats})

    def run(self):
        print(">>> 波普特酒店后端服务已就绪 (OOP版) (Port: 5000)")
        self.socketio.run(self.app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    server = HotelServer()
    server.run()