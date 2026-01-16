#!/usr/bin/env python3
"""
Kubecost Allocation Exporter for CloudTuner

Queries Kubecost allocation API and exposes Prometheus metrics for remote_write to CloudTuner.
Designed for multi-cluster SaaS architecture where direct API access is not available.
"""

import os
import sys
import time
import logging
import requests
import random
from typing import Dict, List, Optional, Union
from prometheus_client import start_http_server, Gauge, Info, Counter
from prometheus_client.core import REGISTRY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
KUBECOST_URL = os.getenv('KUBECOST_URL', 'http://kubecost-cost-analyzer.kubecost.svc.cluster.local:9090')
EXPORTER_PORT = int(os.getenv('EXPORTER_PORT', '9103'))
SCRAPE_INTERVAL = int(os.getenv('SCRAPE_INTERVAL', '120'))  # seconds
SCRAPE_JITTER_MAX = int(os.getenv('SCRAPE_JITTER_MAX', '10'))  # seconds max jitter
AGGREGATION_LEVEL = os.getenv('AGGREGATION_LEVEL', 'namespace')  # namespace or pod
WINDOW = os.getenv('WINDOW', '1h')  # Time window for allocation query
TIME_SERIES = os.getenv('TIME_SERIES', 'false').lower() == 'true'
STEP = os.getenv('STEP', '1h')  # only used if TIME_SERIES=true
ACCUMULATE = os.getenv('ACCUMULATE', 'true').lower() == 'true'
INCLUDE_IDLE = os.getenv('INCLUDE_IDLE', 'true').lower() == 'true'
SHARE_IDLE = os.getenv('SHARE_IDLE', 'weighted')  # none|even|weighted
METRIC_MODE = os.getenv('METRIC_MODE', 'rate').lower()  # rate|total
TENANT_ID = os.getenv('TENANT_ID', '')  # Cloud account ID for multi-tenancy
CLUSTER_NAME = os.getenv('CLUSTER_NAME', 'kubernetes')
CURRENCY = os.getenv('CURRENCY', 'USD')
ENABLE_POD_METRICS = os.getenv('ENABLE_POD_METRICS', 'false').lower() == 'true'
TOP_N_PODS = int(os.getenv('TOP_N_PODS', '50'))  # Limit pod metrics to top N by cost

# Prometheus metrics
# Namespace-level metrics
namespace_total_cost = Gauge(
    'cloudtuner_kubecost_namespace_total_cost',
    'Total cost for namespace',
    ['cluster', 'namespace', 'tenant_id', 'currency']
)

namespace_cpu_cost = Gauge(
    'cloudtuner_kubecost_namespace_cpu_cost',
    'CPU cost for namespace',
    ['cluster', 'namespace', 'tenant_id', 'currency']
)

namespace_ram_cost = Gauge(
    'cloudtuner_kubecost_namespace_ram_cost',
    'RAM cost for namespace',
    ['cluster', 'namespace', 'tenant_id', 'currency']
)

namespace_pv_cost = Gauge(
    'cloudtuner_kubecost_namespace_pv_cost',
    'Persistent volume cost for namespace',
    ['cluster', 'namespace', 'tenant_id', 'currency']
)

namespace_network_cost = Gauge(
    'cloudtuner_kubecost_namespace_network_cost',
    'Network cost for namespace',
    ['cluster', 'namespace', 'tenant_id', 'currency']
)

namespace_lb_cost = Gauge(
    'cloudtuner_kubecost_namespace_lb_cost',
    'Load balancer cost for namespace',
    ['cluster', 'namespace', 'tenant_id', 'currency']
)

namespace_cpu_efficiency = Gauge(
    'cloudtuner_kubecost_namespace_cpu_efficiency',
    'CPU efficiency (usage/allocation) for namespace',
    ['cluster', 'namespace', 'tenant_id']
)

namespace_ram_efficiency = Gauge(
    'cloudtuner_kubecost_namespace_ram_efficiency',
    'RAM efficiency (usage/allocation) for namespace',
    ['cluster', 'namespace', 'tenant_id']
)

namespace_total_efficiency = Gauge(
    'cloudtuner_kubecost_namespace_total_efficiency',
    'Total efficiency for namespace',
    ['cluster', 'namespace', 'tenant_id']
)

# Cluster-level metrics
cluster_total_cost = Gauge(
    'cloudtuner_kubecost_cluster_total_cost',
    'Total cost for cluster',
    ['cluster', 'tenant_id', 'currency']
)

cluster_cpu_cost = Gauge(
    'cloudtuner_kubecost_cluster_cpu_cost',
    'Total CPU cost for cluster',
    ['cluster', 'tenant_id', 'currency']
)

cluster_ram_cost = Gauge(
    'cloudtuner_kubecost_cluster_ram_cost',
    'Total RAM cost for cluster',
    ['cluster', 'tenant_id', 'currency']
)

cluster_pv_cost = Gauge(
    'cloudtuner_kubecost_cluster_pv_cost',
    'Total PV cost for cluster',
    ['cluster', 'tenant_id', 'currency']
)

cluster_network_cost = Gauge(
    'cloudtuner_kubecost_cluster_network_cost',
    'Total network cost for cluster',
    ['cluster', 'tenant_id', 'currency']
)

cluster_lb_cost = Gauge(
    'cloudtuner_kubecost_cluster_lb_cost',
    'Total load balancer cost for cluster',
    ['cluster', 'tenant_id', 'currency']
)

cluster_cpu_efficiency = Gauge(
    'cloudtuner_kubecost_cluster_cpu_efficiency',
    'Average CPU efficiency for cluster',
    ['cluster', 'tenant_id']
)

cluster_ram_efficiency = Gauge(
    'cloudtuner_kubecost_cluster_ram_efficiency',
    'Average RAM efficiency for cluster',
    ['cluster', 'tenant_id']
)

cluster_total_efficiency = Gauge(
    'cloudtuner_kubecost_cluster_total_efficiency',
    'Average total efficiency for cluster',
    ['cluster', 'tenant_id']
)

# Pod-level metrics (optional, high cardinality)
if ENABLE_POD_METRICS:
    pod_total_cost = Gauge(
        'cloudtuner_kubecost_pod_total_cost',
        'Total cost for pod',
        ['cluster', 'namespace', 'pod', 'tenant_id', 'currency']
    )

    pod_cpu_cost = Gauge(
        'cloudtuner_kubecost_pod_cpu_cost',
        'CPU cost for pod',
        ['cluster', 'namespace', 'pod', 'tenant_id', 'currency']
    )

    pod_ram_cost = Gauge(
        'cloudtuner_kubecost_pod_ram_cost',
        'RAM cost for pod',
        ['cluster', 'namespace', 'pod', 'tenant_id', 'currency']
    )

# Exporter health metrics
scrape_duration_seconds = Gauge(
    'cloudtuner_kubecost_exporter_scrape_duration_seconds',
    'Duration of Kubecost API scrape in seconds'
)

scrape_success = Gauge(
    'cloudtuner_kubecost_exporter_scrape_success',
    'Whether the last scrape was successful (1=success, 0=failure)'
)

scrape_errors_total = Counter(
    'cloudtuner_kubecost_exporter_scrape_errors_total',
    'Total number of scrape errors'
)

# Timestamp of last successful scrape
last_success_timestamp_seconds = Gauge(
    'cloudtuner_kubecost_exporter_last_success_timestamp_seconds',
    'Unix timestamp of last successful Kubecost scrape'
)

# Series count exported per scrape (approximation)
exported_series_count = Gauge(
    'cloudtuner_kubecost_exporter_series_count',
    'Number of metric series exported in last scrape'
)

# Info metrics
exporter_info = Info(
    'cloudtuner_kubecost_exporter',
    'Exporter version and configuration'
)
exporter_info.info({
    'version': '1.0.0',
    'kubecost_url': KUBECOST_URL,
    'aggregation_level': AGGREGATION_LEVEL,
    'window': WINDOW,
    'cluster_name': CLUSTER_NAME
})


class KubecostAllocationExporter:
    """Exports Kubecost allocation data as Prometheus metrics."""

    def __init__(self):
        self.kubecost_url = KUBECOST_URL
        self.window = WINDOW
        self.aggregation_level = AGGREGATION_LEVEL
        self.cluster_name = CLUSTER_NAME
        self.tenant_id = TENANT_ID
        self.currency = CURRENCY
        self.enable_pod_metrics = ENABLE_POD_METRICS
        self.top_n_pods = TOP_N_PODS
        self.session = requests.Session()
        self.last_scrape_data = None
        self.last_scrape_time = 0

    def query_kubecost_allocation(self) -> Optional[List[Dict]]:
        """Query Kubecost allocation API and normalize response to a list of dicts."""
        url = f"{self.kubecost_url}/model/allocation"
        params = {
            'window': self.window,
            'aggregate': self.aggregation_level,
            'accumulate': str(ACCUMULATE).lower(),
            'timeSeries': str(TIME_SERIES).lower(),
            'idle': str(INCLUDE_IDLE).lower(),
            'shareIdle': SHARE_IDLE,
        }
        if TIME_SERIES and STEP:
            params['step'] = STEP

        try:
            logger.info(f"Querying Kubecost allocation API: {url}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict) and data.get('code') and data.get('code') != 200:
                logger.error(f"Kubecost API returned non-200 code: {data.get('code')}")
                return None

            payload = data.get('data', data)

            # Normalize to list of dicts
            if isinstance(payload, list):
                return payload
            elif isinstance(payload, dict):
                return [payload]
            else:
                logger.error("Unexpected Kubecost API response format for 'data'")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query Kubecost allocation API: {e}")
            return None

    def _window_hours(self) -> float:
        """Best-effort parse of WINDOW to hours for rate conversion."""
        w = self.window.strip().lower()
        try:
            if w.endswith('h'):
                return float(w[:-1])
            if w.endswith('m'):
                return max(float(w[:-1]) / 60.0, 0.0167)
            if w.endswith('d'):
                return float(w[:-1]) * 24.0
            # simple named windows
            if w in ('today', 'yesterday', '24h'):
                return 24.0
            if w == '7d':
                return 7 * 24.0
            if w == '30d':
                return 30 * 24.0
        except Exception:
            pass
        # Fallback
        return 1.0

    def _maybe_rate(self, value: Union[int, float]) -> float:
        """Convert totals to hourly rate if METRIC_MODE == 'rate'."""
        if METRIC_MODE == 'rate':
            hours = max(self._window_hours(), 0.0001)
            return float(value) / hours
        return float(value)

    def export_namespace_metrics(self, allocation_data: List[Dict]):
        """Export namespace-level metrics."""
        # Aggregate across all time windows in the response
        namespace_totals = {}

        for window_data in allocation_data:
            if window_data is None:
                continue

            for namespace, metrics in window_data.items():
                # Skip special aggregation keys
                if namespace.startswith('__'):
                    continue

                if namespace not in namespace_totals:
                    namespace_totals[namespace] = {
                        'totalCost': 0,
                        'cpuCost': 0,
                        'ramCost': 0,
                        'pvCost': 0,
                        'networkCost': 0,
                        'loadBalancerCost': 0,
                        'cpuEfficiency': 0,
                        'ramEfficiency': 0,
                        'totalEfficiency': 0,
                        'count': 0
                    }

                # Accumulate costs
                namespace_totals[namespace]['totalCost'] += metrics.get('totalCost', 0) or 0
                namespace_totals[namespace]['cpuCost'] += metrics.get('cpuCost', 0) or 0
                namespace_totals[namespace]['ramCost'] += metrics.get('ramCost', 0) or 0
                namespace_totals[namespace]['pvCost'] += metrics.get('pvCost', 0) or 0
                namespace_totals[namespace]['networkCost'] += metrics.get('networkCost', 0) or 0
                namespace_totals[namespace]['loadBalancerCost'] += metrics.get('loadBalancerCost', 0) or 0

                # Accumulate efficiency for averaging
                namespace_totals[namespace]['cpuEfficiency'] += metrics.get('cpuEfficiency', 0)
                namespace_totals[namespace]['ramEfficiency'] += metrics.get('ramEfficiency', 0)
                namespace_totals[namespace]['totalEfficiency'] += metrics.get('totalEfficiency', 0)
                namespace_totals[namespace]['count'] += 1

        # Export metrics for each namespace
        for namespace, totals in namespace_totals.items():
            labels = {
                'cluster': self.cluster_name,
                'namespace': namespace,
                'tenant_id': self.tenant_id,
                'currency': self.currency
            }

            namespace_total_cost.labels(**labels).set(self._maybe_rate(totals['totalCost']))
            namespace_cpu_cost.labels(**labels).set(self._maybe_rate(totals['cpuCost']))
            namespace_ram_cost.labels(**labels).set(self._maybe_rate(totals['ramCost']))
            namespace_pv_cost.labels(**labels).set(self._maybe_rate(totals['pvCost']))
            namespace_network_cost.labels(**labels).set(self._maybe_rate(totals['networkCost']))
            namespace_lb_cost.labels(**labels).set(self._maybe_rate(totals['loadBalancerCost']))

            # Average efficiency metrics
            count = totals['count'] or 1
            eff_labels = {k: v for k, v in labels.items() if k != 'currency'}
            namespace_cpu_efficiency.labels(**eff_labels).set(totals['cpuEfficiency'] / count)
            namespace_ram_efficiency.labels(**eff_labels).set(totals['ramEfficiency'] / count)
            namespace_total_efficiency.labels(**eff_labels).set(totals['totalEfficiency'] / count)

        logger.info(f"Exported metrics for {len(namespace_totals)} namespaces")

    def export_cluster_metrics(self, allocation_data: List[Dict]):
        """Export cluster-level aggregate metrics."""
        cluster_totals = {
            'totalCost': 0,
            'cpuCost': 0,
            'ramCost': 0,
            'pvCost': 0,
            'networkCost': 0,
            'loadBalancerCost': 0,
            'cpuEfficiency': 0,
            'ramEfficiency': 0,
            'totalEfficiency': 0,
            'count': 0
        }

        for window_data in allocation_data:
            if window_data is None:
                continue

            for namespace, metrics in window_data.items():
                # Skip special aggregation keys except idle
                if namespace.startswith('__') and namespace != '__idle__':
                    continue

                cluster_totals['totalCost'] += metrics.get('totalCost', 0) or 0
                cluster_totals['cpuCost'] += metrics.get('cpuCost', 0) or 0
                cluster_totals['ramCost'] += metrics.get('ramCost', 0) or 0
                cluster_totals['pvCost'] += metrics.get('pvCost', 0) or 0
                cluster_totals['networkCost'] += metrics.get('networkCost', 0) or 0
                cluster_totals['loadBalancerCost'] += metrics.get('loadBalancerCost', 0) or 0

                # Accumulate efficiency
                cluster_totals['cpuEfficiency'] += metrics.get('cpuEfficiency', 0)
                cluster_totals['ramEfficiency'] += metrics.get('ramEfficiency', 0)
                cluster_totals['totalEfficiency'] += metrics.get('totalEfficiency', 0)
                cluster_totals['count'] += 1

        # Export cluster metrics
        labels = {
            'cluster': self.cluster_name,
            'tenant_id': self.tenant_id,
            'currency': self.currency
        }

        cluster_total_cost.labels(**labels).set(self._maybe_rate(cluster_totals['totalCost']))
        cluster_cpu_cost.labels(**labels).set(self._maybe_rate(cluster_totals['cpuCost']))
        cluster_ram_cost.labels(**labels).set(self._maybe_rate(cluster_totals['ramCost']))
        cluster_pv_cost.labels(**labels).set(self._maybe_rate(cluster_totals['pvCost']))
        cluster_network_cost.labels(**labels).set(self._maybe_rate(cluster_totals['networkCost']))
        cluster_lb_cost.labels(**labels).set(self._maybe_rate(cluster_totals['loadBalancerCost']))

        # Average efficiency
        count = cluster_totals['count'] or 1
        eff_labels = {k: v for k, v in labels.items() if k != 'currency'}
        cluster_cpu_efficiency.labels(**eff_labels).set(cluster_totals['cpuEfficiency'] / count)
        cluster_ram_efficiency.labels(**eff_labels).set(cluster_totals['ramEfficiency'] / count)
        cluster_total_efficiency.labels(**eff_labels).set(cluster_totals['totalEfficiency'] / count)

        logger.info(f"Exported cluster-level metrics: total_cost=${cluster_totals['totalCost']:.2f} (mode={METRIC_MODE})")

    def export_pod_metrics(self, allocation_data: List[Dict]):
        """Export pod-level metrics (if enabled)."""
        if not self.enable_pod_metrics:
            return

        # Query pod-level data
        url = f"{self.kubecost_url}/model/allocation"
        params = {
            'window': self.window,
            'aggregate': 'pod',
            'accumulate': str(ACCUMULATE).lower(),
            'timeSeries': str(TIME_SERIES).lower(),
            'idle': str(INCLUDE_IDLE).lower(),
            'shareIdle': SHARE_IDLE,
        }
        if TIME_SERIES and STEP:
            params['step'] = STEP

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            pod_data = response.json().get('data', [])

            # Collect all pods with costs
            pod_costs = []
            for window_data in pod_data:
                if window_data is None:
                    continue

                for pod_name, metrics in window_data.items():
                    if pod_name.startswith('__'):
                        continue

                    namespace = metrics.get('properties', {}).get('namespace', 'unknown')
                    total_cost = metrics.get('totalCost', 0)

                    pod_costs.append({
                        'pod': pod_name,
                        'namespace': namespace,
                        'totalCost': total_cost,
                        'cpuCost': metrics.get('cpuCost', 0),
                        'ramCost': metrics.get('ramCost', 0)
                    })

            # Sort by cost and take top N
            pod_costs.sort(key=lambda x: x['totalCost'], reverse=True)
            top_pods = pod_costs[:self.top_n_pods]

            # Export metrics for top N pods
            for pod_info in top_pods:
                labels = {
                    'cluster': self.cluster_name,
                    'namespace': pod_info['namespace'],
                    'pod': pod_info['pod'],
                    'tenant_id': self.tenant_id,
                    'currency': self.currency
                }

                pod_total_cost.labels(**labels).set(pod_info['totalCost'])
                pod_cpu_cost.labels(**labels).set(pod_info['cpuCost'])
                pod_ram_cost.labels(**labels).set(pod_info['ramCost'])

            logger.info(f"Exported metrics for top {len(top_pods)} pods")

        except Exception as e:
            logger.error(f"Failed to export pod metrics: {e}")

    def scrape(self):
        """Scrape Kubecost and export metrics."""
        start_time = time.time()

        try:
            # Query Kubecost allocation API
            allocation_data = self.query_kubecost_allocation()

            if allocation_data is None:
                scrape_success.set(0)
                scrape_errors_total.inc()
                logger.error("Failed to scrape Kubecost allocation data")
                return

            series_counter = 0

            # Export namespace-level metrics
            self.export_namespace_metrics(allocation_data)
            # Rough count: 8 cost series + 3 efficiency per namespace
            try:
                ns_count = sum(1 for w in allocation_data for k in (w or {}).keys() if not str(k).startswith('__'))
                series_counter += max(ns_count, 0) * (6 + 3)
            except Exception:
                pass

            # Export cluster-level metrics
            self.export_cluster_metrics(allocation_data)
            series_counter += 6 + 3

            # Export pod-level metrics (if enabled)
            self.export_pod_metrics(allocation_data)

            # Update health metrics
            scrape_success.set(1)
            self.last_scrape_data = allocation_data
            self.last_scrape_time = time.time()
            last_success_timestamp_seconds.set(self.last_scrape_time)
            exported_series_count.set(series_counter)

            logger.info("Successfully scraped and exported Kubecost allocation data")

        except Exception as e:
            logger.error(f"Error during scrape: {e}", exc_info=True)
            scrape_success.set(0)
            scrape_errors_total.inc()

        finally:
            duration = time.time() - start_time
            scrape_duration_seconds.set(duration)
            logger.info(f"Scrape completed in {duration:.2f}s")


def main():
    """Main entry point."""
    logger.info("Starting Kubecost Allocation Exporter for CloudTuner")
    logger.info(f"Kubecost URL: {KUBECOST_URL}")
    logger.info(f"Exporter Port: {EXPORTER_PORT}")
    logger.info(f"Scrape Interval: {SCRAPE_INTERVAL}s")
    logger.info(f"Aggregation Level: {AGGREGATION_LEVEL}")
    logger.info(f"Window: {WINDOW}")
    logger.info(f"Time Series: {TIME_SERIES}, Step: {STEP}, Accumulate: {ACCUMULATE}")
    logger.info(f"Include Idle: {INCLUDE_IDLE}, Share Idle: {SHARE_IDLE}")
    logger.info(f"Metric Mode: {METRIC_MODE}")
    logger.info(f"Cluster Name: {CLUSTER_NAME}")
    logger.info(f"Tenant ID: {TENANT_ID}")
    logger.info(f"Enable Pod Metrics: {ENABLE_POD_METRICS}")

    # Initialize exporter
    exporter = KubecostAllocationExporter()

    # Start HTTP server for Prometheus scraping
    start_http_server(EXPORTER_PORT)
    logger.info(f"Metrics server started on port {EXPORTER_PORT}")

    # Initial scrape
    exporter.scrape()

    # Continuous scrape loop
    while True:
        # Add small jitter to avoid thundering herd
        sleep_for = SCRAPE_INTERVAL + random.uniform(0, max(SCRAPE_JITTER_MAX, 0))
        time.sleep(sleep_for)
        exporter.scrape()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Exporter stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
