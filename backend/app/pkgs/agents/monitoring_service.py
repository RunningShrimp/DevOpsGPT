"""
Prometheus and Grafana integration for monitoring and alerting
"""
import requests
from config import (PROMETHEUS_ENABLED, PROMETHEUS_URL, GRAFANA_ENABLED, 
                   GRAFANA_URL, GRAFANA_API_KEY)
from datetime import datetime, timedelta


class PrometheusService:
    """与Prometheus交互的服务"""
    
    def __init__(self):
        self.enabled = PROMETHEUS_ENABLED
        self.base_url = PROMETHEUS_URL
    
    def is_available(self):
        """检查Prometheus服务是否可用"""
        if not self.enabled:
            return False
        
        try:
            response = requests.get(f"{self.base_url}/api/v1/status/config", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def query(self, query_string):
        """
        Execute a PromQL query
        
        Args:
            query_string: PromQL查询字符串
        
        Returns:
            tuple: (success, result_data)
        """
        if not self.is_available():
            return False, "Prometheus is not enabled or not available"
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/query",
                params={'query': query_string},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return True, data.get('data', {})
            
            return False, "Query failed"
        except Exception as e:
            return False, f"Error querying Prometheus: {str(e)}"
    
    def query_range(self, query_string, start_time, end_time, step='15s'):
        """
        Execute a PromQL range query
        
        Args:
            query_string: PromQL查询字符串
            start_time: 开始时间 (datetime or timestamp)
            end_time: 结束时间 (datetime or timestamp)
            step: 查询分辨率步长
        
        Returns:
            tuple: (success, result_data)
        """
        if not self.is_available():
            return False, "Prometheus is not enabled or not available"
        
        try:
            if isinstance(start_time, datetime):
                start_time = start_time.timestamp()
            if isinstance(end_time, datetime):
                end_time = end_time.timestamp()
            
            response = requests.get(
                f"{self.base_url}/api/v1/query_range",
                params={
                    'query': query_string,
                    'start': start_time,
                    'end': end_time,
                    'step': step
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return True, data.get('data', {})
            
            return False, "Query failed"
        except Exception as e:
            return False, f"Error querying Prometheus: {str(e)}"
    
    def get_alerts(self):
        """
        Get active alerts from Prometheus
        
        Returns:
            tuple: (成功状态, 告警列表)
        """
        if not self.is_available():
            return False, []
        
        try:
            response = requests.get(f"{self.base_url}/api/v1/alerts", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    alerts = data.get('data', {}).get('alerts', [])
                    return True, alerts
            
            return False, []
        except Exception as e:
            print(f"Error getting Prometheus alerts: {str(e)}")
            return False, []
    
    def check_metric_anomaly(self, metric_name, threshold, comparison='gt'):
        """
        Check if a metric exceeds a threshold
        
        Args:
            metric_name: Prometheus指标名称
            threshold: 阈值
            comparison: 比较运算符 (gt, lt, gte, lte, eq)
        
        Returns:
            dict: 异常检测结果
        """
        success, data = self.query(metric_name)
        
        if not success:
            return {
                'anomaly_detected': False,
                'current_value': None,
                'threshold': threshold,
                'message': 'Failed to query metric'
            }
        
        results = data.get('result', [])
        if not results:
            return {
                'anomaly_detected': False,
                'current_value': None,
                'threshold': threshold,
                'message': 'No data available'
            }
        
        # Get the first result's value
        value = results[0].get('value', [None, None])[1]
        if value is None:
            return {
                'anomaly_detected': False,
                'current_value': None,
                'threshold': threshold,
                'message': 'No value available'
            }
        
        try:
            current_value = float(value)
            anomaly_detected = False
            
            if comparison == 'gt':
                anomaly_detected = current_value > threshold
            elif comparison == 'lt':
                anomaly_detected = current_value < threshold
            elif comparison == 'gte':
                anomaly_detected = current_value >= threshold
            elif comparison == 'lte':
                anomaly_detected = current_value <= threshold
            elif comparison == 'eq':
                anomaly_detected = current_value == threshold
            
            return {
                'anomaly_detected': anomaly_detected,
                'current_value': current_value,
                'threshold': threshold,
                'comparison': comparison,
                'metric_name': metric_name,
                'message': f'Metric value is {current_value}'
            }
        except ValueError:
            return {
                'anomaly_detected': False,
                'current_value': value,
                'threshold': threshold,
                'message': 'Invalid metric value'
            }


class GrafanaService:
    """与Grafana交互的服务"""
    
    def __init__(self):
        self.enabled = GRAFANA_ENABLED
        self.base_url = GRAFANA_URL
        self.api_key = GRAFANA_API_KEY
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def is_available(self):
        """检查Grafana服务是否可用"""
        if not self.enabled or not self.api_key:
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/api/health",
                headers=self.headers,
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_dashboards(self):
        """
        Get list of Grafana dashboards
        
        Returns:
            tuple: (成功状态, 仪表板列表)
        """
        if not self.is_available():
            return False, []
        
        try:
            response = requests.get(
                f"{self.base_url}/api/search?type=dash-db",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            
            return False, []
        except Exception as e:
            print(f"Error getting Grafana dashboards: {str(e)}")
            return False, []
    
    def get_dashboard(self, dashboard_uid):
        """
        Get a specific dashboard by UID
        
        Args:
            dashboard_uid: 仪表板UID
        
        Returns:
            tuple: (成功状态, 仪表板数据)
        """
        if not self.is_available():
            return False, None
        
        try:
            response = requests.get(
                f"{self.base_url}/api/dashboards/uid/{dashboard_uid}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            
            return False, None
        except Exception as e:
            print(f"Error getting Grafana dashboard: {str(e)}")
            return False, None
    
    def get_alerts(self):
        """
        Get active alerts from Grafana
        
        Returns:
            tuple: (成功状态, 告警列表)
        """
        if not self.is_available():
            return False, []
        
        try:
            response = requests.get(
                f"{self.base_url}/api/alerts",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            
            return False, []
        except Exception as e:
            print(f"Error getting Grafana alerts: {str(e)}")
            return False, []
    
    def create_annotation(self, dashboard_id, time, text, tags=None):
        """
        Create an annotation in Grafana
        
        Args:
            dashboard_id: 仪表板ID
            time: 时间戳 (in milliseconds)
            text: 注释文本
            tags: 标签列表
        
        Returns:
            tuple: (成功状态, 注释ID)
        """
        if not self.is_available():
            return False, None
        
        try:
            payload = {
                'dashboardId': dashboard_id,
                'time': time,
                'text': text,
                'tags': tags or []
            }
            
            response = requests.post(
                f"{self.base_url}/api/annotations",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, data.get('id')
            
            return False, None
        except Exception as e:
            print(f"Error creating Grafana annotation: {str(e)}")
            return False, None
