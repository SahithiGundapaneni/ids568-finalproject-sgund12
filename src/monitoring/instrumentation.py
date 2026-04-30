"""
Component 1: Production Monitoring - Metrics Instrumentation
IDS 568 Final Project - Sreesahithi Gundapaneni (sgund12)

This module instruments an LLM inference API with Prometheus metrics,
tracking latency, throughput, error rates, and input integrity signals.
"""

import time
import random
import threading
from prometheus_client import (
    Counter, Histogram, Gauge, Summary,
    start_http_server, CollectorRegistry, generate_latest
)

# ── Prometheus metric definitions ──────────────────────────────────────────────

REQUEST_COUNT = Counter(
    'llm_requests_total',
    'Total number of LLM inference requests',
    ['endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'llm_request_latency_seconds',
    'LLM inference request latency in seconds',
    ['endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0]
)

ACTIVE_REQUESTS = Gauge(
    'llm_active_requests',
    'Number of currently active LLM requests'
)

TOKEN_COUNT = Histogram(
    'llm_response_tokens',
    'Number of tokens in LLM responses',
    buckets=[10, 50, 100, 200, 500, 1000]
)

INPUT_LENGTH = Histogram(
    'llm_input_length_chars',
    'Character length of input prompts',
    buckets=[10, 50, 100, 250, 500, 1000, 2000]
)

DRIFT_SCORE = Gauge(
    'llm_input_drift_score',
    'Rolling drift score for input distribution (0=stable, 1=high drift)'
)

ERROR_RATE = Gauge(
    'llm_error_rate_1min',
    'Rolling 1-minute error rate'
)

THROUGHPUT = Gauge(
    'llm_throughput_rpm',
    'Requests per minute (rolling)'
)


def record_request(endpoint: str, latency: float, status: str,
                   tokens: int, input_len: int):
    """Record a single LLM request's metrics."""
    REQUEST_COUNT.labels(endpoint=endpoint, status=status).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
    TOKEN_COUNT.observe(tokens)
    INPUT_LENGTH.observe(input_len)


def simulate_traffic(duration_seconds: int = 120, requests_per_second: float = 2.0):
    """
    Simulate realistic LLM API traffic for dashboard population.
    Generates a mix of normal requests, slow requests, and errors.
    """
    print(f"[Monitor] Simulating {duration_seconds}s of LLM traffic "
          f"at ~{requests_per_second} req/s ...")

    start = time.time()
    request_times = []
    error_count = 0
    total_count = 0

    while time.time() - start < duration_seconds:
        # Simulate active request
        ACTIVE_REQUESTS.inc()

        # Determine request scenario (90% normal, 7% slow, 3% error)
        scenario = random.choices(
            ['normal', 'slow', 'error'],
            weights=[0.90, 0.07, 0.03]
        )[0]

        if scenario == 'normal':
            latency = random.gauss(0.45, 0.15)   # ~450ms avg
            latency = max(0.05, latency)
            tokens  = int(random.gauss(180, 60))
            tokens  = max(10, tokens)
            status  = 'success'
        elif scenario == 'slow':
            latency = random.gauss(3.5, 0.8)     # ~3.5s (bottleneck)
            latency = max(2.0, latency)
            tokens  = int(random.gauss(400, 100))
            tokens  = max(50, tokens)
            status  = 'success'
        else:
            latency = random.gauss(0.1, 0.05)
            latency = max(0.01, latency)
            tokens  = 0
            status  = 'error'
            error_count += 1

        input_len = int(random.gauss(200, 80))
        input_len = max(10, input_len)

        time.sleep(latency)

        record_request(
            endpoint='/generate',
            latency=latency,
            status=status,
            tokens=tokens,
            input_len=input_len
        )

        ACTIVE_REQUESTS.dec()

        # Update rolling metrics
        now = time.time()
        request_times.append(now)
        total_count += 1

        # Keep only last 60s for rolling window
        request_times = [t for t in request_times if now - t <= 60]
        THROUGHPUT.set(len(request_times))

        if total_count > 0:
            ERROR_RATE.set(error_count / total_count)

        # Simulate mild input drift that grows over time
        elapsed_fraction = (now - start) / duration_seconds
        drift = min(0.15 + elapsed_fraction * 0.35, 0.5)  # grows 0.15→0.5
        DRIFT_SCORE.set(drift + random.gauss(0, 0.02))

        # Sleep between requests
        sleep_time = max(0.01, (1.0 / requests_per_second) - latency)
        time.sleep(sleep_time)

    print(f"[Monitor] Simulation complete. Total requests: {total_count}, "
          f"Errors: {error_count}")


if __name__ == '__main__':
    # Start Prometheus metrics server on port 8000
    start_http_server(8000)
    print("[Monitor] Prometheus metrics server started on http://localhost:8000/metrics")

    # Run traffic simulation
    simulate_traffic(duration_seconds=120, requests_per_second=1.5)
    print("[Monitor] Done. Metrics available at http://localhost:8000/metrics")
