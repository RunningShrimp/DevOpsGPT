from app.extensions import db
import json


class MonitoringAlert(db.Model):
    """监控告警和指标异常存储模型"""
    id = db.Column(db.Integer, primary_key=True)
    requirement_id = db.Column(db.Integer, nullable=False)
    service_name = db.Column(db.String(200))
    
    # 告警信息
    alert_name = db.Column(db.String(200))
    alert_type = db.Column(db.String(100))  # cpu、memory、disk、network、custom
    metric_name = db.Column(db.String(200))
    current_value = db.Column(db.Float)
    threshold_value = db.Column(db.Float)
    
    # 分析结果
    anomaly_detected = db.Column(db.Boolean, default=False)
    anomaly_description = db.Column(db.Text)
    severity = db.Column(db.String(50))  # info、warning、critical
    
    # AI生成的解决方案推荐
    recommended_solutions = db.Column(db.Text)  # 解决方案JSON数组
    auto_resolved = db.Column(db.Boolean, default=False)
    
    # 来源信息
    source_type = db.Column(db.String(100))  # prometheus、grafana、custom
    source_url = db.Column(db.String(500))
    
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    resolved_at = db.Column(db.TIMESTAMP)

    @staticmethod
    def create_alert(requirement_id, service_name, alert_name, alert_type, metric_name,
                    current_value, threshold_value, anomaly_detected=False,
                    anomaly_description=None, severity='info', recommended_solutions=None,
                    source_type='prometheus', source_url=None):
        """创建新的监控告警"""
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
        """根据需求ID获取活动（未解决）的告警"""
        alerts = MonitoringAlert.query.filter_by(
            requirement_id=requirement_id,
            auto_resolved=False
        ).order_by(MonitoringAlert.created_at.desc()).limit(limit).all()
        return [alert.to_dict() for alert in alerts]

    @staticmethod
    def get_alerts_by_service(requirement_id, service_name, limit=10):
        """获取特定服务的告警"""
        alerts = MonitoringAlert.query.filter_by(
            requirement_id=requirement_id,
            service_name=service_name
        ).order_by(MonitoringAlert.created_at.desc()).limit(limit).all()
        return [alert.to_dict() for alert in alerts]

    @staticmethod
    def resolve_alert(alert_id):
        """将告警标记为已解决"""
        alert = MonitoringAlert.query.get(alert_id)
        if alert:
            alert.auto_resolved = True
            alert.resolved_at = db.func.current_timestamp()
            db.session.commit()
            return True
        return False

    def to_dict(self):
        """将告警转换为字典"""
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
