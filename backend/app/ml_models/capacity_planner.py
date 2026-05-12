"""
Advanced Capacity Planning & AI Auto-Scaling
"""

import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CapacityPlanner:

    def __init__(self):
        self.thresholds = {
            'cpu_scale_up': 80,
            'memory_scale_up': 85,
            'disk_scale_up': 90,
            'cpu_scale_down': 25,
            'memory_scale_down': 35,
        }

    def analyze_capacity(self, historical_metrics: list, forecast_days: int = 7) -> dict:
        try:
            if len(historical_metrics) < 20:
                return {'status': 'error', 'message': 'Need at least 20 samples'}

            cpu_values = [m.get('cpu_usage', 0) for m in historical_metrics]
            memory_values = [m.get('memory_usage', 0) for m in historical_metrics]
            disk_values = [m.get('disk_usage', 0) for m in historical_metrics]

            cpu_trend = self._calculate_trend(cpu_values)
            memory_trend = self._calculate_trend(memory_values)
            disk_trend = self._calculate_trend(disk_values)

            cpu_projection = np.mean(cpu_values) + (cpu_trend * forecast_days)
            memory_projection = np.mean(memory_values) + (memory_trend * forecast_days)
            disk_projection = np.mean(disk_values) + (disk_trend * forecast_days)

            scaling_needed = (
                cpu_projection > 85
                or memory_projection > 85
                or disk_projection > 90
            )

            return {
                'status': 'success',
                'scaling_needed': scaling_needed,
                'forecast_days': forecast_days,
                'infrastructure_pressure': self._calculate_pressure(
                    cpu_projection, memory_projection, disk_projection
                ),
                'projections': {
                    'cpu': round(cpu_projection, 2),
                    'memory': round(memory_projection, 2),
                    'disk': round(disk_projection, 2),
                },
                'trends': {
                    'cpu': round(cpu_trend, 4),
                    'memory': round(memory_trend, 4),
                    'disk': round(disk_trend, 4),
                },
                'recommendations': self._generate_recommendations(
                    cpu_projection, memory_projection, disk_projection
                ),
                'cost_optimization': self._calculate_cost_optimization(cpu_values, memory_values),
                'analysis_time': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Capacity analysis failed: {e}")
            return {'status': 'error', 'message': str(e)}

    def get_autoscaling_recommendation(
        self,
        current_metrics: dict,
        cpu_prediction: dict | None = None,
        memory_prediction: dict | None = None,
        failure_prediction: dict | None = None,
    ) -> dict:
        try:
            cpu = current_metrics.get('cpu_usage', 0)
            memory = current_metrics.get('memory_usage', 0)

            # Use predictions if available to be proactive
            predicted_cpu = cpu
            predicted_memory = memory

            if cpu_prediction:
                preds = cpu_prediction.get('predictions', [])
                if preds:
                    predicted_cpu = max(p.get('predicted_cpu', cpu) for p in preds)

            if memory_prediction:
                preds = memory_prediction.get('predictions', [])
                if preds:
                    predicted_memory = max(p.get('predicted_memory', memory) for p in preds)

            failure_prob = failure_prediction.get('failure_probability', 0) if failure_prediction else 0

            actions = []
            severity = "normal"

            if predicted_cpu > 85 or predicted_memory > 85 or failure_prob > 0.7:
                severity = "critical"
                actions.append({
                    'action': 'scale_up',
                    'reason': f'Predicted CPU: {predicted_cpu:.1f}%, Memory: {predicted_memory:.1f}%',
                    'recommended_instance': self._recommend_instance_type(predicted_cpu, predicted_memory),
                    'estimated_instances_needed': self._calculate_instances_needed(predicted_cpu, predicted_memory),
                    'urgency': 'immediate',
                })
            elif cpu < self.thresholds['cpu_scale_down'] and memory < self.thresholds['memory_scale_down']:
                severity = "optimization"
                actions.append({
                    'action': 'scale_down',
                    'reason': 'Resources underutilized',
                    'estimated_cost_saving': '30-50%',
                    'urgency': 'consider',
                })
            else:
                actions.append({
                    'action': 'maintain',
                    'reason': 'Infrastructure stable',
                    'urgency': 'none',
                })

            return {
                'status': 'success',
                'severity': severity,
                'actions': actions,
                'predicted_cpu': round(predicted_cpu, 2),
                'predicted_memory': round(predicted_memory, 2),
                'failure_probability': failure_prob,
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Autoscaling recommendation failed: {e}")
            return {'status': 'error', 'message': str(e)}

    def _calculate_trend(self, values: list) -> float:
        if len(values) < 2:
            return 0.0
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        return float(slope)

    def _calculate_pressure(self, cpu: float, memory: float, disk: float) -> str:
        avg = (cpu + memory + disk) / 3
        if avg > 90:
            return "critical"
        if avg > 75:
            return "high"
        if avg > 50:
            return "moderate"
        return "low"

    def _generate_recommendations(self, cpu: float, memory: float, disk: float) -> list[str]:
        recs = []
        if cpu > 85:
            recs.append("Increase compute resources")
        if memory > 85:
            recs.append("Upgrade RAM capacity")
        if disk > 90:
            recs.append("Expand storage immediately")
        if not recs:
            recs.append("Infrastructure capacity is healthy")
        return recs

    def _calculate_cost_optimization(self, cpu_values: list, memory_values: list) -> dict:
        avg_cpu = float(np.mean(cpu_values))
        avg_memory = float(np.mean(memory_values))
        if avg_cpu < 30 and avg_memory < 40:
            return {
                'optimization_possible': True,
                'recommendation': 'Downsize instance type',
                'estimated_savings': '30-50%',
            }
        return {
            'optimization_possible': False,
            'recommendation': 'Current sizing is appropriate',
        }

    def _recommend_instance_type(self, cpu: float, memory: float) -> str:
        pressure = max(cpu, memory)
        if pressure > 95:
            return "c5.2xlarge"
        if pressure > 85:
            return "c5.xlarge"
        if pressure > 70:
            return "t3.large"
        return "Current instance is sufficient"

    def _calculate_instances_needed(self, cpu: float, memory: float) -> int:
        pressure = max(cpu, memory)
        if pressure > 95:
            return 3
        if pressure > 85:
            return 2
        if pressure > 70:
            return 1
        return 0


capacity_planner = CapacityPlanner()
