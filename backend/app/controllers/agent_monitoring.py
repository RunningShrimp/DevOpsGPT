"""
Monitoring Alert Agent API Controller
"""
import json
from flask import request, Blueprint
from app.pkgs.tools import storage
from app.controllers.common import json_response
from app.pkgs.agents.monitoring_alert_agent import MonitoringAlertAgent
from app.models.monitoring_alert import MonitoringAlert
from app.models.requirement import Requirement
from app.pkgs.tools.i18b import getI18n

bp = Blueprint('agent_monitoring', __name__, url_prefix='/agent/monitoring')


@bp.route('/check_metrics', methods=['POST'])
@json_response
def check_metrics():
    """检查服务指标并检测异常"""
    _ = getI18n("controllers")
    
    service_name = request.json.get('service_name')
    requirement_id = request.json.get('requirement_id')
    
    if not service_name:
        raise Exception(_("Service name is required"))
    
    tenant_id = storage.get("tenant_id")
    if requirement_id:
        req = Requirement.get_requirement_by_id(requirement_id, tenant_id)
        if not req:
            raise Exception(_("Requirement not found"))
    
    # Check metrics
    agent = MonitoringAlertAgent()
    results = agent.check_service_metrics(service_name, requirement_id)
    
    # Save alerts to database
    alert_ids = []
    for alert in results.get('alerts', []):
        alert_record = MonitoringAlert.create_alert(
            requirement_id=requirement_id or 0,
            service_name=service_name,
            alert_name=f"{alert['metric_name']}_threshold",
            alert_type=alert['metric_name'],
            metric_name=alert['metric_name'],
            current_value=alert['current_value'],
            threshold_value=alert['threshold'],
            anomaly_detected=True,
            anomaly_description=alert['description'],
            severity=alert['severity'],
            source_type='prometheus'
        )
        alert_ids.append(alert_record.id)
    
    return {
        'success': True,
        'results': results,
        'alert_ids': alert_ids
    }


@bp.route('/analyze_alert', methods=['POST'])
@json_response
def analyze_alert():
    """分析告警并获取AI推荐"""
    _ = getI18n("controllers")
    
    alert_id = request.json.get('alert_id')
    
    if not alert_id:
        raise Exception(_("Alert ID is required"))
    
    # Get alert from database
    alert_data = MonitoringAlert.query.get(alert_id)
    if not alert_data:
        raise Exception(_("Alert not found"))
    
    # Convert to dict
    alert_dict = alert_data.to_dict()
    
    # Analyze alert
    agent = MonitoringAlertAgent()
    analysis = agent.analyze_alert(alert_dict)
    
    # Update alert with recommendations
    if analysis.get('success'):
        alert_data.recommended_solutions = json.dumps(analysis.get('recommended_solutions', []))
        from app.extensions import db
        db.session.commit()
    
    return {
        'success': True,
        'analysis': analysis
    }


@bp.route('/alerts', methods=['GET'])
@json_response
def get_alerts():
    """获取活动告警"""
    requirement_id = request.args.get('requirement_id', type=int)
    limit = request.args.get('limit', 20, type=int)
    
    if not requirement_id:
        return {'success': True, 'alerts': []}
    
    tenant_id = storage.get("tenant_id")
    req = Requirement.get_requirement_by_id(requirement_id, tenant_id)
    if not req:
        raise Exception("Requirement not found")
    
    alerts = MonitoringAlert.get_active_alerts(requirement_id, limit)
    
    return {
        'success': True,
        'alerts': alerts
    }


@bp.route('/alerts/service', methods=['GET'])
@json_response
def get_service_alerts():
    """获取特定服务的告警"""
    requirement_id = request.args.get('requirement_id', type=int)
    service_name = request.args.get('service_name')
    limit = request.args.get('limit', 10, type=int)
    
    if not requirement_id or not service_name:
        raise Exception("requirement_id and service_name are required")
    
    tenant_id = storage.get("tenant_id")
    req = Requirement.get_requirement_by_id(requirement_id, tenant_id)
    if not req:
        raise Exception("Requirement not found")
    
    alerts = MonitoringAlert.get_alerts_by_service(requirement_id, service_name, limit)
    
    return {
        'success': True,
        'alerts': alerts
    }


@bp.route('/alerts/resolve', methods=['POST'])
@json_response
def resolve_alert():
    """将告警标记为已解决"""
    _ = getI18n("controllers")
    
    alert_id = request.json.get('alert_id')
    
    if not alert_id:
        raise Exception(_("Alert ID is required"))
    
    success = MonitoringAlert.resolve_alert(alert_id)
    
    if not success:
        raise Exception(_("Failed to resolve alert"))
    
    return {
        'success': True,
        'message': 'Alert resolved successfully'
    }


@bp.route('/prometheus/alerts', methods=['GET'])
@json_response
def get_prometheus_alerts():
    """从Prometheus获取告警"""
    agent = MonitoringAlertAgent()
    success, alerts = agent.get_prometheus_alerts()
    
    return {
        'success': success,
        'alerts': alerts
    }


@bp.route('/grafana/alerts', methods=['GET'])
@json_response
def get_grafana_alerts():
    """从Grafana获取告警"""
    agent = MonitoringAlertAgent()
    success, alerts = agent.get_grafana_alerts()
    
    return {
        'success': success,
        'alerts': alerts
    }
