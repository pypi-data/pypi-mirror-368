# ErisPulse-InfoStats 模块

信息统计模块，用于监听和统计来自各个平台的消息、通知和请求事件，提供实时统计数据供其他模块调用。

## 功能特性

- **事件监听**：监听所有平台的 `message`、`notice` 和 `request` 事件
- **实时统计**：统计各类事件总数和按平台分类的统计数据
- **时间范围统计**：支持查询指定时间范围内的事件数量
- **近期事件记录**：保存最近的事件详细信息，包括消息内容
- **内容搜索**：支持按关键词、用户、平台等条件搜索历史事件
- **用户/群组统计**：提供特定用户或群组的详细统计数据
- **持久化存储**：统计数据在系统重启后依然保留

## 安装

```bash
# 通过ErisPulse包管理器安装
epsdk install InfoStats

# 或者直接使用pip安装
pip install ErisPulse-InfoStats
```

## 使用方法

### 1. 基本使用

模块会自动监听所有平台的事件，无需额外配置。

### 2. 获取统计数据

```python
from ErisPulse import sdk

# 注意，需要 `sdk.init()` 之后才能使用

# 获取总体统计信息
total_stats = sdk.InfoStats.get_total_stats()
print(f"总消息数: {total_stats['total_messages']}")
print(f"总通知数: {total_stats['total_notices']}")
print(f"总请求数: {total_stats['total_requests']}")
print(f"总事件数: {total_stats['total_events']}")

# 获取平台分类统计
platform_stats = sdk.InfoStats.get_platform_stats()
print("各平台消息数:", platform_stats['messages_by_platform'])
print("各平台通知数:", platform_stats['notices_by_platform'])
print("各平台请求数:", platform_stats['requests_by_platform'])

# 获取最近的事件记录（默认50条）
recent_events = sdk.InfoStats.get_recent_events()
for event in recent_events:
    print(f"事件: {event['type']} - {event['platform']} - {event['timestamp']}")
    if 'alt_message' in event:
        print(f"  消息内容: {event['alt_message']}")

# 获取最近1分钟内的事件统计
recent_stats = sdk.InfoStats.get_events_in_time_range(1)
print(f"最近1分钟事件数: {recent_stats['total_events']}")
print("按平台分类:", recent_stats['by_platform'])

# 获取最近5分钟每分钟事件数统计
per_minute_stats = sdk.InfoStats.get_events_per_minute(5)
for minute, count in per_minute_stats.items():
    print(f"{minute}: {count} 个事件")
```

### 3. 高级用法

```python
# 获取指定数量的最近事件
recent_100_events = sdk.InfoStats.get_recent_events(100)

# 获取最近10分钟内的事件统计
stats_10min = sdk.InfoStats.get_events_in_time_range(10)

# 获取最近30分钟每分钟事件数统计
per_minute_30min = sdk.InfoStats.get_events_per_minute(30)

# 搜索包含特定关键词的事件
search_results = sdk.InfoStats.search_events(keyword="hello", limit=20)

# 搜索特定用户的所有事件
user_events = sdk.InfoStats.search_events(user_id="user123", limit=100)

# 搜索特定平台的消息事件
telegram_messages = sdk.InfoStats.search_events(
    event_type="message", 
    platform="telegram", 
    limit=50
)

# 获取特定用户的统计数据
user_stats = sdk.InfoStats.get_user_stats("user123")
print(f"用户总消息数: {user_stats['total_messages']}")
print(f"用户活跃平台: {user_stats['platforms']}")

# 获取特定群组的统计数据
group_stats = sdk.InfoStats.get_group_stats("group456")
print(f"群组总消息数: {group_stats['total_messages']}")
print(f"群组参与人数: {group_stats['participant_count']}")

# 重置统计数据
sdk.InfoStats.reset_stats()
```

## API 参考

### `get_total_stats()`
获取总体统计数据
- 返回: `dict` 包含所有统计数据的字典

### `get_platform_stats()]`
获取按平台分类的统计数据
- 返回: `dict` 包含各平台统计数据的字典

### `get_recent_events(limit=50)`
获取最近的事件记录
- 参数: `limit` (int) - 返回事件数量限制，默认50个
- 返回: `list` 最近的事件列表

### `get_events_in_time_range(minutes=1)`
获取指定时间范围内的事件数量
- 参数: `minutes` (int) - 时间范围（分钟），默认1分钟
- 返回: `dict` 时间范围内的统计信息

### `get_events_per_minute(minutes=5)`
获取每分钟事件数量的统计
- 参数: `minutes` (int) - 统计的时间范围（分钟），默认5分钟
- 返回: `dict` 每分钟事件数量统计

### `search_events(keyword=None, event_type=None, platform=None, user_id=None, limit=50)`
搜索事件记录
- 参数:
  - `keyword` (str) - 消息内容关键词搜索
  - `event_type` (str) - 事件类型过滤 ('message', 'notice', 'request')
  - `platform` (str) - 平台过滤
  - `user_id` (str) - 用户ID过滤
  - `limit` (int) - 返回结果数量限制
- 返回: `list` 符合条件的事件列表

### `get_user_stats(user_id)`
获取指定用户的统计数据
- 参数: `user_id` (str) - 用户ID
- 返回: `dict` 用户统计数据

### `get_group_stats(group_id)`
获取指定群组的统计数据
- 参数: `group_id` (str) - 群组ID
- 返回: `dict` 群组统计数据

### `reset_stats()`
重置统计数据

## 数据存储

模块使用 `sdk.env` 进行数据持久化存储，所有统计数据都会保存在以下键中：
- `InfoStats:stats` - 包含所有统计数据的JSON对象

## 注意事项

1. 模块会自动在系统启动时加载并恢复之前的统计数据
2. 事件数据会保存最近1000条记录，超出部分会自动删除
3. 所有统计数据会在每次事件处理后自动保存
4. 消息内容(`alt_message`)会被记录以供后续查询
5. 如果需要清空统计数据，可以调用 `reset_stats()` 方法

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个模块。
