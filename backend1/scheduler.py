import time

class Scheduler:
    def __init__(self):
        self.max_service_count = 3
        self.time_slice = 20
        self.service_queue = []  # 正在服务
        self.wait_queue = []     # 等待中
        # [关键修正] 确保使用英文 Key
        self.priority_map = {'high': 3, 'medium': 2, 'low': 1}

    def request_service(self, room_id, speed):
        # 将速度转换为优先级数字
        priority = self.priority_map.get(speed, 1)
        
        # 1. 构造请求对象
        req = {
            "room_id": str(room_id),
            "speed": speed,
            "priority": priority,
            "timestamp": time.time(), # 请求时间
            "service_start": 0
        }
        print(f"[调度] 房间{room_id} 请求 {speed}风 (优先级{priority})")
        
        # 2. 清理旧状态
        self.remove_room(room_id)
        
        # 3. 加入等待队列
        self.wait_queue.append(req)
        
        # 4. 执行全局调度
        self.dispatch()

    def stop_service(self, room_id):
        print(f"[调度] 房间{room_id} 停止服务")
        self.remove_room(room_id)
        self.dispatch() # 有人走了，触发补位

    def remove_room(self, room_id):
        self.service_queue = [r for r in self.service_queue if r['room_id'] != str(room_id)]
        self.wait_queue = [r for r in self.wait_queue if r['room_id'] != str(room_id)]

    def dispatch(self):
        # --- 步骤1：超员强制踢人 ---
        while len(self.service_queue) > self.max_service_count:
            # 排序：优先级低(1在前) > 服务时间长(时间戳小在前)
            self.service_queue.sort(key=lambda x: (x['priority'], x['service_start']))
            victim = self.service_queue.pop(0)
            print(f" -> [溢出] {victim['room_id']} 被移回等待队列")
            victim['timestamp'] = time.time()
            self.wait_queue.append(victim)

        # --- 步骤2：有空位自动补位 ---
        while len(self.service_queue) < self.max_service_count and self.wait_queue:
            # 排序：优先级高(-3在前) > 等待时间长(时间戳小在前)
            self.wait_queue.sort(key=lambda x: (-x['priority'], x['timestamp']))
            best_candidate = self.wait_queue.pop(0)
            self._add_to_service(best_candidate)
            print(f" -> [补位] {best_candidate['room_id']} 开始服务")

        # --- 步骤3：优先级抢占 ---
        if not self.wait_queue or not self.service_queue:
            return

        self.wait_queue.sort(key=lambda x: (-x['priority'], x['timestamp']))
        best_waiter = self.wait_queue[0]

        self.service_queue.sort(key=lambda x: (x['priority'], x['service_start']))
        worst_runner = self.service_queue[0]

        if best_waiter['priority'] > worst_runner['priority']:
            print(f" -> [抢占] {best_waiter['room_id']}(P{best_waiter['priority']}) 替换 {worst_runner['room_id']}(P{worst_runner['priority']})")
            self.wait_queue.pop(0)
            self.service_queue.pop(0)
            
            worst_runner['timestamp'] = time.time()
            self.wait_queue.append(worst_runner)
            self._add_to_service(best_waiter)
            self.dispatch()

    def _add_to_service(self, req):
        req['service_start'] = time.time()
        self.service_queue.append(req)

    def check_time_slice(self):
        """时间片轮转 (带Debug日志)"""
        if not self.wait_queue: return
        
        now = time.time()
        # 遍历等待队列副本
        for waiter in self.wait_queue[:]:
            wait_duration = now - waiter['timestamp']
            
            # [调试日志] 看看系统到底在算什么
            # print(f"[Debug] 房间{waiter['room_id']} 已等待 {wait_duration:.1f}s (阈值: {self.time_slice}s)")

            if wait_duration > self.time_slice:
                # 寻找服务队列中【同优先级】的房间
                candidates = [r for r in self.service_queue if r['priority'] == waiter['priority']]
                
                if candidates:
                    # 找运行最久的
                    victim = min(candidates, key=lambda x: x['service_start'])
                    print(f" -> [轮转] {waiter['room_id']} 等待了{wait_duration:.1f}s -> 替换 {victim['room_id']}")
                    
                    self.wait_queue.remove(waiter)
                    self.service_queue.remove(victim)
                    
                    victim['timestamp'] = time.time()
                    self.wait_queue.append(victim)
                    
                    waiter['service_start'] = time.time()
                    self.service_queue.append(waiter)
                    return 

    def rebalance(self):
        self.dispatch()

    def get_running_rooms(self):
        return [r['room_id'] for r in self.service_queue]
    
    def get_waiting_rooms(self):
        return [r['room_id'] for r in self.wait_queue]