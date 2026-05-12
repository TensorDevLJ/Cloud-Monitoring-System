"""
Infrastructure Failure Prediction Model
Predicts the probability of system failure using a Random Forest Classifier.
"""

from sklearn.ensemble import RandomForestClassifier
import numpy as np
import joblib
import os
import logging

logger = logging.getLogger(__name__)


class FailureModel:

    def __init__(self, model_dir: str = 'ml_data/models'):
        self.model_path = os.path.join(model_dir, 'failure_model.pkl')
        self.model: RandomForestClassifier | None = None
        os.makedirs(model_dir, exist_ok=True)

    def _prepare_data(self, metrics: list) -> tuple[np.ndarray, np.ndarray]:
        X, y = [], []
        for m in metrics:
            X.append([
                m.cpu_usage,
                m.memory_usage,
                m.disk_usage,
                m.load_1min,
            ])
            # Label: failure if high usage detected in history
            if m.cpu_usage > 85 or m.memory_usage > 85:
                y.append(1)
            else:
                y.append(0)
        
        X = np.array(X)
        y = np.array(y)

        # Handle single-class training cases by adding synthetic samples
        if len(set(y)) < 2:
            # Add synthetic failure sample
            X = np.vstack([X, [95.0, 95.0, 90.0, 10.0]])
            y = np.append(y, 1)

        return X, y

    def train(self, metrics: list) -> dict:
        try:
            X, y = self._prepare_data(metrics)
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X, y)
            joblib.dump(self.model, self.model_path)
            logger.info(f"FailureModel trained on {len(X)} samples")
            return {'status': 'trained', 'samples': len(X)}
        except Exception as e:
            logger.error(f"Failure training failed: {e}")
            return {'status': 'error', 'message': str(e)}

    def predict(self, current_metrics: dict) -> dict:
        if self.model is None:
            if not os.path.exists(self.model_path):
                # Fallback: simple heuristic probability
                cpu = current_metrics.get('cpu_usage', 0)
                mem = current_metrics.get('memory_usage', 0)
                prob = 0.0
                if cpu > 90 or mem > 90:
                    prob = 0.85
                elif cpu > 75 or mem > 75:
                    prob = 0.4
                return {
                    "failure_probability": round(prob, 3),
                    "status": "critical" if prob > 0.7 else "normal",
                    "source": "rule_based"
                }
            self.model = joblib.load(self.model_path)

        X = np.array([[
            current_metrics.get('cpu_usage', 0),
            current_metrics.get('memory_usage', 0),
            current_metrics.get('disk_usage', 0),
            current_metrics.get('load_1min', 0)
        ]])
        
        try:
            probs = self.model.predict_proba(X)[0]
            # Handle class mapping safely
            prob = float(probs[1]) if len(probs) > 1 else 0.0
            
            return {
                "failure_probability": round(prob, 3),
                "status": "critical" if prob > 0.7 else "normal",
                "source": "ml"
            }
        except Exception as e:
            logger.error(f"Failure prediction failed: {e}")
            return {"failure_probability": 0.0, "status": "normal", "error": str(e)}


# Global instance
failure_model = FailureModel()