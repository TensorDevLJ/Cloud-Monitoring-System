"""
Advanced Root Cause Analysis Engine
AI + Rule-Based Infrastructure Diagnostics
"""

from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RootCauseAnalyzer:

    def __init__(self):
        self.rules = self._initialize_rules()

    def _initialize_rules(self) -> list[dict]:
        return [
            {
                'name': 'DDoS Attack',
                'severity': 'critical',
                'confidence': 0.90,
                'condition': lambda m: (
                    m.get('network_rx', 0) > 1_000_000_000
                    and m.get('cpu_usage', 0) > 85
                ),
                'recommendation': (
                    'Enable WAF, rate limiting, traffic filtering, and DDoS protection'
                )
            },
            {
                'name': 'Memory Leak',
                'severity': 'high',
                'confidence': 0.85,
                'condition': lambda m: (
                    m.get('memory_usage', 0) > 90
                    and m.get('cpu_usage', 0) < 50
                ),
                'recommendation': (
                    'Investigate application memory allocation and restart affected services'
                )
            },
            {
                'name': 'CPU Bottleneck',
                'severity': 'critical',
                'confidence': 0.92,
                'condition': lambda m: (
                    m.get('cpu_usage', 0) > 92
                    and m.get('load_1min', 0) > 8
                ),
                'recommendation': (
                    'Optimize high CPU processes or scale compute resources'
                )
            },
            {
                'name': 'Disk I/O Saturation',
                'severity': 'high',
                'confidence': 0.80,
                'condition': lambda m: (
                    m.get('disk_usage', 0) > 90
                    or m.get('disk_write_bytes', 0) > 100_000_000
                ),
                'recommendation': (
                    'Upgrade storage performance or clean unnecessary files'
                )
            },
            {
                'name': 'Network Congestion',
                'severity': 'medium',
                'confidence': 0.75,
                'condition': lambda m: (
                    m.get('network_rx_errors', 0) + m.get('network_tx_errors', 0)
                ) > 100,
                'recommendation': (
                    'Inspect bandwidth, packet loss, and network interface configuration'
                )
            },
            {
                'name': 'Infrastructure Overload',
                'severity': 'critical',
                'confidence': 0.88,
                'condition': lambda m: (
                    m.get('cpu_usage', 0)
                    + m.get('memory_usage', 0)
                    + m.get('disk_usage', 0)
                ) / 3 > 85,
                'recommendation': (
                    'Scale infrastructure immediately or distribute workloads'
                )
            },
            {
                'name': 'Application Instability',
                'severity': 'high',
                'confidence': 0.78,
                'condition': lambda m: (
                    m.get('load_5min', 0) > 6
                    and m.get('memory_usage', 0) > 75
                ),
                'recommendation': (
                    'Investigate unstable applications or memory-intensive services'
                )
            },
        ]

    def analyze(
        self,
        metrics: dict,
        anomaly_result: dict | None = None,
        failure_prediction: dict | None = None,
    ) -> dict:
        try:
            identified_causes = []

            for rule in self.rules:
                try:
                    if rule['condition'](metrics):
                        identified_causes.append({
                            'cause': rule['name'],
                            'severity': rule['severity'],
                            'confidence': rule['confidence'],
                            'recommendation': rule['recommendation'],
                        })
                except Exception:
                    continue

            # Enrich with ML anomaly context
            if anomaly_result and anomaly_result.get('is_anomaly'):
                identified_causes.append({
                    'cause': 'ML Detected Behavioral Anomaly',
                    'severity': anomaly_result.get('severity', 'warning'),
                    'confidence': anomaly_result.get('confidence', 0.75),
                    'recommendation': 'Investigate unusual system behavior patterns',
                })

            # Enrich with failure prediction context
            if failure_prediction:
                probability = failure_prediction.get('failure_probability', 0)
                if probability > 0.7:
                    identified_causes.append({
                        'cause': 'Predicted Infrastructure Failure',
                        'severity': 'critical',
                        'confidence': probability,
                        'recommendation': 'Immediate intervention required',
                    })

            identified_causes.sort(key=lambda x: x['confidence'], reverse=True)
            primary_cause = identified_causes[0] if identified_causes else None

            return {
                'status': 'success',
                'infrastructure_state': self._determine_state(identified_causes),
                'identified_causes': identified_causes,
                'primary_cause': primary_cause,
                'summary': self._generate_summary(primary_cause),
                'recommendation_count': len(identified_causes),
                'timestamp': datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Root cause analysis failed: {e}")
            return {'status': 'error', 'message': str(e)}

    def _generate_summary(self, primary_cause: dict | None) -> str:
        if not primary_cause:
            return "No critical infrastructure issues detected"
        return (
            f"Primary issue: {primary_cause['cause']} "
            f"(confidence: {primary_cause['confidence'] * 100:.1f}%)"
        )

    def _determine_state(self, causes: list[dict]) -> str:
        if not causes:
            return "healthy"
        severities = {c['severity'] for c in causes}
        if 'critical' in severities:
            return "critical"
        if 'high' in severities:
            return "warning"
        return "stable"


root_cause_analyzer = RootCauseAnalyzer()
