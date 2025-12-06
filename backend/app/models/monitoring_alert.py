from app.extensions import db
import json


class MonitoringAlert(db.Model):
    """Model for storing monitoring alerts and metric anomalies"""
    id = db.Column(db.Integer, primary_key=True)
    requirement_id = db.Column(db.Integer, nullable=False)
    service_name = db.Column(db.String(200))
    
    # Alert information
    alert_name = db.Column(db.String(200))
    alert_type = db.Column(db.String(100))  # cpu, memory, disk, network, custom
    metric_name = db.Column(db.String(200))
    current_value = db.Column(db.Float)
    threshold_value = db.Column(db.Float)
    
    # Analysis results
    anomaly_detected = db.Column(db.Boolean, default=False)
    anomaly_description = db.Column(db.Text)
    severity = db.Column(db.String(50))  # info, warning, critical
    
    # AI-generated solution recommendations
    recommended_solutions = db.Column(db.Text)  # JSON array of solutions
    auto_resolved = db.Column(db.Boolean, default=False)
    
    # Source information
    source_type = db.Column(db.String(100))  # prometheus, grafana, custom
    source_url = db.Column(db.String(500))
    
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    resolved_at = db.Column(db.TIMESTAMP)

    @staticmethod
    def create_alert(requirement_id, service_name, alert_name, alert_type, metric_name,
                    current_value, threshold_value, anomaly_detected=False,
                    anomaly_description=None, severity='info', recommended_solutions=None,
                    source_type='prometheus', source_url=None):
        """Create a new monitoring alert"""
        solutions_json = json.dumps(recommended_solutions) if recommended_solutions else None
        
        alert = MonitoringAlert(
            requirement_id=requirement_id,
            service_name=service_name,
            alert_name=alert_name,
            alert_type=alert_type,
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=threshold_value,
            anomaly_detected=anomaly_detected,
            anomaly_description=anomaly_description,
            severity=severity,
            recommended_solutions=solutions_json,
            source_type=source_type,
            source_url=source_url
        )
        db.session.add(alert)
        db.session.commit()
        return alert

    @staticmethod
    def get_active_alerts(requirement_id, limit=20):
        """Get active (unresolved) alerts by requirement ID"""
        alerts = MonitoringAlert.query.filter_by(
            requirement_id=requirement_id,
            auto_resolved=False
        ).order_by(MonitoringAlert.created_at.desc()).limit(limit).all()
        return [alert.to_dict() for alert in alerts]

    @staticmethod
    def get_alerts_by_service(requirement_id, service_name, limit=10):
        """Get alerts for a specific service"""
        alerts = MonitoringAlert.query.filter_by(
            requirement_id=requirement_id,
            service_name=service_name
        ).order_by(MonitoringAlert.created_at.desc()).limit(limit).all()
        return [alert.to_dict() for alert in alerts]

    @staticmethod
    def resolve_alert(alert_id):
        """Mark an alert as resolved"""
        alert = MonitoringAlert.query.get(alert_id)
        if alert:
            alert.auto_resolved = True
            alert.resolved_at = db.func.current_timestamp()
            db.session.commit()
            return True
        return False

    def to_dict(self):
        """Convert alert to dictionary"""
        return {
            'id': self.id,
            'requirement_id': self.requirement_id,
            'service_name': self.service_name,
            'alert_name': self.alert_name,
            'alert_type': self.alert_type,
            'metric_name': self.metric_name,
            'current_value': self.current_value,
            'threshold_value': self.threshold_value,
            'anomaly_detected': self.anomaly_detected,
            'anomaly_description': self.anomaly_description,
            'severity': self.severity,
            'recommended_solutions': json.loads(self.recommended_solutions) if self.recommended_solutions else [],
            'auto_resolved': self.auto_resolved,
            'source_type': self.source_type,
            'source_url': self.source_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }
