"""
Simple structure test for agent modules
Tests the basic file structure without importing config-dependent modules
"""

import os

def test_file_structure():
    """Test that all required files exist"""
    print("Testing file structure...")
    
    base_path = os.path.dirname(__file__)
    
    files_to_check = [
        # Models
        'app/models/log_analysis_record.py',
        'app/models/monitoring_alert.py',
        'app/models/ticket_record.py',
        
        # Services
        'app/pkgs/agents/__init__.py',
        'app/pkgs/agents/elasticsearch_service.py',
        'app/pkgs/agents/monitoring_service.py',
        'app/pkgs/agents/jira_service.py',
        
        # Agents
        'app/pkgs/agents/log_analysis_agent.py',
        'app/pkgs/agents/monitoring_alert_agent.py',
        'app/pkgs/agents/ticket_system_agent.py',
        
        # Controllers
        'app/controllers/agent_log_analysis.py',
        'app/controllers/agent_monitoring.py',
        'app/controllers/agent_ticket.py',
    ]
    
    all_exist = True
    for file_path in files_to_check:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - NOT FOUND")
            all_exist = False
    
    return all_exist

def test_syntax():
    """Test that Python files have valid syntax"""
    import py_compile
    
    print("\nTesting Python syntax...")
    
    base_path = os.path.dirname(__file__)
    
    files_to_check = [
        'app/models/log_analysis_record.py',
        'app/models/monitoring_alert.py',
        'app/models/ticket_record.py',
        'app/pkgs/agents/elasticsearch_service.py',
        'app/pkgs/agents/monitoring_service.py',
        'app/pkgs/agents/jira_service.py',
        'app/pkgs/agents/log_analysis_agent.py',
        'app/pkgs/agents/monitoring_alert_agent.py',
        'app/pkgs/agents/ticket_system_agent.py',
        'app/controllers/agent_log_analysis.py',
        'app/controllers/agent_monitoring.py',
        'app/controllers/agent_ticket.py',
    ]
    
    all_valid = True
    for file_path in files_to_check:
        full_path = os.path.join(base_path, file_path)
        try:
            py_compile.compile(full_path, doraise=True)
            print(f"✓ {file_path} - Valid syntax")
        except py_compile.PyCompileError as e:
            print(f"✗ {file_path} - Syntax error: {e}")
            all_valid = False
    
    return all_valid

def check_requirements():
    """Check that requirements.txt was updated"""
    print("\nChecking requirements.txt...")
    
    base_path = os.path.dirname(__file__)
    req_file = os.path.join(base_path, '..', 'requirements.txt')
    
    required_packages = ['elasticsearch', 'prometheus-client', 'jira', 'requests']
    
    with open(req_file, 'r') as f:
        content = f.read()
    
    all_found = True
    for package in required_packages:
        if package in content:
            print(f"✓ {package} found in requirements.txt")
        else:
            print(f"✗ {package} NOT found in requirements.txt")
            all_found = False
    
    return all_found

if __name__ == '__main__':
    print("=" * 60)
    print("DevOpsGPT Agent Modules Structure Test")
    print("=" * 60)
    
    result1 = test_file_structure()
    result2 = test_syntax()
    result3 = check_requirements()
    
    print("\n" + "=" * 60)
    if result1 and result2 and result3:
        print("✓ All structure tests passed!")
    else:
        print("✗ Some tests failed")
    print("=" * 60)
