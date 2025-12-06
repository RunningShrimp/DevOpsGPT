from app.extensions import db
import json


class LogAnalysisRecord(db.Model):
    """日志分析记录存储模型"""
    id = db.Column(db.Integer, primary_key=True)
    requirement_id = db.Column(db.Integer, nullable=False)
    service_name = db.Column(db.String(200))
    log_source = db.Column(db.String(500))  # 日志来源（文件路径、elasticsearch索引等）
    
    # 分析结果
    anomaly_detected = db.Column(db.Boolean, default=False)
    anomaly_patterns = db.Column(db.Text)  # 检测到的异常模式JSON数组
    fault_report = db.Column(db.Text)  # 生成的故障报告
    severity = db.Column(db.String(50))  # 严重性：低、中、高、严重
    
    # 元数据
    analyzed_log_count = db.Column(db.Integer, default=0)
    analysis_duration = db.Column(db.Float)  # 分析耗时（秒）
    
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    @staticmethod
    def create_record(requirement_id, service_name, log_source, anomaly_detected=False, 
                     anomaly_patterns=None, fault_report=None, severity='low',
                     analyzed_log_count=0, analysis_duration=0.0):
        """创建新的日志分析记录"""
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
        """根据需求ID获取日志分析记录"""
        records = LogAnalysisRecord.query.filter_by(requirement_id=requirement_id)\
            .order_by(LogAnalysisRecord.created_at.desc())\
            .limit(limit).all()
        return [record.to_dict() for record in records]

    @staticmethod
    def get_latest_record(requirement_id, service_name):
        """获取服务的最新日志分析记录"""
        record = LogAnalysisRecord.query.filter_by(
            requirement_id=requirement_id,
            service_name=service_name
        ).order_by(LogAnalysisRecord.created_at.desc()).first()
        return record.to_dict() if record else None

    def to_dict(self):
        """将记录转换为字典"""
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
