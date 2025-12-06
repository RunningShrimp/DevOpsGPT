"""
Test script for DevOpsGPT Agent Modules

This script tests the basic functionality of the new agent modules:
- Log Analysis Agent
- Monitoring Alert Agent  
- Intelligent Ticket System
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from app.pkgs.agents.elasticsearch_service import ElasticsearchService
        print("✓ ElasticsearchService imported successfully")
    except Exception as e:
        print(f"✗ Failed to import ElasticsearchService: {e}")
    
    try:
        from app.pkgs.agents.monitoring_service import PrometheusService, GrafanaService
        print("✓ PrometheusService and GrafanaService imported successfully")
    except Exception as e:
        print(f"✗ Failed to import monitoring services: {e}")
    
    try:
        from app.pkgs.agents.jira_service import JiraService
        print("✓ JiraService imported successfully")
    except Exception as e:
        print(f"✗ Failed to import JiraService: {e}")
    
    try:
        from app.pkgs.agents.log_analysis_agent import LogAnalysisAgent
        print("✓ LogAnalysisAgent imported successfully")
    except Exception as e:
        print(f"✗ Failed to import LogAnalysisAgent: {e}")
    
    try:
        from app.pkgs.agents.monitoring_alert_agent import MonitoringAlertAgent
        print("✓ MonitoringAlertAgent imported successfully")
    except Exception as e:
        print(f"✗ Failed to import MonitoringAlertAgent: {e}")
    
    try:
        from app.pkgs.agents.ticket_system_agent import TicketSystemAgent
        print("✓ TicketSystemAgent imported successfully")
    except Exception as e:
        print(f"✗ Failed to import TicketSystemAgent: {e}")
    
    try:
        from app.models.log_analysis_record import LogAnalysisRecord
        print("✓ LogAnalysisRecord model imported successfully")
    except Exception as e:
        print(f"✗ Failed to import LogAnalysisRecord: {e}")
    
    try:
        from app.models.monitoring_alert import MonitoringAlert
        print("✓ MonitoringAlert model imported successfully")
    except Exception as e:
        print(f"✗ Failed to import MonitoringAlert: {e}")
    
    try:
        from app.models.ticket_record import TicketRecord
        print("✓ TicketRecord model imported successfully")
    except Exception as e:
        print(f"✗ Failed to import TicketRecord: {e}")
    
    try:
        from app.controllers.agent_log_analysis import bp as log_bp
        print("✓ Log analysis controller imported successfully")
    except Exception as e:
        print(f"✗ Failed to import log analysis controller: {e}")
    
    try:
        from app.controllers.agent_monitoring import bp as monitoring_bp
        print("✓ Monitoring controller imported successfully")
    except Exception as e:
        print(f"✗ Failed to import monitoring controller: {e}")
    
    try:
        from app.controllers.agent_ticket import bp as ticket_bp
        print("✓ Ticket controller imported successfully")
    except Exception as e:
        print(f"✗ Failed to import ticket controller: {e}")
    
    print("\nImport tests completed!")

def test_service_initialization():
    """Test that services can be initialized (without actual connections)"""
    print("\nTesting service initialization...")
    
    try:
        from app.pkgs.agents.elasticsearch_service import ElasticsearchService
        es = ElasticsearchService()
        print(f"✓ ElasticsearchService initialized (enabled: {es.enabled})")
    except Exception as e:
        print(f"✗ Failed to initialize ElasticsearchService: {e}")
    
    try:
        from app.pkgs.agents.monitoring_service import PrometheusService
        prom = PrometheusService()
        print(f"✓ PrometheusService initialized (enabled: {prom.enabled})")
    except Exception as e:
        print(f"✗ Failed to initialize PrometheusService: {e}")
    
    try:
        from app.pkgs.agents.monitoring_service import GrafanaService
        grafana = GrafanaService()
        print(f"✓ GrafanaService initialized (enabled: {grafana.enabled})")
    except Exception as e:
        print(f"✗ Failed to initialize GrafanaService: {e}")
    
    try:
        from app.pkgs.agents.jira_service import JiraService
        jira = JiraService()
        print(f"✓ JiraService initialized (enabled: {jira.enabled})")
    except Exception as e:
        print(f"✗ Failed to initialize JiraService: {e}")
    
    print("\nService initialization tests completed!")

def test_agent_initialization():
    """Test that agents can be initialized"""
    print("\nTesting agent initialization...")
    
    try:
        from app.pkgs.agents.log_analysis_agent import LogAnalysisAgent
        agent = LogAnalysisAgent()
        print("✓ LogAnalysisAgent initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize LogAnalysisAgent: {e}")
    
    try:
        from app.pkgs.agents.monitoring_alert_agent import MonitoringAlertAgent
        agent = MonitoringAlertAgent()
        print("✓ MonitoringAlertAgent initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize MonitoringAlertAgent: {e}")
    
    try:
        from app.pkgs.agents.ticket_system_agent import TicketSystemAgent
        agent = TicketSystemAgent()
        print("✓ TicketSystemAgent initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize TicketSystemAgent: {e}")
    
    print("\nAgent initialization tests completed!")

def test_model_methods():
    """Test that model methods exist"""
    print("\nTesting model methods...")
    
    try:
        from app.models.log_analysis_record import LogAnalysisRecord
        assert hasattr(LogAnalysisRecord, 'create_record')
        assert hasattr(LogAnalysisRecord, 'get_records_by_requirement')
        assert hasattr(LogAnalysisRecord, 'get_latest_record')
        assert hasattr(LogAnalysisRecord, 'to_dict')
        print("✓ LogAnalysisRecord has all required methods")
    except Exception as e:
        print(f"✗ LogAnalysisRecord methods test failed: {e}")
    
    try:
        from app.models.monitoring_alert import MonitoringAlert
        assert hasattr(MonitoringAlert, 'create_alert')
        assert hasattr(MonitoringAlert, 'get_active_alerts')
        assert hasattr(MonitoringAlert, 'get_alerts_by_service')
        assert hasattr(MonitoringAlert, 'resolve_alert')
        assert hasattr(MonitoringAlert, 'to_dict')
        print("✓ MonitoringAlert has all required methods")
    except Exception as e:
        print(f"✗ MonitoringAlert methods test failed: {e}")
    
    try:
        from app.models.ticket_record import TicketRecord
        assert hasattr(TicketRecord, 'create_ticket')
        assert hasattr(TicketRecord, 'get_tickets_by_requirement')
        assert hasattr(TicketRecord, 'get_ticket_by_key')
        assert hasattr(TicketRecord, 'update_ticket_status')
        assert hasattr(TicketRecord, 'get_historical_tickets')
        assert hasattr(TicketRecord, 'to_dict')
        print("✓ TicketRecord has all required methods")
    except Exception as e:
        print(f"✗ TicketRecord methods test failed: {e}")
    
    print("\nModel methods tests completed!")

if __name__ == '__main__':
    print("=" * 60)
    print("DevOpsGPT Agent Modules Test Suite")
    print("=" * 60)
    
    test_imports()
    test_service_initialization()
    test_agent_initialization()
    test_model_methods()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\nNote: This test only verifies basic functionality.")
    print("To fully test the agents, you need to:")
    print("1. Configure Elasticsearch, Prometheus/Grafana, and Jira in env.yaml")
    print("2. Ensure these services are running and accessible")
    print("3. Run the Flask application and test the API endpoints")
