"""
日志分析Agent API控制器
"""
from flask import request, Blueprint
from app.pkgs.tools import storage
from app.controllers.common import json_response
from app.pkgs.agents.log_analysis_agent import LogAnalysisAgent
from app.pkgs.agents.elasticsearch_service import ElasticsearchService
from app.models.log_analysis_record import LogAnalysisRecord
from app.models.requirement import Requirement
from app.pkgs.tools.i18b import getI18n
import time

bp = Blueprint('agent_log_analysis', __name__, url_prefix='/agent/log_analysis')


@bp.route('/analyze', methods=['POST'])
@json_response
def analyze_logs():
    """分析服务日志"""
    _ = getI18n("controllers")
    
    service_name = request.json.get('service_name')
    requirement_id = request.json.get('requirement_id')
    time_range_hours = request.json.get('time_range_hours', 24)
    
    if not service_name:
        raise Exception(_("Service name is required"))
    
    tenant_id = storage.get("tenant_id")
    if requirement_id:
        req = Requirement.get_requirement_by_id(requirement_id, tenant_id)
        if not req:
            raise Exception(_("Requirement not found"))
    
    # 执行日志分析
    agent = LogAnalysisAgent()
    start_time = time.time()
    
    analysis_result = agent.analyze_logs(
        service_name=service_name,
        requirement_id=requirement_id,
        time_range_hours=time_range_hours
    )
    
    analysis_duration = time.time() - start_time
    
    # 保存分析记录
    record = LogAnalysisRecord.create_record(
        requirement_id=requirement_id or 0,
        service_name=service_name,
        log_source='elasticsearch',
        anomaly_detected=analysis_result.get('anomaly_detected', False),
        anomaly_patterns=analysis_result.get('patterns', []),
        fault_report=analysis_result.get('fault_report', ''),
        severity=analysis_result.get('severity', 'low'),
        analyzed_log_count=analysis_result.get('error_count', 0),
        analysis_duration=analysis_duration
    )
    
    return {
        'success': True,
        'record_id': record.id,
        'analysis': analysis_result
    }


@bp.route('/records', methods=['GET'])
@json_response
def get_records():
    """获取日志分析记录"""
    requirement_id = request.args.get('requirement_id', type=int)
    limit = request.args.get('limit', 10, type=int)
    
    if not requirement_id:
        return {'success': True, 'records': []}
    
    tenant_id = storage.get("tenant_id")
    req = Requirement.get_requirement_by_id(requirement_id, tenant_id)
    if not req:
        raise Exception("Requirement not found")
    
    records = LogAnalysisRecord.get_records_by_requirement(requirement_id, limit)
    
    return {
        'success': True,
        'records': records
    }


@bp.route('/latest', methods=['GET'])
@json_response
def get_latest_record():
    """获取服务的最新日志分析记录"""
    requirement_id = request.args.get('requirement_id', type=int)
    service_name = request.args.get('service_name')
    
    if not requirement_id or not service_name:
        raise Exception("requirement_id and service_name are required")
    
    tenant_id = storage.get("tenant_id")
    req = Requirement.get_requirement_by_id(requirement_id, tenant_id)
    if not req:
        raise Exception("Requirement not found")
    
    record = LogAnalysisRecord.get_latest_record(requirement_id, service_name)
    
    return {
        'success': True,
        'record': record
    }


@bp.route('/search_logs', methods=['POST'])
@json_response
def search_logs():
    """在Elasticsearch中搜索日志"""
    _ = getI18n("controllers")
    
    service_name = request.json.get('service_name')
    query = request.json.get('query')
    time_range_hours = request.json.get('time_range_hours', 24)
    size = request.json.get('size', 100)
    
    if not service_name:
        raise Exception(_("Service name is required"))
    
    es_service = ElasticsearchService()
    
    if not es_service.is_available():
        raise Exception(_("Elasticsearch is not enabled or not available"))
    
    logs, total = es_service.search_logs(service_name, query, time_range_hours, size)
    
    return {
        'success': True,
        'logs': logs,
        'total': total
    }


@bp.route('/index_logs', methods=['POST'])
@json_response
def index_logs():
    """将日志索引到Elasticsearch"""
    _ = getI18n("controllers")
    
    service_name = request.json.get('service_name')
    logs = request.json.get('logs', [])
    requirement_id = request.json.get('requirement_id')
    
    if not service_name:
        raise Exception(_("Service name is required"))
    
    if not logs:
        raise Exception(_("Logs array is required"))
    
    es_service = ElasticsearchService()
    
    if not es_service.is_available():
        raise Exception(_("Elasticsearch is not enabled or not available"))
    
    success, message = es_service.index_logs(service_name, logs, requirement_id)
    
    if not success:
        raise Exception(message)
    
    return {
        'success': True,
        'message': message
    }


@bp.route('/analyze_entry', methods=['POST'])
@json_response
def analyze_log_entry():
    """使用AI分析特定日志条目"""
    _ = getI18n("controllers")
    
    log_entry = request.json.get('log_entry')
    
    if not log_entry:
        raise Exception(_("Log entry is required"))
    
    agent = LogAnalysisAgent()
    result = agent.analyze_specific_log_entry(log_entry)
    
    return result
