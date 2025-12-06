"""
AI-powered log analysis and fault report generation
"""
from app.pkgs.agents.elasticsearch_service import ElasticsearchService
from app.pkgs.tools.llm import llm
import json


class LogAnalysisAgent:
    """Agent for analyzing logs and generating fault reports"""
    
    def __init__(self):
        self.es_service = ElasticsearchService()
    
    def analyze_logs(self, service_name, requirement_id=None, time_range_hours=24):
        """
        Analyze logs for a service and detect anomalies
        
        Args:
            service_name: Name of the service
            requirement_id: Optional requirement ID
            time_range_hours: Hours to look back
        
        Returns:
            dict: Analysis results
        """
        # Get error patterns from Elasticsearch
        error_analysis = self.es_service.analyze_error_patterns(service_name, time_range_hours)
        log_stats = self.es_service.get_log_statistics(service_name, time_range_hours)
        
        # Determine if anomalies exist
        error_count = error_analysis.get('error_count', 0)
        anomaly_detected = error_count > 10  # Simple threshold
        
        if anomaly_detected:
            severity = self._determine_severity(error_count, log_stats)
            patterns = error_analysis.get('patterns', [])
            fault_report = self._generate_fault_report(service_name, patterns, log_stats)
        else:
            severity = 'low'
            patterns = []
            fault_report = f"No significant anomalies detected in {service_name} logs."
        
        return {
            'service_name': service_name,
            'requirement_id': requirement_id,
            'anomaly_detected': anomaly_detected,
            'patterns': patterns,
            'fault_report': fault_report,
            'severity': severity,
            'error_count': error_count,
            'log_statistics': log_stats,
            'time_range_hours': time_range_hours
        }
    
    def _determine_severity(self, error_count, log_stats):
        """
        Determine severity based on error count and log statistics
        
        Args:
            error_count: Number of errors
            log_stats: Log statistics by level
        
        Returns:
            str: Severity level (low, medium, high, critical)
        """
        critical_count = log_stats.get('CRITICAL', 0) + log_stats.get('FATAL', 0)
        
        if critical_count > 5 or error_count > 100:
            return 'critical'
        elif error_count > 50:
            return 'high'
        elif error_count > 20:
            return 'medium'
        else:
            return 'low'
    
    def _generate_fault_report(self, service_name, patterns, log_stats):
        """
        Generate a fault report using AI
        
        Args:
            service_name: Name of the service
            patterns: List of detected error patterns
            log_stats: Log statistics
        
        Returns:
            str: Generated fault report
        """
        if not patterns:
            return f"Service {service_name} has errors but no specific patterns detected."
        
        # Prepare context for LLM
        context = f"""Service: {service_name}
Log Statistics: {json.dumps(log_stats, indent=2)}

Top Error Patterns:
"""
        for i, pattern in enumerate(patterns[:5], 1):
            context += f"{i}. {pattern.get('message', 'Unknown error')} (occurred {pattern.get('count', 0)} times)\n"
        
        prompt = f"""Analyze the following log data and generate a concise fault report.

{context}

Please provide:
1. Summary of the issue
2. Potential root causes
3. Impact assessment
4. Recommended actions

Keep the report concise and actionable."""
        
        try:
            response = llm(prompt)
            return response
        except Exception as e:
            print(f"Error generating fault report with AI: {str(e)}")
            # Fallback to template-based report
            return self._generate_template_report(service_name, patterns, log_stats)
    
    def _generate_template_report(self, service_name, patterns, log_stats):
        """
        Generate a template-based fault report as fallback
        
        Args:
            service_name: Name of the service
            patterns: List of detected error patterns
            log_stats: Log statistics
        
        Returns:
            str: Generated fault report
        """
        report = f"# Fault Report for {service_name}\n\n"
        report += f"## Summary\n"
        report += f"Multiple errors detected in the service logs.\n\n"
        
        report += f"## Log Statistics\n"
        for level, count in log_stats.items():
            report += f"- {level}: {count}\n"
        
        report += f"\n## Top Error Patterns\n"
        for i, pattern in enumerate(patterns[:5], 1):
            report += f"{i}. {pattern.get('message', 'Unknown error')} (occurred {pattern.get('count', 0)} times)\n"
        
        report += f"\n## Recommended Actions\n"
        report += f"1. Investigate the most frequent errors\n"
        report += f"2. Check service health and resource usage\n"
        report += f"3. Review recent code changes\n"
        report += f"4. Monitor the situation and escalate if needed\n"
        
        return report
    
    def analyze_specific_log_entry(self, log_entry):
        """
        Analyze a specific log entry using AI
        
        Args:
            log_entry: Log entry to analyze
        
        Returns:
            dict: Analysis result
        """
        prompt = f"""Analyze this log entry and provide insights:

Log Entry:
{log_entry}

Provide:
1. What is the issue?
2. Is this a critical error?
3. Possible causes
4. Suggested fix"""
        
        try:
            response = llm(prompt)
            return {
                'success': True,
                'analysis': response
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
