"""
Performance monitoring middleware and utilities for ML-Battle backend.
"""
import time
import logging
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor request/response times and database queries.
    Logs slow requests and queries for optimization.
    """
    
    def process_request(self, request):
        """Record start time and reset query counter."""
        request._start_time = time.time()
        request._queries_before = len(connection.queries)
    
    def process_response(self, request, response):
        """Log request performance metrics."""
        if hasattr(request, '_start_time'):
            # Calculate request duration
            duration = time.time() - request._start_time
            duration_ms = round(duration * 1000, 2)
            
            # Calculate number of queries
            queries_count = len(connection.queries) - getattr(request, '_queries_before', 0)
            
            # Build log message
            log_data = {
                'method': request.method,
                'path': request.path,
                'duration_ms': duration_ms,
                'queries': queries_count,
                'status': response.status_code
            }
            
            # Log as warning if slow or many queries
            if duration_ms > 1000 or queries_count > 20:
                logger.warning(f"SLOW REQUEST: {log_data}")
            elif duration_ms > 500 or queries_count > 10:
                logger.info(f"Request: {log_data}")
            else:
                logger.debug(f"Request: {log_data}")
            
            # Add custom headers for debugging (only in development)
            if hasattr(settings, 'DEBUG') and settings.DEBUG:
                response['X-Request-Duration-Ms'] = str(duration_ms)
                response['X-DB-Queries'] = str(queries_count)
        
        return response


def log_query_count(func):
    """
    Decorator to log database query count for a function/view.
    Usage: @log_query_count
    """
    def wrapper(*args, **kwargs):
        queries_before = len(connection.queries)
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        duration = time.time() - start_time
        queries_count = len(connection.queries) - queries_before
        
        logger.info(
            f"{func.__name__}: {round(duration * 1000, 2)}ms, "
            f"{queries_count} queries"
        )
        
        if queries_count > 10:
            logger.warning(
                f"High query count in {func.__name__}: {queries_count} queries"
            )
        
        return result
    
    return wrapper


def analyze_queries():
    """
    Analyze and log all database queries from the connection.
    Use this in Django shell or tests to debug N+1 queries.
    """
    for i, query in enumerate(connection.queries, 1):
        logger.info(f"Query {i}: {query['sql'][:200]}... ({query['time']}s)")


class QueryDebugContext:
    """
    Context manager to debug queries in a code block.
    
    Usage:
        with QueryDebugContext("My operation"):
            # Your code here
            Competition.objects.all()
    """
    
    def __init__(self, label="Operation"):
        self.label = label
        self.queries_before = 0
        self.start_time = 0
    
    def __enter__(self):
        self.queries_before = len(connection.queries)
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        queries_count = len(connection.queries) - self.queries_before
        
        logger.info(
            f"{self.label}: {round(duration * 1000, 2)}ms, "
            f"{queries_count} queries"
        )
        
        if queries_count > 10:
            logger.warning(f"High query count in {self.label}: {queries_count}")
            for query in connection.queries[self.queries_before:]:
                logger.debug(f"  {query['sql'][:150]}... ({query['time']}s)")


# Import settings for middleware
from django.conf import settings
