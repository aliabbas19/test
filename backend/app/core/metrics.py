"""
Request metrics tracking for performance monitoring
"""
from collections import deque
from threading import Lock
import time
import os
from typing import Dict, List


class RequestMetrics:
    """Lightweight in-memory tracker for recent request latencies."""
    
    def __init__(self, window_size: int = 500):
        self.window_size = max(50, window_size)
        self._records = deque(maxlen=self.window_size)
        self._lock = Lock()
        self._total = 0

    def add(self, endpoint: str, duration_ms: float, status_code: int):
        """Add a request metric"""
        now = time.time()
        with self._lock:
            self._records.append({
                'endpoint': endpoint,
                'duration_ms': duration_ms,
                'status': status_code,
                'ts': now
            })
            self._total += 1

    def snapshot(self) -> Dict:
        """Get current metrics snapshot"""
        with self._lock:
            records = list(self._records)
            total = self._total
        
        if not records:
            return {
                'total_requests': total,
                'recent_count': 0,
                'avg_duration_ms': 0,
                'p95_duration_ms': 0,
                'slow_requests': 0
            }

        durations = sorted(r['duration_ms'] for r in records)
        avg_duration = sum(durations) / len(durations)
        idx_95 = max(0, int(len(durations) * 0.95) - 1)
        p95 = durations[idx_95]
        slow_threshold = float(os.getenv('SLOW_REQUEST_THRESHOLD_MS', '800'))
        slow_requests = sum(1 for d in durations if d >= slow_threshold)

        return {
            'total_requests': total,
            'recent_count': len(records),
            'avg_duration_ms': round(avg_duration, 2),
            'p95_duration_ms': round(p95, 2),
            'slow_requests': slow_requests,
            'window_size': self.window_size
        }


# Global metrics instance
request_metrics = RequestMetrics()

