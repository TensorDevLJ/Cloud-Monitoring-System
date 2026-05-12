"""
Instance Health Scoring Model
Computes a 0-100 health score using a Random Forest Regressor
trained on historical metrics snapshots.
"""

from sklearn.ensemble import RandomForestRegressor
import numpy as np
import joblib
import os
import logging

logger = logging.getLogger(__name__)


class HealthModel:

    FEATURES = ['cpu_usage', 'memory_usage', 'disk_usage', 'network_rx', 'network_tx', 'load_1min']

    def __init__(self, model_dir: str = 'ml_data/models'):
        self.model_path = os.path.join(model_dir, 'health_model.pkl')
        self.model: RandomForestRegressor | None = None
        os.makedirs(model_dir, exist_ok=True)

    def _prepare_data(self, metrics: list) -> tuple[np.ndarray, np.ndarray]:
        X, y = [], []
        for m in metrics:
            X.append([
                m.cpu_usage,
                m.memory_usage,
                m.disk_usage,
                m.network_rx,
                m.network_tx,
                m.load_1min,
            ])
            # Heuristic health label: high usage = low health
            score = 100 - (
                m.cpu_usage * 0.3
                + m.memory_usage * 0.3
                + m.disk_usage * 0.2
                + m.load_1min * 5
            )
            y.append(max(0.0, min(100.0, score)))
        return np.array(X), np.array(y)

    def train(self, metrics: list) -> dict:
        X, y = self._prepare_data(metrics)
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        joblib.dump(self.model, self.model_path)
        logger.info(f"HealthModel trained on {len(X)} samples")
        return {'status': 'trained', 'samples': len(X)}

    def predict(self, current_metrics: dict) -> dict:
        if self.model is None:
            if not os.path.exists(self.model_path):
                # Fallback: rule-based score when no model trained yet
                cpu = current_metrics.get('cpu_usage', 0)
                mem = current_metrics.get('memory_usage', 0)
                disk = current_metrics.get('disk_usage', 0)
                load = current_metrics.get('load_1min', 0)
                score = max(0.0, min(100.0, 100 - (cpu * 0.3 + mem * 0.3 + disk * 0.2 + load * 5)))
                return {'health_score': round(score, 2), 'source': 'rule_based'}
            self.model = joblib.load(self.model_path)

        X = np.array([[
            current_metrics.get('cpu_usage', 0),
            current_metrics.get('memory_usage', 0),
            current_metrics.get('disk_usage', 0),
            current_metrics.get('network_rx', 0),
            current_metrics.get('network_tx', 0),
            current_metrics.get('load_1min', 0),
        ]])
        score = float(self.model.predict(X)[0])
        return {'health_score': round(score, 2), 'source': 'ml'}


health_model = HealthModel()