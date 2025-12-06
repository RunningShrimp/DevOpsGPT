from app.extensions import db
import json


class LogAnalysisRecord(db.Model):
    """Model for storing log analysis records"""
    id = db.Column(db.Integer, primary_key=True)
    requirement_id = db.Column(db.Integer, nullable=False)
    service_name = db.Column(db.String(200))
    log_source = db.Column(db.String(500))  # Source of the logs (file path, elasticsearch index, etc.)
    
    # Analysis results
    anomaly_detected = db.Column(db.Boolean, default=False)
    anomaly_patterns = db.Column(db.Text)  # JSON array of detected patterns
    fault_report = db.Column(db.Text)  # Generated fault report
    severity = db.Column(db.String(50))  # low, medium, high, critical
    
    # Metadata
    analyzed_log_count = db.Column(db.Integer, default=0)
    analysis_duration = db.Column(db.Float)  # in seconds
    
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    @staticmethod
    def create_record(requirement_id, service_name, log_source, anomaly_detected=False, 
                     anomaly_patterns=None, fault_report=None, severity='low',
                     analyzed_log_count=0, analysis_duration=0.0):
        """Create a new log analysis record"""
        patterns_json = json.dumps(anomaly_patterns) if anomaly_patterns else None
        
        record = LogAnalysisRecord(
            requirement_id=requirement_id,
            service_name=service_name,
            log_source=log_source,
            anomaly_detected=anomaly_detected,
            anomaly_patterns=patterns_json,
            fault_report=fault_report,
            severity=severity,
            analyzed_log_count=analyzed_log_count,
            analysis_duration=analysis_duration
        )
        db.session.add(record)
        db.session.commit()
        return record

    @staticmethod
    def get_records_by_requirement(requirement_id, limit=10):
        """Get log analysis records by requirement ID"""
        records = LogAnalysisRecord.query.filter_by(requirement_id=requirement_id)\
            .order_by(LogAnalysisRecord.created_at.desc())\
            .limit(limit).all()
        return [record.to_dict() for record in records]

    @staticmethod
    def get_latest_record(requirement_id, service_name):
        """Get the latest log analysis record for a service"""
        record = LogAnalysisRecord.query.filter_by(
            requirement_id=requirement_id,
            service_name=service_name
        ).order_by(LogAnalysisRecord.created_at.desc()).first()
        return record.to_dict() if record else None

    def to_dict(self):
        """Convert record to dictionary"""
        return {
            'id': self.id,
            'requirement_id': self.requirement_id,
            'service_name': self.service_name,
            'log_source': self.log_source,
            'anomaly_detected': self.anomaly_detected,
            'anomaly_patterns': json.loads(self.anomaly_patterns) if self.anomaly_patterns else [],
            'fault_report': self.fault_report,
            'severity': self.severity,
            'analyzed_log_count': self.analyzed_log_count,
            'analysis_duration': self.analysis_duration,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
