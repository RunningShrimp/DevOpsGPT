"""
Intelligent Ticket System Agent API Controller
"""
from flask import request, Blueprint
from app.pkgs.tools import storage
from app.controllers.common import json_response
from app.pkgs.agents.ticket_system_agent import TicketSystemAgent
from app.models.ticket_record import TicketRecord
from app.models.log_analysis_record import LogAnalysisRecord
from app.models.monitoring_alert import MonitoringAlert
from app.models.requirement import Requirement
from app.pkgs.tools.i18b import getI18n

bp = Blueprint('agent_ticket', __name__, url_prefix='/agent/ticket')


@bp.route('/create_from_log', methods=['POST'])
@json_response
def create_ticket_from_log():
    """Create a Jira ticket from log analysis"""
    _ = getI18n("controllers")
    
    requirement_id = request.json.get('requirement_id')
    log_analysis_id = request.json.get('log_analysis_id')
    
    if not requirement_id or not log_analysis_id:
        raise Exception(_("requirement_id and log_analysis_id are required"))
    
    tenant_id = storage.get("tenant_id")
    req = Requirement.get_requirement_by_id(requirement_id, tenant_id)
    if not req:
        raise Exception(_("Requirement not found"))
    
    # Get log analysis record
    log_record = LogAnalysisRecord.query.get(log_analysis_id)
    if not log_record:
        raise Exception(_("Log analysis record not found"))
    
    # Convert to dict for agent
    fault_data = log_record.to_dict()
    
    # Create ticket
    agent = TicketSystemAgent()
    result = agent.create_ticket_from_fault(
        requirement_id=requirement_id,
        service_name=log_record.service_name,
        fault_data=fault_data,
        source_type='log_analysis',
        source_id=log_analysis_id
    )
    
    return result


@bp.route('/create_from_alert', methods=['POST'])
@json_response
def create_ticket_from_alert():
    """Create a Jira ticket from monitoring alert"""
    _ = getI18n("controllers")
    
    requirement_id = request.json.get('requirement_id')
    alert_id = request.json.get('alert_id')
    
    if not requirement_id or not alert_id:
        raise Exception(_("requirement_id and alert_id are required"))
    
    tenant_id = storage.get("tenant_id")
    req = Requirement.get_requirement_by_id(requirement_id, tenant_id)
    if not req:
        raise Exception(_("Requirement not found"))
    
    # Get alert record
    alert_record = MonitoringAlert.query.get(alert_id)
    if not alert_record:
        raise Exception(_("Alert record not found"))
    
    # Convert to dict for agent
    fault_data = alert_record.to_dict()
    
    # Create ticket
    agent = TicketSystemAgent()
    result = agent.create_ticket_from_fault(
        requirement_id=requirement_id,
        service_name=alert_record.service_name,
        fault_data=fault_data,
        source_type='monitoring_alert',
        source_id=alert_id
    )
    
    return result


@bp.route('/create_manual', methods=['POST'])
@json_response
def create_ticket_manual():
    """Create a Jira ticket manually"""
    _ = getI18n("controllers")
    
    requirement_id = request.json.get('requirement_id')
    service_name = request.json.get('service_name')
    title = request.json.get('title')
    description = request.json.get('description')
    priority = request.json.get('priority', 'Medium')
    
    if not requirement_id or not service_name or not title:
        raise Exception(_("requirement_id, service_name, and title are required"))
    
    tenant_id = storage.get("tenant_id")
    req = Requirement.get_requirement_by_id(requirement_id, tenant_id)
    if not req:
        raise Exception(_("Requirement not found"))
    
    agent = TicketSystemAgent()
    
    # Create ticket directly in Jira
    if agent.jira.is_available():
        success, ticket_key, ticket_url, message = agent.jira.create_ticket(
            summary=title,
            description=description or "Manual ticket creation",
            issue_type='Task',
            priority=priority,
            labels=[service_name, 'manual']
        )
        
        if not success:
            raise Exception(message)
    else:
        ticket_key = f"MOCK-{requirement_id}-MANUAL"
        ticket_url = f"http://localhost/tickets/{ticket_key}"
        message = "Jira not available, created mock ticket"
    
    # Store in database
    ticket_record = TicketRecord.create_ticket(
        requirement_id=requirement_id,
        service_name=service_name,
        ticket_key=ticket_key,
        ticket_url=ticket_url,
        ticket_title=title,
        ticket_description=description or "Manual ticket creation",
        ticket_type='task',
        priority=priority.lower(),
        status='open',
        source_type='manual'
    )
    
    return {
        'success': True,
        'ticket_key': ticket_key,
        'ticket_url': ticket_url,
        'ticket_id': ticket_record.id,
        'message': message
    }


@bp.route('/tickets', methods=['GET'])
@json_response
def get_tickets():
    """Get tickets by requirement"""
    requirement_id = request.args.get('requirement_id', type=int)
    status = request.args.get('status')
    limit = request.args.get('limit', 20, type=int)
    
    if not requirement_id:
        return {'success': True, 'tickets': []}
    
    tenant_id = storage.get("tenant_id")
    req = Requirement.get_requirement_by_id(requirement_id, tenant_id)
    if not req:
        raise Exception("Requirement not found")
    
    tickets = TicketRecord.get_tickets_by_requirement(requirement_id, status, limit)
    
    return {
        'success': True,
        'tickets': tickets
    }


@bp.route('/ticket/<ticket_key>', methods=['GET'])
@json_response
def get_ticket(ticket_key):
    """Get ticket by key"""
    ticket = TicketRecord.get_ticket_by_key(ticket_key)
    
    if not ticket:
        raise Exception("Ticket not found")
    
    return {
        'success': True,
        'ticket': ticket
    }


@bp.route('/ticket/update_status', methods=['POST'])
@json_response
def update_ticket_status():
    """Update ticket status"""
    _ = getI18n("controllers")
    
    ticket_id = request.json.get('ticket_id')
    status = request.json.get('status')
    
    if not ticket_id or not status:
        raise Exception(_("ticket_id and status are required"))
    
    from datetime import datetime
    resolved_at = datetime.now() if status in ['resolved', 'closed'] else None
    
    success = TicketRecord.update_ticket_status(ticket_id, status, resolved_at)
    
    if not success:
        raise Exception(_("Failed to update ticket status"))
    
    return {
        'success': True,
        'message': 'Ticket status updated successfully'
    }


@bp.route('/ticket/sync_from_jira', methods=['POST'])
@json_response
def sync_ticket_from_jira():
    """Sync ticket status from Jira"""
    _ = getI18n("controllers")
    
    ticket_key = request.json.get('ticket_key')
    
    if not ticket_key:
        raise Exception(_("ticket_key is required"))
    
    agent = TicketSystemAgent()
    success, message = agent.update_ticket_from_jira(ticket_key)
    
    return {
        'success': success,
        'message': message
    }


@bp.route('/historical', methods=['GET'])
@json_response
def get_historical_tickets():
    """Get historical tickets for analysis"""
    service_name = request.args.get('service_name')
    limit = request.args.get('limit', 50, type=int)
    
    tickets = TicketRecord.get_historical_tickets(service_name, limit)
    
    return {
        'success': True,
        'tickets': tickets
    }
