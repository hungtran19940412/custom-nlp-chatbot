from prometheus_client import start_http_server, Counter, Gauge, Histogram
from typing import Dict, Any
import time

class MetricsCollector:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics = {}
        self.init_metrics()
        start_http_server(config['metrics_port'])

    def init_metrics(self):
        """Initialize Prometheus metrics"""
        self.metrics['requests_total'] = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )
        
        self.metrics['response_time'] = Histogram(
            'http_response_time_seconds',
            'HTTP response time in seconds',
            ['method', 'endpoint']
        )
        
        self.metrics['active_requests'] = Gauge(
            'http_active_requests',
            'Number of active HTTP requests'
        )
        
        self.metrics['error_rate'] = Counter(
            'http_error_rate',
            'HTTP error rate',
            ['method', 'endpoint']
        )

    def track_request(self, method: str, endpoint: str):
        """Track incoming request"""
        self.metrics['active_requests'].inc()
        start_time = time.time()
        return start_time

    def track_response(self, method: str, endpoint: str, status: int, start_time: float):
        """Track request completion"""
        self.metrics['active_requests'].dec()
        self.metrics['requests_total'].labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        response_time = time.time() - start_time
        self.metrics['response_time'].labels(
            method=method,
            endpoint=endpoint
        ).observe(response_time)
        
        if status >= 400:
            self.metrics['error_rate'].labels(
                method=method,
                endpoint=endpoint
            ).inc()

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics values"""
        return {
            name: metric.collect()[0].samples[0].value
            for name, metric in self.metrics.items()
        }
