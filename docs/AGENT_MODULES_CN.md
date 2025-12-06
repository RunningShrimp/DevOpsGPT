# DevOpsGPT 智能代理模块

## 概述

本文档介绍了添加到 DevOpsGPT 的三个新的 AI 驱动的智能代理模块：

1. **日志分析Agent** - 自动分析应用日志，识别异常模式
2. **监控告警Agent** - 对接监控系统，自动分析指标异常
3. **智能工单系统** - 自动创建和管理工单，提供智能推荐

## 1. 日志分析Agent模块

### 功能特性
- 集成 Elasticsearch，实现日志存储和检索
- 自动识别异常模式
- AI 驱动的故障报告生成
- 严重性分类（低、中、高、严重）

### 配置说明

在 `env.yaml` 中添加：

```yaml
# 日志分析Agent配置
ELASTICSEARCH_ENABLED: false
ELASTICSEARCH_HOST: "localhost"
ELASTICSEARCH_PORT: 9200
ELASTICSEARCH_USERNAME: ""
ELASTICSEARCH_PASSWORD: ""
ELASTICSEARCH_INDEX_PREFIX: "devopsgpt-logs"
```

### API 接口

#### 分析日志
```
POST /agent/log_analysis/analyze
```
请求示例：
```json
{
  "service_name": "my-service",
  "requirement_id": 123,
  "time_range_hours": 24
}
```

响应示例：
```json
{
  "success": true,
  "record_id": 1,
  "analysis": {
    "service_name": "my-service",
    "anomaly_detected": true,
    "patterns": [...],
    "fault_report": "...",
    "severity": "high"
  }
}
```

#### 搜索日志
```
POST /agent/log_analysis/search_logs
```

#### 索引日志
```
POST /agent/log_analysis/index_logs
```

#### 获取分析记录
```
GET /agent/log_analysis/records?requirement_id=123
```

### 使用示例

```python
from app.pkgs.agents.log_analysis_agent import LogAnalysisAgent

agent = LogAnalysisAgent()
result = agent.analyze_logs(
    service_name="my-service",
    requirement_id=123,
    time_range_hours=24
)

print(f"检测到异常: {result['anomaly_detected']}")
print(f"故障报告: {result['fault_report']}")
```

## 2. 监控告警Agent模块

### 功能特性
- 集成 Prometheus 和 Grafana
- 实时指标异常检测
- AI 驱动的解决方案推荐
- 告警严重性分类
- 历史告警追踪

### 配置说明

在 `env.yaml` 中添加：

```yaml
# 监控告警Agent配置
PROMETHEUS_ENABLED: false
PROMETHEUS_URL: "http://localhost:9090"
GRAFANA_ENABLED: false
GRAFANA_URL: "http://localhost:3000"
GRAFANA_API_KEY: ""
```

### API 接口

#### 检查服务指标
```
POST /agent/monitoring/check_metrics
```
请求示例：
```json
{
  "service_name": "my-service",
  "requirement_id": 123
}
```

响应示例：
```json
{
  "success": true,
  "results": {
    "service_name": "my-service",
    "alerts": [
      {
        "metric_name": "cpu_usage",
        "current_value": 0.85,
        "threshold": 0.8,
        "severity": "warning"
      }
    ]
  }
}
```

#### AI 分析告警
```
POST /agent/monitoring/analyze_alert
```

#### 获取活动告警
```
GET /agent/monitoring/alerts?requirement_id=123
```

#### 解决告警
```
POST /agent/monitoring/alerts/resolve
```

### 监控指标

系统自动监控以下指标：
- CPU 使用率
- 内存使用率
- HTTP 错误率 (5xx)

### 使用示例

```python
from app.pkgs.agents.monitoring_alert_agent import MonitoringAlertAgent

agent = MonitoringAlertAgent()
results = agent.check_service_metrics("my-service", requirement_id=123)

for alert in results['alerts']:
    print(f"告警: {alert['metric_name']} = {alert['current_value']}")
    
    # 获取 AI 推荐方案
    analysis = agent.analyze_alert(alert)
    print(f"推荐方案: {analysis['recommended_solutions']}")
```

## 3. 智能工单系统模块

### 功能特性
- 集成 Jira 进行工单管理
- 从日志和告警自动创建工单
- 历史工单分析
- AI 驱动的解决方案推荐
- 相似工单检测
- 基于历史数据的自动分配

### 配置说明

在 `env.yaml` 中添加：

```yaml
# 智能工单系统配置
JIRA_ENABLED: false
JIRA_URL: "https://your-domain.atlassian.net"
JIRA_USERNAME: ""
JIRA_API_TOKEN: ""
JIRA_PROJECT_KEY: ""
```

### API 接口

#### 从日志分析创建工单
```
POST /agent/ticket/create_from_log
```
请求示例：
```json
{
  "requirement_id": 123,
  "log_analysis_id": 1
}
```

响应示例：
```json
{
  "success": true,
  "ticket_key": "DEVOPS-123",
  "ticket_url": "https://jira.example.com/browse/DEVOPS-123",
  "ticket_id": 1,
  "priority": "High",
  "recommendations": [...],
  "similar_tickets": [...]
}
```

#### 从告警创建工单
```
POST /agent/ticket/create_from_alert
```

#### 手动创建工单
```
POST /agent/ticket/create_manual
```

#### 获取工单列表
```
GET /agent/ticket/tickets?requirement_id=123
```

#### 更新工单状态
```
POST /agent/ticket/ticket/update_status
```

#### 从 Jira 同步
```
POST /agent/ticket/ticket/sync_from_jira
```

### 使用示例

```python
from app.pkgs.agents.ticket_system_agent import TicketSystemAgent

agent = TicketSystemAgent()

# 从故障数据创建工单
result = agent.create_ticket_from_fault(
    requirement_id=123,
    service_name="my-service",
    fault_data=log_analysis_result,
    source_type='log_analysis',
    source_id=1
)

print(f"创建工单: {result['ticket_key']}")
print(f"工单链接: {result['ticket_url']}")
print(f"推荐方案: {result['recommendations']}")
print(f"相似工单: {result['similar_tickets']}")
```

## 集成工作流

### 典型使用场景

1. **日志分析**: 服务生成日志，索引到 Elasticsearch
2. **异常检测**: 日志分析Agent检测异常并生成故障报告
3. **告警生成**: 监控Agent检测指标异常
4. **自动创建工单**: 工单系统Agent自动创建 Jira 工单
5. **AI 推荐**: 系统基于历史数据提供解决方案推荐
6. **解决追踪**: 追踪工单并记录解决时间

### 完整工作流示例

```python
# 1. 分析日志
log_agent = LogAnalysisAgent()
log_result = log_agent.analyze_logs("my-service", requirement_id=123)

if log_result['anomaly_detected']:
    # 2. 创建日志分析记录
    from app.models.log_analysis_record import LogAnalysisRecord
    log_record = LogAnalysisRecord.create_record(
        requirement_id=123,
        service_name="my-service",
        log_source='elasticsearch',
        anomaly_detected=True,
        anomaly_patterns=log_result['patterns'],
        fault_report=log_result['fault_report'],
        severity=log_result['severity']
    )
    
    # 3. 自动创建 Jira 工单
    ticket_agent = TicketSystemAgent()
    ticket_result = ticket_agent.create_ticket_from_fault(
        requirement_id=123,
        service_name="my-service",
        fault_data=log_result,
        source_type='log_analysis',
        source_id=log_record.id
    )
    
    print(f"已创建工单: {ticket_result['ticket_key']}")
    print(f"AI 推荐方案: {ticket_result['recommendations']}")
```

## 数据库结构

### LogAnalysisRecord（日志分析记录）
- `id`: 主键
- `requirement_id`: 关联需求
- `service_name`: 服务名称
- `log_source`: 日志来源
- `anomaly_detected`: 是否检测到异常
- `anomaly_patterns`: 异常模式（JSON）
- `fault_report`: 故障报告
- `severity`: 严重性（低/中/高/严重）
- `analyzed_log_count`: 分析的日志数量
- `analysis_duration`: 分析耗时
- `created_at`, `updated_at`: 时间戳

### MonitoringAlert（监控告警）
- `id`: 主键
- `requirement_id`: 关联需求
- `service_name`: 服务名称
- `alert_name`, `alert_type`: 告警标识
- `metric_name`: 监控指标名称
- `current_value`, `threshold_value`: 指标值
- `anomaly_detected`: 是否检测到异常
- `anomaly_description`: 异常描述
- `severity`: 严重性（info/warning/critical）
- `recommended_solutions`: 推荐方案（JSON）
- `auto_resolved`: 是否自动解决
- `source_type`, `source_url`: 来源信息
- `created_at`, `updated_at`, `resolved_at`: 时间戳

### TicketRecord（工单记录）
- `id`: 主键
- `requirement_id`: 关联需求
- `service_name`: 服务名称
- `ticket_key`: Jira 工单键值
- `ticket_url`: Jira 工单链接
- `ticket_title`, `ticket_description`: 工单内容
- `ticket_type`: 类型（bug/task/story）
- `priority`: 优先级
- `status`: 状态（open/in_progress/resolved/closed）
- `source_type`, `source_id`: 来源信息
- `fault_summary`: 故障摘要
- `recommended_solutions`: 推荐方案（JSON）
- `similar_tickets`: 相似工单（JSON）
- `auto_assigned_to`: 自动分配给
- `resolution_time`: 解决时间（小时）
- `created_at`, `updated_at`, `resolved_at`: 时间戳

## 安全注意事项

1. **Elasticsearch**: 生产环境使用认证和 SSL/TLS
2. **Prometheus/Grafana**: 使用适当的认证保护 API 端点
3. **Jira**: 使用 API token 而不是密码
4. **敏感数据**: 索引前确保日志不包含敏感信息

## 最佳实践

1. **日志索引**: 定期索引日志但避免过载 Elasticsearch
2. **指标监控**: 为服务设置适当的阈值
3. **工单创建**: 定期审查自动创建的工单
4. **历史数据**: 保留历史工单以获得更好的 AI 推荐
5. **误报**: 审查并调整异常检测阈值

## 故障排除

### Elasticsearch 连接问题
- 验证 `ELASTICSEARCH_HOST` 和 `ELASTICSEARCH_PORT` 正确
- 检查网络连接
- 验证认证凭据

### Prometheus/Grafana 连接问题
- 确保服务运行且可访问
- 验证 API URL 和 token
- 检查防火墙规则

### Jira 集成问题
- 验证 JIRA_URL 正确（包含 https://）
- 检查 API token 有适当的权限
- 确保项目键值存在

## 未来增强

1. 使用机器学习改进异常检测
2. 集成更多监控工具（Datadog、New Relic 等）
3. 支持更多工单系统（ServiceNow、Zendesk 等）
4. 使用嵌入向量的高级模式识别
5. 自动修复操作
6. 集成 ChatOps 平台（Slack、Teams 等）

## 技术支持

问题咨询：
- GitHub Issues: https://github.com/kuafuai/DevOpsGPT/issues
- 邮箱: service@kuafuai.net
- Discord: https://discord.gg/4RMUCZwnxF
