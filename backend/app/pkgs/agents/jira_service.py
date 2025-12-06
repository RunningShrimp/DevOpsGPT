"""
Jira integration for intelligent ticket system
"""
from jira import JIRA
from jira.exceptions import JIRAError
from config import (JIRA_ENABLED, JIRA_URL, JIRA_USERNAME, 
                   JIRA_API_TOKEN, JIRA_PROJECT_KEY)


class JiraService:
    """Service for interacting with Jira"""
    
    def __init__(self):
        self.enabled = JIRA_ENABLED
        self.url = JIRA_URL
        self.username = JIRA_USERNAME
        self.api_token = JIRA_API_TOKEN
        self.project_key = JIRA_PROJECT_KEY
        self.client = None
        
        if self.enabled and self.url and self.username and self.api_token:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Jira client"""
        try:
            self.client = JIRA(
                server=self.url,
                basic_auth=(self.username, self.api_token)
            )
        except Exception as e:
            print(f"Error initializing Jira client: {str(e)}")
            self.enabled = False
    
    def is_available(self):
        """Check if Jira service is available"""
        return self.enabled and self.client is not None
    
    def create_ticket(self, summary, description, issue_type='Bug', priority='Medium', 
                     labels=None, assignee=None):
        """
        Create a new Jira ticket
        
        Args:
            summary: Ticket summary/title
            description: Ticket description
            issue_type: Type of issue (Bug, Task, Story, etc.)
            priority: Priority level (Highest, High, Medium, Low, Lowest)
            labels: List of labels
            assignee: Username to assign the ticket to
        
        Returns:
            tuple: (success, ticket_key, ticket_url, message)
        """
        if not self.is_available():
            return False, None, None, "Jira is not enabled or not available"
        
        try:
            issue_dict = {
                'project': {'key': self.project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'name': issue_type},
                'priority': {'name': priority}
            }
            
            if labels:
                issue_dict['labels'] = labels
            
            if assignee:
                issue_dict['assignee'] = {'name': assignee}
            
            new_issue = self.client.create_issue(fields=issue_dict)
            
            ticket_key = new_issue.key
            ticket_url = f"{self.url}/browse/{ticket_key}"
            
            return True, ticket_key, ticket_url, f"Ticket {ticket_key} created successfully"
        except JIRAError as e:
            return False, None, None, f"Jira error: {str(e)}"
        except Exception as e:
            return False, None, None, f"Error creating ticket: {str(e)}"
    
    def get_ticket(self, ticket_key):
        """
        Get ticket details by key
        
        Args:
            ticket_key: Jira ticket key (e.g., DEVOPS-123)
        
        Returns:
            tuple: (success, ticket_data)
        """
        if not self.is_available():
            return False, None
        
        try:
            issue = self.client.issue(ticket_key)
            
            ticket_data = {
                'key': issue.key,
                'summary': issue.fields.summary,
                'description': issue.fields.description,
                'status': issue.fields.status.name,
                'priority': issue.fields.priority.name if issue.fields.priority else 'None',
                'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
                'created': issue.fields.created,
                'updated': issue.fields.updated,
                'url': f"{self.url}/browse/{issue.key}"
            }
            
            return True, ticket_data
        except JIRAError as e:
            return False, f"Jira error: {str(e)}"
        except Exception as e:
            return False, f"Error getting ticket: {str(e)}"
    
    def update_ticket_status(self, ticket_key, status):
        """
        Update ticket status
        
        Args:
            ticket_key: Jira ticket key
            status: New status (e.g., 'In Progress', 'Done', 'Closed')
        
        Returns:
            tuple: (success, message)
        """
        if not self.is_available():
            return False, "Jira is not enabled or not available"
        
        try:
            issue = self.client.issue(ticket_key)
            
            # Get available transitions
            transitions = self.client.transitions(issue)
            transition_id = None
            
            for transition in transitions:
                if transition['name'].lower() == status.lower():
                    transition_id = transition['id']
                    break
            
            if transition_id:
                self.client.transition_issue(issue, transition_id)
                return True, f"Ticket {ticket_key} status updated to {status}"
            else:
                return False, f"Status '{status}' not available for ticket {ticket_key}"
        except JIRAError as e:
            return False, f"Jira error: {str(e)}"
        except Exception as e:
            return False, f"Error updating ticket status: {str(e)}"
    
    def add_comment(self, ticket_key, comment):
        """
        Add a comment to a ticket
        
        Args:
            ticket_key: Jira ticket key
            comment: Comment text
        
        Returns:
            tuple: (success, message)
        """
        if not self.is_available():
            return False, "Jira is not enabled or not available"
        
        try:
            self.client.add_comment(ticket_key, comment)
            return True, f"Comment added to ticket {ticket_key}"
        except JIRAError as e:
            return False, f"Jira error: {str(e)}"
        except Exception as e:
            return False, f"Error adding comment: {str(e)}"
    
    def search_tickets(self, jql_query, max_results=50):
        """
        Search tickets using JQL
        
        Args:
            jql_query: JQL query string
            max_results: Maximum number of results
        
        Returns:
            tuple: (success, tickets_list)
        """
        if not self.is_available():
            return False, []
        
        try:
            issues = self.client.search_issues(jql_query, maxResults=max_results)
            
            tickets = []
            for issue in issues:
                ticket = {
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'status': issue.fields.status.name,
                    'priority': issue.fields.priority.name if issue.fields.priority else 'None',
                    'created': issue.fields.created,
                    'url': f"{self.url}/browse/{issue.key}"
                }
                tickets.append(ticket)
            
            return True, tickets
        except JIRAError as e:
            return False, f"Jira error: {str(e)}"
        except Exception as e:
            return False, f"Error searching tickets: {str(e)}"
    
    def get_similar_tickets(self, summary, description, max_results=5):
        """
        Find similar tickets based on summary and description
        
        Args:
            summary: Ticket summary to search for
            description: Ticket description to search for
            max_results: Maximum number of similar tickets to return
        
        Returns:
            tuple: (success, similar_tickets)
        """
        if not self.is_available():
            return False, []
        
        try:
            # Extract key terms from summary
            search_terms = summary.split()[:5]  # Use first 5 words
            search_query = ' OR '.join([f'summary ~ "{term}"' for term in search_terms if len(term) > 3])
            
            jql = f'project = {self.project_key} AND ({search_query}) ORDER BY created DESC'
            
            return self.search_tickets(jql, max_results=max_results)
        except Exception as e:
            print(f"Error finding similar tickets: {str(e)}")
            return False, []
    
    def assign_ticket(self, ticket_key, assignee):
        """
        Assign a ticket to a user
        
        Args:
            ticket_key: Jira ticket key
            assignee: Username to assign to
        
        Returns:
            tuple: (success, message)
        """
        if not self.is_available():
            return False, "Jira is not enabled or not available"
        
        try:
            issue = self.client.issue(ticket_key)
            self.client.assign_issue(issue, assignee)
            return True, f"Ticket {ticket_key} assigned to {assignee}"
        except JIRAError as e:
            return False, f"Jira error: {str(e)}"
        except Exception as e:
            return False, f"Error assigning ticket: {str(e)}"
