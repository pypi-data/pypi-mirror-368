import asyncio

import psutil
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    push_to_gateway,
)
from prometheus_client.exposition import basic_auth_handler

from pyvetic.constants import (
    APP_NAME,
    MONITORING_AUTH_PASS,
    MONITORING_AUTH_USER,
    PUSHGATEWAY_HOST,
    PUSHGATEWAY_JOB_NAME,
)
from pyvetic.logger import get_logger

logger = get_logger(__name__)


# Not for external use
class MetricsCollectorSingleton:
    _instance = None

    def __init__(self):
        self.registry = None
        self.request_counter = None
        self.exception_counter = None
        self.request_latency = None
        self.cpu_usage = None
        self.memory_usage = None
        self.runs = 0

        self.initialize()

    @staticmethod
    def get_instance():
        if MetricsCollectorSingleton._instance is None:
            MetricsCollectorSingleton._instance = MetricsCollectorSingleton()
        return MetricsCollectorSingleton._instance

    def initialize(self):
        if self.registry is not None:
            del self.registry
            del self.request_counter
            del self.exception_counter
            del self.request_latency
            del self.cpu_usage
            del self.memory_usage

            self.runs = 0

        self.registry = CollectorRegistry()
        self.request_counter = Counter(
            "http_requests",
            f"Total number of HTTP requests to {APP_NAME}",
            ["app", "method", "endpoint", "status_code"],
            registry=self.registry,
        )
        self.exception_counter = Counter(
            "http_exceptions",
            f"Total number of exceptions in {APP_NAME}",
            ["app", "method", "endpoint", "status_code"],
            registry=self.registry,
        )
        self.request_latency = Histogram(
            "http_request_latency_seconds",
            f"Request latency in seconds to {APP_NAME}",
            ["app", "method", "endpoint", "status_code"],
            registry=self.registry,
            buckets=[0.1, 0.5, 1, 5, 10],
        )
        self.cpu_usage = Gauge(
            "system_cpu_usage_percent", "Current CPU usage percentage", ["app"], registry=self.registry
        )
        self.memory_usage = Gauge(
            "system_memory_usage_percent", "Current memory usage percentage", ["app"], registry=self.registry
        )

    def increment_runs(self):
        self.runs += 1

    def observe_cpu_usage(self, cpu_percent):
        self.increment_runs()
        self.cpu_usage.labels(app=APP_NAME).set(cpu_percent)

    def observe_memory_usage(self, memory_percent):
        self.increment_runs()
        self.memory_usage.labels(app=APP_NAME).set(memory_percent)

    def observe_request(self, method, endpoint, status_code):
        self.increment_runs()
        self.request_counter.labels(app=APP_NAME, method=method, endpoint=endpoint, status_code=status_code).inc()

    def observe_exception(self, method, endpoint, status_code):
        self.increment_runs()
        self.exception_counter.labels(app=APP_NAME, method=method, endpoint=endpoint, status_code=status_code).inc()

    def observe_request_latency(self, method, endpoint, status_code, latency):
        self.increment_runs()
        self.request_latency.labels(app=APP_NAME, method=method, endpoint=endpoint, status_code=status_code).observe(
            latency
        )

    def push_metrics(self):
        try:
            push_to_gateway(
                gateway=PUSHGATEWAY_HOST,
                job=PUSHGATEWAY_JOB_NAME,
                registry=self.registry,
                timeout=3,
                handler=self.auth_handler,
            )
        except Exception as e:
            logger.error(f"Failed to push metrics to Pushgateway: {e}")

        if self.runs > 10000000:
            # Reset metrics after 10 million runs
            self.initialize()

    def auth_handler(self, url, method, timeout, headers, data):
        return basic_auth_handler(url, method, timeout, headers, data, MONITORING_AUTH_USER, MONITORING_AUTH_PASS)


async def collect_system_metrics(interval=5):
    """Background task to collect system metrics and push to Pushgateway"""

    while True:
        metrics_collector = MetricsCollectorSingleton.get_instance()
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()

            metrics_collector.observe_cpu_usage(cpu_percent)
            metrics_collector.observe_memory_usage(memory.percent)

            metrics_collector.push_metrics()
        except Exception as e:
            logger.error(f"Error in collect_system_metrics: {e}")

        await asyncio.sleep(interval)  # Collect metrics in intervals
