import time

class Scheduler:
    def __init__(self):
        self.max_service_count = 3
        self.time_slice = 120
        self.service_queue = [] # 正在服务
        self.wait_queue = []    # 等待中
        self.priority_map = {'high': 3, 'medium': 2, 'low': 1}

    def request_service(self, room_id, speed):
        """用户请求服务"""
        priority = self.priority_map.get(speed, 1)
        req = {
            'room_id': room_id,
            'speed': speed,
            'priority': priority,
            'timestamp': time.time(),
            'service_start': 0
        }
        print(f"[调度] 房间{room_id} 请求 {speed}风")
        self.remove_room(room_id)
        self._schedule(req)

    def _schedule(self, req):
        """核心调度：进服务队列 or 进等待队列"""
        # 1. 有空位 -> 进
        if len(self.service_queue) < self.max_service_count:
            self._add_to_service(req)
            return

        # 2. 没空位 -> 抢占
        self.service_queue.sort(key=lambda x: (x['priority'], x['service_start']))
        lowest = self.service_queue[0]

        if req['priority'] > lowest['priority']:
            print(f"  -> [抢占] {req['room_id']} 踢掉 {lowest['room_id']}")
            self._move_to_wait(lowest)
            self._add_to_service(req)
        else:
            print(f"  -> [等待] {req['room_id']} 进入等待队列")
            self.wait_queue.append(req)

    # === [核心修复] 完美的重平衡逻辑 ===
    def rebalance(self):
        print(f"[调度] 执行重平衡 (Max: {self.max_service_count})")
        
        # 1. 情况A: 服务数 > 最大限制 -> 踢人 (缩容)
        while len(self.service_queue) > self.max_service_count:
            # 排序：优先级低在前，服务时间长在前
            self.service_queue.sort(key=lambda x: (x['priority'], x['service_start']))
            victim = self.service_queue.pop(0)
            print(f"  -> [溢出] {victim['room_id']} 被移入等待队列")
            # 移入等待队列 (重置等待时间)
            victim['timestamp'] = time.time()
            self.wait_queue.append(victim)

        # 2. 情况B: 服务数 < 最大限制 且 有人在排队 -> 拉人 (扩容)
        # 这就是你刚才缺少的逻辑！
        while len(self.service_queue) < self.max_service_count and self.wait_queue:
            self._fill_vacancy()

    def check_time_slice(self):
        """时间片轮转"""
        if not self.wait_queue: return
        now = time.time()
        for waiter in self.wait_queue[:]:
            if (now - waiter['timestamp']) > self.time_slice:
                # 找同级对手
                candidates = [r for r in self.service_queue if r['priority'] == waiter['priority']]
                if candidates:
                    victim = min(candidates, key=lambda x: x['service_start'])
                    print(f"  -> [轮转] {waiter['room_id']} 替换 {victim['room_id']}")
                    self._move_to_wait(victim)
                    self.wait_queue.remove(waiter)
                    self._add_to_service(waiter)
                    return

    def stop_service(self, room_id):
        self.remove_room(room_id)
        self._fill_vacancy()

    def remove_room(self, room_id):
        self.service_queue = [r for r in self.service_queue if r['room_id'] != room_id]
        self.wait_queue = [r for r in self.wait_queue if r['room_id'] != room_id]

    def _add_to_service(self, req):
        req['service_start'] = time.time()
        self.service_queue.append(req)

    def _move_to_wait(self, req):
        self.remove_room(req['room_id'])
        req['timestamp'] = time.time()
        self.wait_queue.append(req)

    def _fill_vacancy(self):
        """补位逻辑：优先级高 > 等待久"""
        if len(self.service_queue) < self.max_service_count and self.wait_queue:
            self.wait_queue.sort(key=lambda x: (-x['priority'], x['timestamp']))
            next_room = self.wait_queue.pop(0)
            self._add_to_service(next_room)
            print(f"  -> [补位] {next_room['room_id']} 开始送风")

    def get_running_rooms(self):
        return [r['room_id'] for r in self.service_queue]