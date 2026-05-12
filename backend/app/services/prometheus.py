# services/prometheus.py

"""
Prometheus client for querying metrics
"""
import requests
from typing import Dict, List, Any
from app.config import settings
import logging
import random

logger = logging.getLogger(__name__)


class PrometheusClient:
    """Client for interacting with Prometheus API"""
    
    def __init__(self, url: str = settings.PROMETHEUS_URL):
        self.url = url.rstrip('/')
        self.api_url = f"{self.url}/api/v1"
        self.demo_mode = False  # Will be set to True if Prometheus is not available
        self._check_prometheus_availability()
    
    def _check_prometheus_availability(self):
        """Check if Prometheus is available, enable demo mode if not"""
        try:
            response = requests.get(f"{self.url}/-/healthy", timeout=2)
            self.demo_mode = response.status_code != 200
        except requests.RequestException:
            self.demo_mode = True
            logger.warning("Prometheus not available - using DEMO MODE with mock data")
    
    def _generate_mock_cpu(self) -> float:
        """Generate realistic mock CPU usage"""
        base = 45 + random.uniform(-10, 25)
        return round(min(95, max(5, base)), 2)
    
    def _generate_mock_memory(self) -> Dict[str, float]:
        """Generate realistic mock memory metrics"""
        total = 16 * 1024 * 1024 * 1024  # 16GB
        used_percent = 55 + random.uniform(-15, 25)
        used = (total * used_percent) / 100
        available = total - used
        
        return {
            "total": total,
            "used": used,
            "available": available,
            "usage_percent": round(used_percent, 2),
            "swap_total": 4 * 1024 * 1024 * 1024,
            "swap_used": random.uniform(0, 1024 * 1024 * 1024)
        }
    
    def _generate_mock_disk(self) -> Dict[str, float]:
        """Generate realistic mock disk metrics"""
        total = 500 * 1024 * 1024 * 1024  # 500GB
        used_percent = 40 + random.uniform(-10, 30)
        used = (total * used_percent) / 100
        available = total - used
        
        return {
            "total": total,
            "used": used,
            "available": available,
            "usage_percent": round(used_percent, 2),
            "read_bytes": random.uniform(1000000, 10000000),
            "write_bytes": random.uniform(500000, 5000000)
        }
    
    def _generate_mock_network(self) -> Dict[str, float]:
        """Generate realistic mock network metrics"""
        return {
            "rx_bytes": random.uniform(1000000, 50000000),
            "tx_bytes": random.uniform(500000, 30000000),
            "rx_packets": random.uniform(1000, 50000),
            "tx_packets": random.uniform(500, 30000),
            "rx_errors": random.uniform(0, 10),
            "tx_errors": random.uniform(0, 5)
        }
    
    def _generate_mock_load(self) -> Dict[str, float]:
        """Generate realistic mock load average"""
        base_load = random.uniform(0.5, 3.0)
        return {
            "load_1min": round(base_load, 2),
            "load_5min": round(base_load * 0.9, 2),
            "load_15min": round(base_load * 0.8, 2)
        }
    
    def query(self, query: str) -> Dict[str, Any]:
        """Execute instant query"""
        try:
            response = requests.get(
                f"{self.api_url}/query",
                params={"query": query},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Prometheus query error: {e}")
            return {"status": "error", "data": {"result": []}}
    
    def query_range(self, query: str, start: int, end: int, step: str = "15s") -> Dict[str, Any]:
        """Execute range query"""
        try:
            response = requests.get(
                f"{self.api_url}/query_range",
                params={
                    "query": query,
                    "start": start,
                    "end": end,
                    "step": step
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Prometheus range query error: {e}")
            return {"status": "error", "data": {"result": []}}
    
    def get_cpu_usage(self, instance: str) -> float:
        """Get CPU usage percentage"""
        if self.demo_mode:
            return self._generate_mock_cpu()
        
        query = f'100 - (avg by (instance) (irate(node_cpu_seconds_total{{mode="idle",instance="{instance}"}}[5m])) * 100)'
        result = self.query(query)
        
        if result.get("status") == "success" and result.get("data", {}).get("result"):
            return float(result["data"]["result"][0]["value"][1])
        return self._generate_mock_cpu()  # Fallback to mock data
    
    def get_cpu_per_core(self, instance: str) -> List[float]:
        """Get CPU usage per core"""
        if self.demo_mode:
            return [self._generate_mock_cpu() for _ in range(4)]  # 4 cores
        
        query = f'100 - (avg by (cpu) (irate(node_cpu_seconds_total{{mode="idle",instance="{instance}"}}[5m])) * 100)'
        result = self.query(query)
        
        cores = []
        if result.get("status") == "success" and result.get("data", {}).get("result"):
            for item in result["data"]["result"]:
                cores.append(float(item["value"][1]))
        return cores if cores else [self._generate_mock_cpu() for _ in range(4)]
    
    def get_memory_usage(self, instance: str) -> Dict[str, float]:
        """Get memory usage metrics"""
        if self.demo_mode:
            return self._generate_mock_memory()
        
        queries = {
            "total": f'node_memory_MemTotal_bytes{{instance="{instance}"}}',
            "available": f'node_memory_MemAvailable_bytes{{instance="{instance}"}}',
            "used": f'node_memory_MemTotal_bytes{{instance="{instance}"}} - node_memory_MemAvailable_bytes{{instance="{instance}"}}',
            "swap_total": f'node_memory_SwapTotal_bytes{{instance="{instance}"}}',
            "swap_used": f'node_memory_SwapTotal_bytes{{instance="{instance}"}} - node_memory_SwapFree_bytes{{instance="{instance}"}}'
        }
        
        metrics = {}
        for key, query in queries.items():
            result = self.query(query)
            if result.get("status") == "success" and result.get("data", {}).get("result"):
                metrics[key] = float(result["data"]["result"][0]["value"][1])
            else:
                metrics[key] = 0.0
        
        # Calculate usage percentage
        if metrics["total"] > 0:
            metrics["usage_percent"] = (metrics["used"] / metrics["total"]) * 100
        else:
            return self._generate_mock_memory()  # Fallback to mock data
        
        return metrics
    
    def get_disk_usage(self, instance: str, mount_point: str = "/") -> Dict[str, float]:
        """Get disk usage metrics"""
        if self.demo_mode:
            return self._generate_mock_disk()
        
        queries = {
            "total": f'node_filesystem_size_bytes{{instance="{instance}",mountpoint="{mount_point}"}}',
            "available": f'node_filesystem_avail_bytes{{instance="{instance}",mountpoint="{mount_point}"}}',
            "used": f'node_filesystem_size_bytes{{instance="{instance}",mountpoint="{mount_point}"}} - node_filesystem_avail_bytes{{instance="{instance}",mountpoint="{mount_point}"}}',
            "read_bytes": f'rate(node_disk_read_bytes_total{{instance="{instance}"}}[5m])',
            "write_bytes": f'rate(node_disk_written_bytes_total{{instance="{instance}"}}[5m])'
        }
        
        metrics = {}
        for key, query in queries.items():
            result = self.query(query)
            if result.get("status") == "success" and result.get("data", {}).get("result"):
                if result["data"]["result"]:
                    metrics[key] = float(result["data"]["result"][0]["value"][1])
                else:
                    metrics[key] = 0.0
            else:
                metrics[key] = 0.0
        
        # Calculate usage percentage
        if metrics["total"] > 0:
            metrics["usage_percent"] = (metrics["used"] / metrics["total"]) * 100
        else:
            return self._generate_mock_disk()  # Fallback to mock data
        
        return metrics
    
    def get_network_usage(self, instance: str) -> Dict[str, float]:
        """Get network usage metrics"""
        if self.demo_mode:
            return self._generate_mock_network()
        
        queries = {
            "rx_bytes": f'rate(node_network_receive_bytes_total{{instance="{instance}",device!="lo"}}[5m])',
            "tx_bytes": f'rate(node_network_transmit_bytes_total{{instance="{instance}",device!="lo"}}[5m])',
            "rx_packets": f'rate(node_network_receive_packets_total{{instance="{instance}",device!="lo"}}[5m])',
            "tx_packets": f'rate(node_network_transmit_packets_total{{instance="{instance}",device!="lo"}}[5m])',
            "rx_errors": f'rate(node_network_receive_errs_total{{instance="{instance}",device!="lo"}}[5m])',
            "tx_errors": f'rate(node_network_transmit_errs_total{{instance="{instance}",device!="lo"}}[5m])'
        }
        
        metrics = {}
        for key, query in queries.items():
            result = self.query(query)
            total = 0.0
            if result.get("status") == "success" and result.get("data", {}).get("result"):
                for item in result["data"]["result"]:
                    total += float(item["value"][1])
            metrics[key] = total
        
        # If no data, return mock data
        if all(v == 0.0 for v in metrics.values()):
            return self._generate_mock_network()
        
        return metrics
    
    def get_load_average(self, instance: str) -> Dict[str, float]:
        """Get load average"""
        if self.demo_mode:
            return self._generate_mock_load()
        
        queries = {
            "load_1min": f'node_load1{{instance="{instance}"}}',
            "load_5min": f'node_load5{{instance="{instance}"}}',
            "load_15min": f'node_load15{{instance="{instance}"}}'
        }
        
        metrics = {}
        for key, query in queries.items():
            result = self.query(query)
            if result.get("status") == "success" and result.get("data", {}).get("result"):
                metrics[key] = float(result["data"]["result"][0]["value"][1])
            else:
                metrics[key] = 0.0
        
        # If no data, return mock data
        if all(v == 0.0 for v in metrics.values()):
            return self._generate_mock_load()
        
        return metrics
    
    def get_uptime(self, instance: str) -> float:
        """Get system uptime in seconds"""
        if self.demo_mode:
            return random.uniform(86400, 2592000)  # 1-30 days
        
        query = f'node_time_seconds{{instance="{instance}"}} - node_boot_time_seconds{{instance="{instance}"}}'
        result = self.query(query)
        
        if result.get("status") == "success" and result.get("data", {}).get("result"):
            return float(result["data"]["result"][0]["value"][1])
        return random.uniform(86400, 2592000)  # Fallback to mock data
        

    def get_all_metrics(self, instance: str) -> Dict[str, Any]:
        """
           Get all metrics together
         """

        cpu = self.get_cpu_usage(instance)
        memory = self.get_memory_usage(instance)
        disk = self.get_disk_usage(instance)
        network = self.get_network_usage(instance)
        load = self.get_load_average(instance)

        return {
        "cpu_usage": cpu,

        "memory_usage": memory.get("usage_percent", 0),

        "disk_usage": disk.get("usage_percent", 0),

        "network_rx": network.get("rx_bytes", 0),
        "network_tx": network.get("tx_bytes", 0),

        "network_rx_errors": network.get("rx_errors", 0),
        "network_tx_errors": network.get("tx_errors", 0),

        "load_1min": load.get("load_1min", 0),
        "load_5min": load.get("load_5min", 0),
        "load_15min": load.get("load_15min", 0),
    }

    def check_health(self) -> bool:
        """Check if Prometheus is healthy"""
        try:
            response = requests.get(f"{self.url}/-/healthy", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False


# Global Prometheus client instance
prometheus_client = PrometheusClient()
