from ErisPulse import sdk
from collections import defaultdict, deque
from datetime import datetime, timedelta

class Main:
    def __init__(self):
        self.sdk = sdk
        self.logger = sdk.logger
        self.env = sdk.env
        
        # 初始化统计数据
        self.stats = {
            'total_messages': 0,
            'total_notices': 0,
            'total_requests': 0,
            'messages_by_platform': defaultdict(int),
            'notices_by_platform': defaultdict(int),
            'requests_by_platform': defaultdict(int),
            'recent_events': deque(maxlen=1000)  # 保存最近1000个事件
        }
        
        # 从持久化存储加载数据
        self._load_stats_from_storage()
        
        # 注册事件监听器
        self._register_event_listeners()
        
        self.logger.info("信息统计模块已加载")
    
    @staticmethod
    def should_eager_load():
        return True
    
    def _load_stats_from_storage(self):
        try:
            # 从env加载统计数据
            stored_stats = self.env.get("InfoStats:stats", {})
            if stored_stats:
                self.stats['total_messages'] = stored_stats.get('total_messages', 0)
                self.stats['total_notices'] = stored_stats.get('total_notices', 0)
                self.stats['total_requests'] = stored_stats.get('total_requests', 0)
                
                # 加载平台统计数据
                self.stats['messages_by_platform'] = defaultdict(
                    int, 
                    stored_stats.get('messages_by_platform', {})
                )
                self.stats['notices_by_platform'] = defaultdict(
                    int, 
                    stored_stats.get('notices_by_platform', {})
                )
                self.stats['requests_by_platform'] = defaultdict(
                    int, 
                    stored_stats.get('requests_by_platform', {})
                )
                
                # 加载最近事件（如果有存储的话）
                stored_events = stored_stats.get('recent_events', [])
                for event_data in stored_events:
                    event_info = {
                        'type': event_data['type'],
                        'platform': event_data['platform'],
                        'timestamp': datetime.fromisoformat(event_data['timestamp']),
                        'detail_type': event_data['detail_type'],
                        'user_id': event_data.get('user_id'),
                        'group_id': event_data.get('group_id'),
                        'alt_message': event_data.get('alt_message'),
                        'message_id': event_data.get('message_id')
                    }
                    self.stats['recent_events'].append(event_info)
                
                self.logger.info("统计数据已从持久化存储加载")
        except Exception as e:
            self.logger.error(f"加载统计数据时出错: {e}")
    
    def _save_stats_to_storage(self):
        try:
            # 将defaultdict转换为普通dict以便序列化
            stats_to_save = {
                'total_messages': self.stats['total_messages'],
                'total_notices': self.stats['total_notices'],
                'total_requests': self.stats['total_requests'],
                'messages_by_platform': dict(self.stats['messages_by_platform']),
                'notices_by_platform': dict(self.stats['notices_by_platform']),
                'requests_by_platform': dict(self.stats['requests_by_platform']),
                'recent_events': [
                    {
                        'type': event['type'],
                        'platform': event['platform'],
                        'timestamp': event['timestamp'].isoformat(),
                        'detail_type': event['detail_type'],
                        'user_id': event.get('user_id'),
                        'group_id': event.get('group_id'),
                        'alt_message': event.get('alt_message'),
                        'message_id': event.get('message_id')
                    }
                    for event in self.stats['recent_events']
                ]
            }
            
            # 保存到env
            self.env.set("InfoStats:stats", stats_to_save)
        except Exception as e:
            self.logger.error(f"保存统计数据时出错: {e}")
    
    def _register_event_listeners(self):
        @sdk.adapter.on("message")
        async def on_message(data):
            await self._handle_message_event(data)
            
        @sdk.adapter.on("notice")
        async def on_notice(data):
            await self._handle_notice_event(data)
            
        @sdk.adapter.on("request")
        async def on_request(data):
            await self._handle_request_event(data)
    
    async def _handle_message_event(self, data):
        self.stats['total_messages'] += 1
        platform = data.get('platform', 'unknown')
        self.stats['messages_by_platform'][platform] += 1
        
        # 记录事件到最近事件队列
        event_info = {
            'type': 'message',
            'platform': platform,
            'timestamp': datetime.now(),
            'detail_type': data.get('detail_type', 'unknown'),
            'user_id': data.get('user_id'),
            'group_id': data.get('group_id'),
            'alt_message': data.get('alt_message', ''),
            'message_id': data.get('message_id')
        }
        self.stats['recent_events'].append(event_info)
        
        # 保存统计数据
        self._save_stats_to_storage()
        
        self.logger.debug(f"记录消息事件: {platform} - {data.get('detail_type', 'unknown')}")
    
    async def _handle_notice_event(self, data):
        self.stats['total_notices'] += 1
        platform = data.get('platform', 'unknown')
        self.stats['notices_by_platform'][platform] += 1
        
        # 记录事件到最近事件队列
        event_info = {
            'type': 'notice',
            'platform': platform,
            'timestamp': datetime.now(),
            'detail_type': data.get('detail_type', 'unknown'),
            'user_id': data.get('user_id'),
            'group_id': data.get('group_id'),
            'alt_message': data.get('alt_message', ''),  # 有些通知也有消息内容
            'message_id': data.get('message_id')
        }
        self.stats['recent_events'].append(event_info)
        
        # 保存统计数据
        self._save_stats_to_storage()
        
        self.logger.debug(f"记录通知事件: {platform} - {data.get('detail_type', 'unknown')}")
    
    async def _handle_request_event(self, data):
        self.stats['total_requests'] += 1
        platform = data.get('platform', 'unknown')
        self.stats['requests_by_platform'][platform] += 1
        
        # 记录事件到最近事件队列
        event_info = {
            'type': 'request',
            'platform': platform,
            'timestamp': datetime.now(),
            'detail_type': data.get('detail_type', 'unknown'),
            'user_id': data.get('user_id'),
            'group_id': data.get('group_id'),
            'alt_message': data.get('comment', ''),  # 请求事件通常有comment字段
            'message_id': data.get('request_id')     # 请求事件通常有request_id
        }
        self.stats['recent_events'].append(event_info)
        
        # 保存统计数据
        self._save_stats_to_storage()
        
        self.logger.debug(f"记录请求事件: {platform} - {data.get('detail_type', 'unknown')}")
    
    def get_total_stats(self):
        return {
            'total_messages': self.stats['total_messages'],
            'total_notices': self.stats['total_notices'],
            'total_requests': self.stats['total_requests'],
            'total_events': self.stats['total_messages'] + self.stats['total_notices'] + self.stats['total_requests']
        }
    
    def get_platform_stats(self):
        return {
            'messages_by_platform': dict(self.stats['messages_by_platform']),
            'notices_by_platform': dict(self.stats['notices_by_platform']),
            'requests_by_platform': dict(self.stats['requests_by_platform'])
        }
    
    def get_recent_events(self, limit=50):
        events = list(self.stats['recent_events'])
        return events[-limit:] if len(events) > limit else events
    
    def get_events_in_time_range(self, minutes=1):
        since_time = datetime.now() - timedelta(minutes=minutes)
        count = 0
        messages = 0
        notices = 0
        requests = 0
        by_platform = defaultdict(int)
        
        for event in self.stats['recent_events']:
            if event['timestamp'] >= since_time:
                count += 1
                if event['type'] == 'message':
                    messages += 1
                elif event['type'] == 'notice':
                    notices += 1
                elif event['type'] == 'request':
                    requests += 1
                by_platform[event['platform']] += 1
        
        return {
            'total_events': count,
            'messages': messages,
            'notices': notices,
            'requests': requests,
            'by_platform': dict(by_platform),
            'time_range_minutes': minutes
        }
    
    def get_events_per_minute(self, minutes=5):
        now = datetime.now()
        result = {}
        
        for i in range(minutes):
            target_time = now - timedelta(minutes=i)
            minute_key = target_time.strftime("%H:%M")
            
            # 计算该分钟内的事件数
            count = 0
            start_time = target_time.replace(second=0, microsecond=0)
            end_time = start_time + timedelta(minutes=1)
            
            for event in self.stats['recent_events']:
                if start_time <= event['timestamp'] < end_time:
                    count += 1
                    
            result[minute_key] = count
            
        return result
    
    def search_events(self, keyword=None, event_type=None, platform=None, user_id=None, limit=50):
        results = []
        
        for event in reversed(self.stats['recent_events']):  # 从最新开始搜索
            # 类型过滤
            if event_type and event['type'] != event_type:
                continue
                
            # 平台过滤
            if platform and event['platform'] != platform:
                continue
                
            # 用户ID过滤
            if user_id and event.get('user_id') != user_id:
                continue
                
            # 关键词搜索
            if keyword:
                alt_message = event.get('alt_message', '')
                if keyword.lower() not in alt_message.lower():
                    continue
                    
            results.append(event)
            
            # 限制结果数量
            if len(results) >= limit:
                break
                
        return results
    
    def get_user_stats(self, user_id):
        user_messages = 0
        user_notices = 0
        user_requests = 0
        platforms = set()
        recent_user_events = []
        
        for event in self.stats['recent_events']:
            if event.get('user_id') == user_id:
                if event['type'] == 'message':
                    user_messages += 1
                elif event['type'] == 'notice':
                    user_notices += 1
                elif event['type'] == 'request':
                    user_requests += 1
                    
                platforms.add(event['platform'])
                recent_user_events.append(event)
        
        return {
            'user_id': user_id,
            'total_messages': user_messages,
            'total_notices': user_notices,
            'total_requests': user_requests,
            'total_events': user_messages + user_notices + user_requests,
            'platforms': list(platforms),
            'recent_events': recent_user_events[-10:] if len(recent_user_events) > 10 else recent_user_events
        }
    
    def get_group_stats(self, group_id):
        group_messages = 0
        group_notices = 0
        group_requests = 0
        platforms = set()
        participants = set()
        recent_group_events = []
        
        for event in self.stats['recent_events']:
            if event.get('group_id') == group_id:
                if event['type'] == 'message':
                    group_messages += 1
                elif event['type'] == 'notice':
                    group_notices += 1
                elif event['type'] == 'request':
                    group_requests += 1
                    
                platforms.add(event['platform'])
                if event.get('user_id'):
                    participants.add(event['user_id'])
                recent_group_events.append(event)
        
        return {
            'group_id': group_id,
            'total_messages': group_messages,
            'total_notices': group_notices,
            'total_requests': group_requests,
            'total_events': group_messages + group_notices + group_requests,
            'platforms': list(platforms),
            'participant_count': len(participants),
            'participants': list(participants),
            'recent_events': recent_group_events[-10:] if len(recent_group_events) > 10 else recent_group_events
        }
    
    def reset_stats(self):
        self.stats['total_messages'] = 0
        self.stats['total_notices'] = 0
        self.stats['total_requests'] = 0
        self.stats['messages_by_platform'].clear()
        self.stats['notices_by_platform'].clear()
        self.stats['requests_by_platform'].clear()
        self.stats['recent_events'].clear()
        
        # 保存重置后的数据
        self._save_stats_to_storage()
        
        self.logger.info("统计数据已重置")

