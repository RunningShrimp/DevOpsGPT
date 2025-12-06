"""
AI-powered monitoring alert analysis and solution recommendation
"""
from app.pkgs.agents.monitoring_service import PrometheusService, GrafanaService
from app.pkgs.tools.llm import llm
import json


class MonitoringAlertAgent:
    """Agent for analyzing monitoring alerts and recommending solutions"""
    
    def __init__(self):
        self.prometheus = PrometheusService()
        self.grafana = GrafanaService()
    
    def check_service_metrics(self, service_name, requirement_id=None):
        """
        Check common metrics for a service
        
        Args:
            service_name: Name of the service
            requirement_id: Optional requirement ID
        
        Returns:
            dict: Metrics check results
        """
        results = {
            'service_name': service_name,
            'requirement_id': requirement_id,
            'alerts': [],
            'metrics': {}
        }
        
        # Define common metrics to check
        metrics_to_check = [
            {
                'name': 'cpu_usage',
                'query': f'rate(container_cpu_usage_seconds_total{{name=~".*{service_name}.*"}}[5m])',
                'threshold': 0.8,
                'comparison': 'gt',
                'description': 'CPU usage rate'
            },
            {
                'name': 'memory_usage',
                'query': f'container_memory_usage_bytes{{name=~".*{service_name}.*"}} / container_spec_memory_limit_bytes{{name=~".*{service_name}.*"}}',
                'threshold': 0.85,
                'comparison': 'gt',
                'description': 'Memory usage percentage'
            },
            {
                'name': 'error_rate',
                'query': f'rate(http_requests_total{{service="{service_name}",status=~"5.."}}[5m])',
                'threshold': 0.01,
                'comparison': 'gt',
                'description': 'HTTP 5xx error rate'
            }
        ]
        
        for metric in metrics_to_check:
            anomaly_result = self.prometheus.check_metric_anomaly(
                metric['query'],
                metric['threshold'],
                metric['comparison']
            )
            
            results['metrics'][metric['name']] = anomaly_result
            
            if anomaly_result.get('anomaly_detected'):
                alert = {
                    'metric_name': metric['name'],
                    'description': metric['description'],
                    'current_value': anomaly_result.get('current_value'),
                    'threshold': metric['threshold'],
                    'severity': self._determine_alert_severity(metric['name'], anomaly_result)
                }
                results['alerts'].append(alert)
        
        return results
    
    def analyze_alert(self, alert_data):
        """
        Analyze an alert and recommend solutions using AI
        
        Args:
            alert_data: Alert data dictionary
        
        Returns:
            dict: Analysis and recommendations
        """
        alert_name = alert_data.get('alert_name', 'Unknown')
        metric_name = alert_data.get('metric_name', 'Unknown')
        current_value = alert_data.get('current_value', 0)
        threshold = alert_data.get('threshold_value', 0)
        
        prompt = f"""Analyze this monitoring alert and recommend solutions:

Alert: {alert_name}
Metric: {metric_name}
Current Value: {current_value}
Threshold: {threshold}

Provide:
1. Root cause analysis
2. Immediate actions to take
3. Long-term preventive measures
4. Priority level (low, medium, high, critical)

Be concise and actionable."""
        
        try:
            response = llm(prompt)
            
            # Extract priority from response (simple heuristic)
            priority = 'medium'
            if 'critical' in response.lower():
                priority = 'critical'
            elif 'high' in response.lower():
                priority = 'high'
            elif 'low' in response.lower():
                priority = 'low'
            
            return {
                'success': True,
                'analysis': response,
                'recommended_priority': priority,
                'recommended_solutions': self._extract_solutions(response)
            }
        except Exception as e:
            print(f"Error analyzing alert with AI: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'analysis': self._generate_template_solution(alert_data)
            }
    
    def _determine_alert_severity(self, metric_name, anomaly_result):
        """
        Determine alert severity based on metric and value
        
        Args:
            metric_name: Name of the metric
            anomaly_result: Anomaly detection result
        
        Returns:
            str: Severity level
        """
        current_value = anomaly_result.get('current_value', 0)
        threshold = anomaly_result.get('threshold', 0)
        
        # Calculate how much the value exceeds the threshold
        if threshold > 0:
            ratio = current_value / threshold
        else:
            ratio = 1.0
        
        if metric_name in ['cpu_usage', 'memory_usage']:
            if ratio > 1.5:
                return 'critical'
            elif ratio > 1.2:
                return 'high'
            else:
                return 'warning'
        elif metric_name == 'error_rate':
            if ratio > 5.0:
                return 'critical'
            elif ratio > 2.0:
                return 'high'
            else:
                return 'warning'
        
        return 'info'
    
    def _extract_solutions(self, analysis_text):
        """
        Extract action items from AI analysis
        
        Args:
            analysis_text: AI-generated analysis text
        
        Returns:
            list: List of solution steps
        """
        solutions = []
        
        # Simple extraction - look for numbered lists or bullet points
        lines = analysis_text.split('\n')
        for line in lines:
            line = line.strip()
            # Look for numbered items or bullet points
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                solutions.append(line)
        
        return solutions if solutions else [analysis_text]
    
    def _generate_template_solution(self, alert_data):
        """
        Generate template-based solution as fallback
        
        Args:
            alert_data: Alert data dictionary
        
        Returns:
            str: Template solution
        """
        metric_name = alert_data.get('metric_name', 'Unknown')
        
        solutions = {
            'cpu_usage': """
## High CPU Usage Detected

### Immediate Actions:
1. Check for runaway processes
2. Review recent deployments
3. Scale horizontally if possible

### Long-term Measures:
1. Optimize application code
2. Implement better caching
3. Review resource allocation
            """,
            'memory_usage': """
## High Memory Usage Detected

### Immediate Actions:
1. Check for memory leaks
2. Restart service if necessary
3. Scale vertically if possible

### Long-term Measures:
1. Profile memory usage
2. Optimize data structures
3. Implement proper garbage collection
            """,
            'error_rate': """
## High Error Rate Detected

### Immediate Actions:
1. Check application logs
2. Review recent changes
3. Rollback if necessary

### Long-term Measures:
1. Improve error handling
2. Add better monitoring
3. Implement circuit breakers
            """
        }
        
        return solutions.get(metric_name, "No specific solution template available for this metric.")
    
    def get_prometheus_alerts(self):
        """
        Get all active alerts from Prometheus
        
        Returns:
            tuple: (success, alerts_list)
        """
        return self.prometheus.get_alerts()
    
    def get_grafana_alerts(self):
        """
        Get all active alerts from Grafana
        
        Returns:
            tuple: (success, alerts_list)
        """
        return self.grafana.get_alerts()
