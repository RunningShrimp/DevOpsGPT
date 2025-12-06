"""
Elasticsearch integration for log analysis
"""
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError as ESConnectionError, NotFoundError
from config import (ELASTICSEARCH_ENABLED, ELASTICSEARCH_HOST, ELASTICSEARCH_PORT,
                   ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD, ELASTICSEARCH_INDEX_PREFIX)
import json
from datetime import datetime, timedelta


class ElasticsearchService:
    """Service for interacting with Elasticsearch"""
    
    def __init__(self):
        self.enabled = ELASTICSEARCH_ENABLED
        self.client = None
        if self.enabled:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Elasticsearch client"""
        try:
            auth = None
            if ELASTICSEARCH_USERNAME and ELASTICSEARCH_PASSWORD:
                auth = (ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD)
            
            self.client = Elasticsearch(
                [{'host': ELASTICSEARCH_HOST, 'port': ELASTICSEARCH_PORT, 'scheme': 'http'}],
                basic_auth=auth
            )
            
            # Test connection
            if not self.client.ping():
                print(f"Warning: Cannot connect to Elasticsearch at {ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}")
                self.enabled = False
        except Exception as e:
            print(f"Error initializing Elasticsearch client: {str(e)}")
            self.enabled = False
    
    def is_available(self):
        """Check if Elasticsearch service is available"""
        return self.enabled and self.client is not None
    
    def index_logs(self, service_name, logs, requirement_id=None):
        """
        Index logs to Elasticsearch
        
        Args:
            service_name: Name of the service
            logs: List of log entries (dict with timestamp, level, message, etc.)
            requirement_id: Optional requirement ID for tracking
        
        Returns:
            tuple: (success, message)
        """
        if not self.is_available():
            return False, "Elasticsearch is not enabled or not available"
        
        try:
            index_name = f"{ELASTICSEARCH_INDEX_PREFIX}-{service_name.lower()}"
            
            # Bulk index logs
            for log in logs:
                doc = {
                    'timestamp': log.get('timestamp', datetime.now().isoformat()),
                    'level': log.get('level', 'INFO'),
                    'message': log.get('message', ''),
                    'service_name': service_name,
                    'requirement_id': requirement_id,
                    'indexed_at': datetime.now().isoformat()
                }
                self.client.index(index=index_name, document=doc)
            
            return True, f"Successfully indexed {len(logs)} logs"
        except Exception as e:
            return False, f"Error indexing logs: {str(e)}"
    
    def search_logs(self, service_name, query=None, time_range_hours=24, size=100):
        """
        Search logs in Elasticsearch
        
        Args:
            service_name: Name of the service
            query: Optional search query string
            time_range_hours: Hours to look back
            size: Maximum number of results
        
        Returns:
            tuple: (logs, total_count)
        """
        if not self.is_available():
            return [], 0
        
        try:
            index_name = f"{ELASTICSEARCH_INDEX_PREFIX}-{service_name.lower()}"
            
            # Build query
            must_clauses = [
                {'match': {'service_name': service_name}},
                {'range': {
                    'timestamp': {
                        'gte': f'now-{time_range_hours}h',
                        'lte': 'now'
                    }
                }}
            ]
            
            if query:
                must_clauses.append({'match': {'message': query}})
            
            search_query = {
                'query': {
                    'bool': {
                        'must': must_clauses
                    }
                },
                'sort': [{'timestamp': {'order': 'desc'}}],
                'size': size
            }
            
            result = self.client.search(index=index_name, body=search_query)
            
            logs = [hit['_source'] for hit in result['hits']['hits']]
            total = result['hits']['total']['value']
            
            return logs, total
        except NotFoundError:
            return [], 0
        except Exception as e:
            print(f"Error searching logs: {str(e)}")
            return [], 0
    
    def analyze_error_patterns(self, service_name, time_range_hours=24):
        """
        Analyze logs to find error patterns
        
        Args:
            service_name: Name of the service
            time_range_hours: Hours to look back
        
        Returns:
            dict: Analysis results with error patterns
        """
        if not self.is_available():
            return {
                'error_count': 0,
                'patterns': [],
                'top_errors': []
            }
        
        try:
            index_name = f"{ELASTICSEARCH_INDEX_PREFIX}-{service_name.lower()}"
            
            # Query for error-level logs
            search_query = {
                'query': {
                    'bool': {
                        'must': [
                            {'match': {'service_name': service_name}},
                            {'terms': {'level': ['ERROR', 'FATAL', 'CRITICAL']}},
                            {'range': {
                                'timestamp': {
                                    'gte': f'now-{time_range_hours}h',
                                    'lte': 'now'
                                }
                            }}
                        ]
                    }
                },
                'size': 0,
                'aggs': {
                    'error_count': {
                        'value_count': {'field': 'message.keyword'}
                    },
                    'top_errors': {
                        'terms': {
                            'field': 'message.keyword',
                            'size': 10
                        }
                    }
                }
            }
            
            result = self.client.search(index=index_name, body=search_query)
            
            error_count = result.get('aggregations', {}).get('error_count', {}).get('value', 0)
            top_errors = result.get('aggregations', {}).get('top_errors', {}).get('buckets', [])
            
            patterns = []
            for error in top_errors:
                patterns.append({
                    'message': error['key'],
                    'count': error['doc_count'],
                    'pattern_type': 'repeated_error'
                })
            
            return {
                'error_count': error_count,
                'patterns': patterns,
                'top_errors': [p['message'] for p in patterns[:5]]
            }
        except NotFoundError:
            return {
                'error_count': 0,
                'patterns': [],
                'top_errors': []
            }
        except Exception as e:
            print(f"Error analyzing error patterns: {str(e)}")
            return {
                'error_count': 0,
                'patterns': [],
                'top_errors': []
            }
    
    def get_log_statistics(self, service_name, time_range_hours=24):
        """
        Get log statistics by level
        
        Args:
            service_name: Name of the service
            time_range_hours: Hours to look back
        
        Returns:
            dict: Statistics by log level
        """
        if not self.is_available():
            return {}
        
        try:
            index_name = f"{ELASTICSEARCH_INDEX_PREFIX}-{service_name.lower()}"
            
            search_query = {
                'query': {
                    'bool': {
                        'must': [
                            {'match': {'service_name': service_name}},
                            {'range': {
                                'timestamp': {
                                    'gte': f'now-{time_range_hours}h',
                                    'lte': 'now'
                                }
                            }}
                        ]
                    }
                },
                'size': 0,
                'aggs': {
                    'by_level': {
                        'terms': {
                            'field': 'level.keyword'
                        }
                    }
                }
            }
            
            result = self.client.search(index=index_name, body=search_query)
            buckets = result.get('aggregations', {}).get('by_level', {}).get('buckets', [])
            
            stats = {}
            for bucket in buckets:
                stats[bucket['key']] = bucket['doc_count']
            
            return stats
        except Exception as e:
            print(f"Error getting log statistics: {str(e)}")
            return {}
