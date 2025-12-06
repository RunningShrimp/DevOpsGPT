# DevOpsGPT Agent Modules

## Overview

This document describes the three new AI-powered agent modules added to DevOpsGPT:

1. **Log Analysis Agent** (日志分析Agent)
2. **Monitoring Alert Agent** (监控告警Agent)
3. **Intelligent Ticket System** (智能工单系统)

## 1. Log Analysis Agent Module

### Features
- Integration with Elasticsearch for log storage and retrieval
- Automatic anomaly pattern detection
- AI-powered fault report generation
- Severity classification (low, medium, high, critical)

### Configuration

Add to your `env.yaml`:

```yaml
# Log Analysis Agent Configuration
ELASTICSEARCH_ENABLED: false
ELASTICSEARCH_HOST: "localhost"
ELASTICSEARCH_PORT: 9200
ELASTICSEARCH_USERNAME: ""
ELASTICSEARCH_PASSWORD: ""
ELASTICSEARCH_INDEX_PREFIX: "devopsgpt-logs"
```

### API Endpoints

#### Analyze Logs
```
POST /agent/log_analysis/analyze
```
Request:
```json
{
  "service_name": "my-service",
  "requirement_id": 123,
  "time_range_hours": 24
}
```

Response:
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

#### Search Logs
```
POST /agent/log_analysis/search_logs
```

#### Index Logs
```
POST /agent/log_analysis/index_logs
```

#### Get Analysis Records
```
GET /agent/log_analysis/records?requirement_id=123
```

### Usage Example

```python
from app.pkgs.agents.log_analysis_agent import LogAnalysisAgent

agent = LogAnalysisAgent()
result = agent.analyze_logs(
    service_name="my-service",
    requirement_id=123,
    time_range_hours=24
)

print(f"Anomaly detected: {result['anomaly_detected']}")
print(f"Fault report: {result['fault_report']}")
```

## 2. Monitoring Alert Agent Module

### Features
- Integration with Prometheus and Grafana
- Real-time metric anomaly detection
- AI-powered solution recommendations
- Alert severity classification
- Historical alert tracking

### Configuration

Add to your `env.yaml`:

```yaml
# Monitoring Alert Agent Configuration
PROMETHEUS_ENABLED: false
PROMETHEUS_URL: "http://localhost:9090"
GRAFANA_ENABLED: false
GRAFANA_URL: "http://localhost:3000"
GRAFANA_API_KEY: ""
```

### API Endpoints

#### Check Service Metrics
```
POST /agent/monitoring/check_metrics
```
Request:
```json
{
  "service_name": "my-service",
  "requirement_id": 123
}
```

Response:
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

#### Analyze Alert with AI
```
POST /agent/monitoring/analyze_alert
```

#### Get Active Alerts
```
GET /agent/monitoring/alerts?requirement_id=123
```

#### Resolve Alert
```
POST /agent/monitoring/alerts/resolve
```

### Monitored Metrics

The agent automatically monitors:
- CPU usage rate
- Memory usage percentage
- HTTP error rates (5xx)

### Usage Example

```python
from app.pkgs.agents.monitoring_alert_agent import MonitoringAlertAgent

agent = MonitoringAlertAgent()
results = agent.check_service_metrics("my-service", requirement_id=123)

for alert in results['alerts']:
    print(f"Alert: {alert['metric_name']} = {alert['current_value']}")
    
    # Get AI recommendations
    analysis = agent.analyze_alert(alert)
    print(f"Recommendations: {analysis['recommended_solutions']}")
```

## 3. Intelligent Ticket System Module

### Features
- Integration with Jira for ticket creation
- Automatic ticket creation from logs and alerts
- Historical ticket analysis
- AI-powered solution recommendations
- Similar ticket detection
- Auto-assignment based on historical data

### Configuration

Add to your `env.yaml`:

```yaml
# Intelligent Ticket System Configuration
JIRA_ENABLED: false
JIRA_URL: "https://your-domain.atlassian.net"
JIRA_USERNAME: ""
JIRA_API_TOKEN: ""
JIRA_PROJECT_KEY: ""
```

### API Endpoints

#### Create Ticket from Log Analysis
```
POST /agent/ticket/create_from_log
```
Request:
```json
{
  "requirement_id": 123,
  "log_analysis_id": 1
}
```

Response:
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

#### Create Ticket from Alert
```
POST /agent/ticket/create_from_alert
```

#### Create Manual Ticket
```
POST /agent/ticket/create_manual
```

#### Get Tickets
```
GET /agent/ticket/tickets?requirement_id=123
```

#### Update Ticket Status
```
POST /agent/ticket/ticket/update_status
```

#### Sync from Jira
```
POST /agent/ticket/ticket/sync_from_jira
```

### Usage Example

```python
from app.pkgs.agents.ticket_system_agent import TicketSystemAgent

agent = TicketSystemAgent()

# Create ticket from fault data
result = agent.create_ticket_from_fault(
    requirement_id=123,
    service_name="my-service",
    fault_data=log_analysis_result,
    source_type='log_analysis',
    source_id=1
)

print(f"Created ticket: {result['ticket_key']}")
print(f"Ticket URL: {result['ticket_url']}")
print(f"Recommendations: {result['recommendations']}")
print(f"Similar tickets: {result['similar_tickets']}")
```

## Integration Workflow

### Typical Usage Scenario

1. **Log Analysis**: Service generates logs, they are indexed to Elasticsearch
2. **Anomaly Detection**: Log Analysis Agent detects anomalies and generates fault report
3. **Alert Generation**: Monitoring Agent detects metric anomalies
4. **Automatic Ticket Creation**: Ticket System Agent automatically creates Jira tickets
5. **AI Recommendations**: System provides recommendations based on historical data
6. **Resolution Tracking**: Tickets are tracked and resolution times are recorded

### Example Complete Workflow

```python
# 1. Analyze logs
log_agent = LogAnalysisAgent()
log_result = log_agent.analyze_logs("my-service", requirement_id=123)

if log_result['anomaly_detected']:
    # 2. Create log analysis record
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
    
    # 3. Automatically create Jira ticket
    ticket_agent = TicketSystemAgent()
    ticket_result = ticket_agent.create_ticket_from_fault(
        requirement_id=123,
        service_name="my-service",
        fault_data=log_result,
        source_type='log_analysis',
        source_id=log_record.id
    )
    
    print(f"Ticket created: {ticket_result['ticket_key']}")
    print(f"AI Recommendations: {ticket_result['recommendations']}")
```

## Database Schema

### LogAnalysisRecord
- `id`: Primary key
- `requirement_id`: Associated requirement
- `service_name`: Service name
- `log_source`: Source of logs
- `anomaly_detected`: Boolean
- `anomaly_patterns`: JSON array of patterns
- `fault_report`: Generated report
- `severity`: low/medium/high/critical
- `analyzed_log_count`: Number of logs analyzed
- `analysis_duration`: Time taken for analysis
- `created_at`, `updated_at`: Timestamps

### MonitoringAlert
- `id`: Primary key
- `requirement_id`: Associated requirement
- `service_name`: Service name
- `alert_name`, `alert_type`: Alert identifiers
- `metric_name`: Metric being monitored
- `current_value`, `threshold_value`: Metric values
- `anomaly_detected`: Boolean
- `anomaly_description`: Description
- `severity`: info/warning/critical
- `recommended_solutions`: JSON array of solutions
- `auto_resolved`: Boolean
- `source_type`, `source_url`: Source information
- `created_at`, `updated_at`, `resolved_at`: Timestamps

### TicketRecord
- `id`: Primary key
- `requirement_id`: Associated requirement
- `service_name`: Service name
- `ticket_key`: Jira ticket key
- `ticket_url`: Jira ticket URL
- `ticket_title`, `ticket_description`: Ticket content
- `ticket_type`: bug/task/story
- `priority`: low/medium/high/critical
- `status`: open/in_progress/resolved/closed
- `source_type`, `source_id`: Source information
- `fault_summary`: Summary of the fault
- `recommended_solutions`: JSON array of solutions
- `similar_tickets`: JSON array of similar tickets
- `auto_assigned_to`: Assigned user
- `resolution_time`: Time to resolve in hours
- `created_at`, `updated_at`, `resolved_at`: Timestamps

## Security Considerations

1. **Elasticsearch**: Use authentication and SSL/TLS for production
2. **Prometheus/Grafana**: Secure API endpoints with proper authentication
3. **Jira**: Use API tokens instead of passwords
4. **Sensitive Data**: Ensure logs don't contain sensitive information before indexing

## Best Practices

1. **Log Indexing**: Index logs regularly but avoid overwhelming Elasticsearch
2. **Metric Monitoring**: Set appropriate thresholds for your services
3. **Ticket Creation**: Review automatically created tickets periodically
4. **Historical Data**: Keep historical tickets for better AI recommendations
5. **False Positives**: Review and adjust anomaly detection thresholds

## Troubleshooting

### Elasticsearch Connection Issues
- Verify `ELASTICSEARCH_HOST` and `ELASTICSEARCH_PORT` are correct
- Check network connectivity
- Verify authentication credentials

### Prometheus/Grafana Connection Issues
- Ensure services are running and accessible
- Verify API URLs and tokens
- Check firewall rules

### Jira Integration Issues
- Verify JIRA_URL is correct (include https://)
- Check API token has proper permissions
- Ensure project key exists

## Future Enhancements

1. Machine learning for better anomaly detection
2. Integration with more monitoring tools (Datadog, New Relic, etc.)
3. Support for more ticketing systems (ServiceNow, Zendesk, etc.)
4. Advanced pattern recognition using embeddings
5. Automated remediation actions
6. Integration with ChatOps platforms (Slack, Teams, etc.)

## Support

For issues and questions:
- GitHub Issues: https://github.com/kuafuai/DevOpsGPT/issues
- Email: service@kuafuai.net
- Discord: https://discord.gg/4RMUCZwnxF
