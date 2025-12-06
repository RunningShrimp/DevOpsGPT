"""
Intelligent ticket system agent with historical data analysis
"""
from app.pkgs.agents.jira_service import JiraService
from app.pkgs.tools.llm import llm
from app.models.ticket_record import TicketRecord
import json


class TicketSystemAgent:
    """Agent for intelligent ticket creation and management"""
    
    def __init__(self):
        self.jira = JiraService()
    
    def create_ticket_from_fault(self, requirement_id, service_name, fault_data, 
                                source_type='log_analysis', source_id=None):
        """
        Automatically create a Jira ticket from fault/alert data
        
        Args:
            requirement_id: Requirement ID
            service_name: Name of the service
            fault_data: Fault or alert data dictionary
            source_type: Type of source (log_analysis, monitoring_alert, manual)
            source_id: ID of the source record
        
        Returns:
            dict: Ticket creation result
        """
        # Generate ticket title and description using AI
        ticket_info = self._generate_ticket_content(service_name, fault_data, source_type)
        
        # Find similar historical tickets
        similar_tickets = self._find_similar_tickets(service_name, ticket_info['title'])
        
        # Generate recommendations based on historical data
        recommendations = self._generate_recommendations(similar_tickets, fault_data)
        
        # Determine priority
        priority = self._determine_priority(fault_data, similar_tickets)
        
        # Auto-assign if possible
        assignee = self._suggest_assignee(similar_tickets)
        
        # Create ticket in Jira if enabled
        if self.jira.is_available():
            success, ticket_key, ticket_url, message = self.jira.create_ticket(
                summary=ticket_info['title'],
                description=ticket_info['description'],
                issue_type='Bug',
                priority=priority,
                labels=[service_name, source_type],
                assignee=assignee
            )
            
            if not success:
                return {
                    'success': False,
                    'error': message
                }
        else:
            # Create a mock ticket if Jira is not available
            ticket_key = f"MOCK-{requirement_id}-{source_id or 0}"
            ticket_url = f"http://localhost/tickets/{ticket_key}"
            message = "Jira not available, created mock ticket"
        
        # Store ticket record in database
        ticket_record = TicketRecord.create_ticket(
            requirement_id=requirement_id,
            service_name=service_name,
            ticket_key=ticket_key,
            ticket_url=ticket_url,
            ticket_title=ticket_info['title'],
            ticket_description=ticket_info['description'],
            ticket_type='bug',
            priority=priority.lower(),
            status='open',
            source_type=source_type,
            source_id=source_id,
            fault_summary=json.dumps(fault_data),
            recommended_solutions=recommendations,
            similar_tickets=[t['key'] for t in similar_tickets] if similar_tickets else None,
            auto_assigned_to=assignee
        )
        
        return {
            'success': True,
            'ticket_key': ticket_key,
            'ticket_url': ticket_url,
            'ticket_id': ticket_record.id,
            'priority': priority,
            'recommendations': recommendations,
            'similar_tickets': similar_tickets,
            'message': message
        }
    
    def _generate_ticket_content(self, service_name, fault_data, source_type):
        """
        Generate ticket title and description using AI
        
        Args:
            service_name: Name of the service
            fault_data: Fault or alert data
            source_type: Type of source
        
        Returns:
            dict: Title and description
        """
        if source_type == 'log_analysis':
            fault_summary = fault_data.get('fault_report', 'Log analysis detected issues')
            error_count = fault_data.get('error_count', 0)
            severity = fault_data.get('severity', 'unknown')
            
            context = f"""Service: {service_name}
Source: Log Analysis
Severity: {severity}
Error Count: {error_count}
Fault Report:
{fault_summary}"""
        
        elif source_type == 'monitoring_alert':
            metric_name = fault_data.get('metric_name', 'Unknown')
            current_value = fault_data.get('current_value', 0)
            threshold = fault_data.get('threshold_value', 0)
            
            context = f"""Service: {service_name}
Source: Monitoring Alert
Metric: {metric_name}
Current Value: {current_value}
Threshold: {threshold}
Description: {fault_data.get('anomaly_description', 'No description')}"""
        
        else:
            context = f"""Service: {service_name}
Source: {source_type}
Data: {json.dumps(fault_data, indent=2)}"""
        
        prompt = f"""Generate a concise Jira ticket title and description for this issue:

{context}

Provide:
1. Title (one line, under 100 characters)
2. Description (clear, structured, actionable)

Format the output as:
TITLE: <title here>
DESCRIPTION: <description here>"""
        
        try:
            response = llm(prompt)
            
            # Parse response
            title = "Unknown Issue"
            description = context
            
            if 'TITLE:' in response:
                parts = response.split('DESCRIPTION:', 1)
                title = parts[0].replace('TITLE:', '').strip()
                if len(parts) > 1:
                    description = parts[1].strip()
            
            return {
                'title': title[:200],  # Limit title length
                'description': description
            }
        except Exception as e:
            print(f"Error generating ticket content: {str(e)}")
            return {
                'title': f"Issue in {service_name}",
                'description': context
            }
    
    def _find_similar_tickets(self, service_name, ticket_title):
        """
        Find similar historical tickets
        
        Args:
            service_name: Name of the service
            ticket_title: Ticket title to search for
        
        Returns:
            list: Similar tickets
        """
        # Get historical tickets from database
        historical = TicketRecord.get_historical_tickets(service_name=service_name, limit=20)
        
        # Simple similarity check (could be enhanced with embeddings)
        similar = []
        title_words = set(ticket_title.lower().split())
        
        for ticket in historical:
            ticket_title_words = set(ticket.get('ticket_title', '').lower().split())
            # Calculate overlap
            overlap = len(title_words & ticket_title_words)
            if overlap >= 2:  # At least 2 common words
                similar.append({
                    'key': ticket.get('ticket_key'),
                    'title': ticket.get('ticket_title'),
                    'resolution_time': ticket.get('resolution_time'),
                    'solutions': ticket.get('recommended_solutions', [])
                })
        
        return similar[:5]  # Return top 5
    
    def _generate_recommendations(self, similar_tickets, fault_data):
        """
        Generate solution recommendations based on historical data
        
        Args:
            similar_tickets: List of similar historical tickets
            fault_data: Current fault data
        
        Returns:
            list: Recommended solutions
        """
        if not similar_tickets:
            return self._generate_generic_recommendations(fault_data)
        
        # Collect solutions from similar tickets
        historical_solutions = []
        for ticket in similar_tickets:
            solutions = ticket.get('solutions', [])
            if solutions:
                historical_solutions.extend(solutions)
        
        if not historical_solutions:
            return self._generate_generic_recommendations(fault_data)
        
        # Use AI to synthesize recommendations
        prompt = f"""Based on historical ticket resolutions, recommend solutions for the current issue.

Historical Solutions:
{json.dumps(historical_solutions, indent=2)}

Current Issue:
{json.dumps(fault_data, indent=2)}

Provide 3-5 prioritized, actionable recommendations."""
        
        try:
            response = llm(prompt)
            # Extract numbered items
            solutions = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    solutions.append(line)
            return solutions if solutions else [response]
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            return historical_solutions[:5]
    
    def _generate_generic_recommendations(self, fault_data):
        """
        Generate generic recommendations when no historical data is available
        
        Args:
            fault_data: Fault data
        
        Returns:
            list: Generic recommendations
        """
        return [
            "1. Review application logs for detailed error information",
            "2. Check service health and resource utilization",
            "3. Verify recent deployments or configuration changes",
            "4. Monitor the situation and escalate if issue persists",
            "5. Update documentation with findings"
        ]
    
    def _determine_priority(self, fault_data, similar_tickets):
        """
        Determine ticket priority based on fault data and historical patterns
        
        Args:
            fault_data: Fault data
            similar_tickets: Similar historical tickets
        
        Returns:
            str: Priority level (Highest, High, Medium, Low, Lowest)
        """
        severity = fault_data.get('severity', 'low')
        
        # Map severity to Jira priority
        priority_map = {
            'critical': 'Highest',
            'high': 'High',
            'medium': 'Medium',
            'low': 'Low'
        }
        
        return priority_map.get(severity, 'Medium')
    
    def _suggest_assignee(self, similar_tickets):
        """
        Suggest an assignee based on historical ticket assignments
        
        Args:
            similar_tickets: Similar historical tickets
        
        Returns:
            str: Suggested assignee username or None
        """
        # Count assignees from similar tickets
        assignee_counts = {}
        for ticket in similar_tickets:
            assignee = ticket.get('auto_assigned_to')
            if assignee:
                assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
        
        if assignee_counts:
            # Return most common assignee
            return max(assignee_counts, key=assignee_counts.get)
        
        return None
    
    def update_ticket_from_jira(self, ticket_key):
        """
        Update local ticket record with latest data from Jira
        
        Args:
            ticket_key: Jira ticket key
        
        Returns:
            tuple: (success, message)
        """
        success, ticket_data = self.jira.get_ticket(ticket_key)
        
        if not success:
            return False, f"Failed to get ticket from Jira: {ticket_data}"
        
        # Update local record
        local_ticket = TicketRecord.get_ticket_by_key(ticket_key)
        if not local_ticket:
            return False, f"Local ticket record not found for {ticket_key}"
        
        TicketRecord.update_ticket_status(
            local_ticket['id'],
            ticket_data['status'].lower()
        )
        
        return True, f"Ticket {ticket_key} updated successfully"
