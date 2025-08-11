"""Monitoring utilities for Redshift query performance and resource usage."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Union

from .models import QueryState


@dataclass
class QueryMetrics:
    """Metrics for a single query execution."""
    query_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    state: QueryState = QueryState.SUBMITTED
    duration_ms: Optional[float] = None
    cpu_time_ms: Optional[float] = None
    memory_mb: Optional[float] = None
    disk_io_mb: Optional[float] = None
    rows_processed: Optional[int] = None
    rows_returned: Optional[int] = None
    compilation_time_ms: Optional[float] = None
    queue_time_ms: Optional[float] = None
    execution_time_ms: Optional[float] = None
    error_message: Optional[str] = None

    def update(self, metrics: Dict[str, Union[float, int, str]]) -> None:
        """Update metrics with new values."""
        for key, value in metrics.items():
            if hasattr(self, key):
                setattr(self, key, value)


class QueryMonitor:
    """Monitor and collect metrics for Redshift queries."""

    def __init__(self):
        self._active_queries: Dict[str, QueryMetrics] = {}
        self._completed_queries: List[QueryMetrics] = []

    def start_query(self, query_id: str) -> None:
        """Start monitoring a new query."""
        self._active_queries[query_id] = QueryMetrics(
            query_id=query_id,
            start_time=datetime.now(),
        )

    def update_query(self, query_id: str, metrics: Dict[str, Union[float, int, str]]) -> None:
        """Update metrics for an active query."""
        if query_id in self._active_queries:
            self._active_queries[query_id].update(metrics)

    def complete_query(self, query_id: str, state: QueryState, error: Optional[str] = None) -> None:
        """Mark a query as completed."""
        if query_id in self._active_queries:
            metrics = self._active_queries[query_id]
            metrics.end_time = datetime.now()
            metrics.state = state
            if error:
                metrics.error_message = error
            if metrics.end_time and metrics.start_time:
                metrics.duration_ms = (
                    metrics.end_time - metrics.start_time).total_seconds() * 1000
            self._completed_queries.append(metrics)
            del self._active_queries[query_id]

    def get_active_queries(self) -> List[QueryMetrics]:
        """Get metrics for all active queries."""
        return list(self._active_queries.values())

    def get_completed_queries(
        self,
        limit: Optional[int] = None,
        state: Optional[QueryState] = None,
    ) -> List[QueryMetrics]:
        """Get metrics for completed queries with optional filtering."""
        queries = self._completed_queries
        if state:
            queries = [q for q in queries if q.state == state]
        if limit:
            queries = queries[-limit:]
        return queries

    def get_query_metrics(self, query_id: str) -> Optional[QueryMetrics]:
        """Get metrics for a specific query."""
        if query_id in self._active_queries:
            return self._active_queries[query_id]
        for query in self._completed_queries:
            if query.query_id == query_id:
                return query
        return None


class ResourceMonitor:
    """Monitor Redshift cluster resource usage."""

    def __init__(self):
        self._metrics: Dict[str, List[float]] = {
            'cpu_utilization': [],
            'memory_utilization': [],
            'disk_queue_depth': [],
            'network_receive_throughput': [],
            'network_transmit_throughput': [],
            'read_iops': [],
            'write_iops': [],
            'read_latency': [],
            'write_latency': [],
        }
        self._timestamps: List[datetime] = []

    def record_metrics(
        self,
        cpu_utilization: float,
        memory_utilization: float,
        disk_queue_depth: float,
        network_receive_throughput: float,
        network_transmit_throughput: float,
        read_iops: float,
        write_iops: float,
        read_latency: float,
        write_latency: float,
    ) -> None:
        """Record a new set of resource metrics."""
        self._metrics['cpu_utilization'].append(cpu_utilization)
        self._metrics['memory_utilization'].append(memory_utilization)
        self._metrics['disk_queue_depth'].append(disk_queue_depth)
        self._metrics['network_receive_throughput'].append(
            network_receive_throughput)
        self._metrics['network_transmit_throughput'].append(
            network_transmit_throughput)
        self._metrics['read_iops'].append(read_iops)
        self._metrics['write_iops'].append(write_iops)
        self._metrics['read_latency'].append(read_latency)
        self._metrics['write_latency'].append(write_latency)
        self._timestamps.append(datetime.now())

    def get_metrics(
        self,
        metric_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[float]:
        """Get historical values for a specific metric with optional time range."""
        if metric_name not in self._metrics:
            raise ValueError(f"Unknown metric: {metric_name}")

        if not start_time and not end_time:
            return self._metrics[metric_name]

        values = []
        for timestamp, value in zip(self._timestamps, self._metrics[metric_name]):
            if start_time and timestamp < start_time:
                continue
            if end_time and timestamp > end_time:
                continue
            values.append(value)
        return values

    def get_average(self, metric_name: str, window_size: int = 10) -> float:
        """Calculate the moving average for a metric."""
        if metric_name not in self._metrics:
            raise ValueError(f"Unknown metric: {metric_name}")

        values = self._metrics[metric_name][-window_size:]
        if not values:
            return 0.0
        return sum(values) / len(values)

    def get_peak(self, metric_name: str, window_size: int = 10) -> float:
        """Get the peak value for a metric within the window."""
        if metric_name not in self._metrics:
            raise ValueError(f"Unknown metric: {metric_name}")

        values = self._metrics[metric_name][-window_size:]
        if not values:
            return 0.0
        return max(values)


class PerformanceAnalyzer:
    """Analyze query and resource performance patterns."""

    def __init__(self, query_monitor: QueryMonitor, resource_monitor: ResourceMonitor):
        self.query_monitor = query_monitor
        self.resource_monitor = resource_monitor

    def analyze_query_patterns(self) -> Dict[str, float]:
        """Analyze patterns in query execution times."""
        completed = self.query_monitor.get_completed_queries()
        if not completed:
            return {}

        total_queries = len(completed)
        successful = sum(1 for q in completed if q.state ==
                         QueryState.COMPLETED)
        failed = sum(1 for q in completed if q.state == QueryState.FAILED)
        avg_duration = sum(
            q.duration_ms or 0 for q in completed) / total_queries
        avg_compilation = sum(
            q.compilation_time_ms or 0 for q in completed) / total_queries
        avg_queue = sum(
            q.queue_time_ms or 0 for q in completed) / total_queries
        avg_execution = sum(
            q.execution_time_ms or 0 for q in completed) / total_queries

        return {
            'success_rate': successful / total_queries,
            'failure_rate': failed / total_queries,
            'avg_duration_ms': avg_duration,
            'avg_compilation_ms': avg_compilation,
            'avg_queue_ms': avg_queue,
            'avg_execution_ms': avg_execution,
        }

    def analyze_resource_usage(self) -> Dict[str, Dict[str, float]]:
        """Analyze resource usage patterns."""
        metrics = {}
        for metric_name in self.resource_monitor._metrics:
            metrics[metric_name] = {
                'current': self.resource_monitor.get_average(metric_name, window_size=1),
                'avg_5min': self.resource_monitor.get_average(metric_name, window_size=300),
                'peak_5min': self.resource_monitor.get_peak(metric_name, window_size=300),
            }
        return metrics

    def identify_bottlenecks(self) -> List[str]:
        """Identify potential performance bottlenecks."""
        bottlenecks = []
        metrics = self.analyze_resource_usage()

        # CPU bottleneck
        if metrics['cpu_utilization']['avg_5min'] > 80:
            bottlenecks.append("High CPU utilization")

        # Memory bottleneck
        if metrics['memory_utilization']['avg_5min'] > 80:
            bottlenecks.append("High memory utilization")

        # Disk I/O bottleneck
        if metrics['disk_queue_depth']['avg_5min'] > 10:
            bottlenecks.append("High disk queue depth")

        # Network bottleneck
        network_util = (
            metrics['network_receive_throughput']['avg_5min'] +
            metrics['network_transmit_throughput']['avg_5min']
        )
        if network_util > 100_000_000:  # 100 MB/s
            bottlenecks.append("High network utilization")

        # Query patterns
        patterns = self.analyze_query_patterns()
        if patterns.get('avg_queue_ms', 0) > 1000:  # 1 second
            bottlenecks.append("Long query queue times")
        if patterns.get('failure_rate', 0) > 0.1:  # 10%
            bottlenecks.append("High query failure rate")

        return bottlenecks
