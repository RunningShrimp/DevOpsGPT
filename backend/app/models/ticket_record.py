from app.extensions import db
import json


class TicketRecord(db.Model):
    """Model for storing intelligent ticket system records"""
    id = db.Column(db.Integer, primary_key=True)
    requirement_id = db.Column(db.Integer, nullable=False)
    service_name = db.Column(db.String(200))
    
    # Ticket information
    ticket_key = db.Column(db.String(100))  # Jira ticket key (e.g., DEVOPS-123)
    ticket_url = db.Column(db.String(500))
    ticket_title = db.Column(db.String(500))
    ticket_description = db.Column(db.Text)
    ticket_type = db.Column(db.String(50))  # bug, task, story, etc.
    priority = db.Column(db.String(50))  # low, medium, high, critical
    status = db.Column(db.String(50))  # open, in_progress, resolved, closed
    
    # Source information
    source_type = db.Column(db.String(100))  # log_analysis, monitoring_alert, manual
    source_id = db.Column(db.Integer)  # ID of the source record (log_analysis_id or alert_id)
    fault_summary = db.Column(db.Text)  # Summary of the fault that triggered ticket creation
    
    # AI recommendations
    recommended_solutions = db.Column(db.Text)  # JSON array of solutions based on historical data
    similar_tickets = db.Column(db.Text)  # JSON array of similar historical tickets
    auto_assigned_to = db.Column(db.String(200))  # Auto-assigned user
    
    # Tracking
    resolution_time = db.Column(db.Float)  # Time to resolve in hours
    
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    resolved_at = db.Column(db.TIMESTAMP)

    @staticmethod
    def create_ticket(requirement_id, service_name, ticket_key, ticket_url, ticket_title,
                     ticket_description, ticket_type='bug', priority='medium', status='open',
                     source_type='manual', source_id=None, fault_summary=None,
                     recommended_solutions=None, similar_tickets=None, auto_assigned_to=None):
        """Create a new ticket record"""
        solutions_json = json.dumps(recommended_solutions) if recommended_solutions else None
        similar_json = json.dumps(similar_tickets) if similar_tickets else None
        
        ticket = TicketRecord(
            requirement_id=requirement_id,
            service_name=service_name,
            ticket_key=ticket_key,
            ticket_url=ticket_url,
            ticket_title=ticket_title,
            ticket_description=ticket_description,
            ticket_type=ticket_type,
            priority=priority,
            status=status,
            source_type=source_type,
            source_id=source_id,
            fault_summary=fault_summary,
            recommended_solutions=solutions_json,
            similar_tickets=similar_json,
            auto_assigned_to=auto_assigned_to
        )
        db.session.add(ticket)
        db.session.commit()
        return ticket

    @staticmethod
    def get_tickets_by_requirement(requirement_id, status=None, limit=20):
        """Get tickets by requirement ID, optionally filtered by status"""
        query = TicketRecord.query.filter_by(requirement_id=requirement_id)
        if status:
            query = query.filter_by(status=status)
        tickets = query.order_by(TicketRecord.created_at.desc()).limit(limit).all()
        return [ticket.to_dict() for ticket in tickets]

    @staticmethod
    def get_ticket_by_key(ticket_key):
        """Get ticket by Jira ticket key"""
        ticket = TicketRecord.query.filter_by(ticket_key=ticket_key).first()
        return ticket.to_dict() if ticket else None

    @staticmethod
    def update_ticket_status(ticket_id, status, resolved_at=None):
        """Update ticket status"""
        ticket = TicketRecord.query.get(ticket_id)
        if ticket:
            ticket.status = status
            if resolved_at:
                ticket.resolved_at = resolved_at
                if ticket.created_at:
                    # Calculate resolution time in hours
                    time_diff = resolved_at - ticket.created_at
                    ticket.resolution_time = time_diff.total_seconds() / 3600.0
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_historical_tickets(service_name=None, limit=50):
        """Get historical tickets for pattern analysis"""
        query = TicketRecord.query.filter(TicketRecord.status.in_(['resolved', 'closed']))
        if service_name:
            query = query.filter_by(service_name=service_name)
        tickets = query.order_by(TicketRecord.resolved_at.desc()).limit(limit).all()
        return [ticket.to_dict() for ticket in tickets]

    def to_dict(self):
        """Convert ticket to dictionary"""
        return {
            'id': self.id,
            'requirement_id': self.requirement_id,
            'service_name': self.service_name,
            'ticket_key': self.ticket_key,
            'ticket_url': self.ticket_url,
            'ticket_title': self.ticket_title,
            'ticket_description': self.ticket_description,
            'ticket_type': self.ticket_type,
            'priority': self.priority,
            'status': self.status,
            'source_type': self.source_type,
            'source_id': self.source_id,
            'fault_summary': self.fault_summary,
            'recommended_solutions': json.loads(self.recommended_solutions) if self.recommended_solutions else [],
            'similar_tickets': json.loads(self.similar_tickets) if self.similar_tickets else [],
            'auto_assigned_to': self.auto_assigned_to,
            'resolution_time': self.resolution_time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }
