"""
Memory Usage Forecasting using RandomForest
Production-friendly lightweight forecasting model
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MemoryPredictor:
    """
    Memory prediction + leak detection
    """

    def __init__(self, model_dir='ml_data/models'):
        self.model_dir = model_dir
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.is_trained = False
        os.makedirs(model_dir, exist_ok=True)
        self.model_path = os.path.join(self.model_dir, 'memory_randomforest_model.pkl')

    def prepare_data(self, historical_data):
        """
        Prepare training data with lag features
        """
        df = pd.DataFrame(historical_data)
        if len(df) < 20:
            raise ValueError("Not enough training data (need at least 20 samples)")

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        # Lag features
        df['mem_lag_1'] = df['memory_usage'].shift(1)
        df['mem_lag_2'] = df['memory_usage'].shift(2)
        df['mem_lag_3'] = df['memory_usage'].shift(3)

        # Rolling features
        df['mem_mean_5'] = df['memory_usage'].rolling(5).mean()
        df['mem_mean_10'] = df['memory_usage'].rolling(10).mean()

        # Time features
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute

        df = df.dropna()

        features = [
            'mem_lag_1', 'mem_lag_2', 'mem_lag_3',
            'mem_mean_5', 'mem_mean_10',
            'hour', 'minute'
        ]

        X = df[features]
        y = df['memory_usage']

        return X, y

    def train(self, historical_data):
        """
        Train memory prediction model
        """
        try:
            X, y = self.prepare_data(historical_data)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            self.model.fit(X_train, y_train)
            self.is_trained = True
            joblib.dump(self.model, self.model_path)
            
            logger.info(f"Memory prediction model trained on {len(X)} samples")
            return {'status': 'success', 'samples_trained': len(X)}
        except Exception as e:
            logger.error(f"Memory training failed: {e}")
            return {'status': 'error', 'message': str(e)}

    def predict(self, historical_data=None, minutes_ahead=30):
        """
        Predict future memory usage.
        """
        if not self.is_trained:
            if os.path.exists(self.model_path):
                try:
                    self.model = joblib.load(self.model_path)
                    self.is_trained = True
                except:
                    pass

        if not self.is_trained or not historical_data or len(historical_data) < 10:
            return self._predict_fallback(historical_data, minutes_ahead)

        try:
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            latest = df.tail(10).copy()
            memory_values = latest['memory_usage'].tolist()
            
            predictions = []
            current_time = datetime.now()

            for i in range(minutes_ahead):
                feature_row = pd.DataFrame([{
                    'mem_lag_1': memory_values[-1],
                    'mem_lag_2': memory_values[-2],
                    'mem_lag_3': memory_values[-3],
                    'mem_mean_5': np.mean(memory_values[-5:]),
                    'mem_mean_10': np.mean(memory_values[-10:]),
                    'hour': current_time.hour,
                    'minute': current_time.minute
                }])

                predicted_memory = self.model.predict(feature_row)[0]
                predicted_memory = max(0, min(100, predicted_memory))

                predictions.append({
                    'timestamp': current_time.isoformat(),
                    'predicted_memory': round(float(predicted_memory), 2),
                    'confidence': 0.85
                })

                memory_values.append(predicted_memory)
                current_time += timedelta(minutes=1)

            return {
                'status': 'success',
                'predictions': predictions,
                'source': 'ml'
            }

        except Exception as e:
            logger.error(f"Memory Prediction failed: {e}")
            return self._predict_fallback(historical_data, minutes_ahead)

    def _predict_fallback(self, historical_data, minutes_ahead):
        predictions = []
        current_time = datetime.now()
        
        base_value = 30.0
        if historical_data and len(historical_data) > 0:
            base_value = historical_data[-1].get('memory_usage', base_value)
            
        for i in range(minutes_ahead):
            predictions.append({
                'timestamp': current_time.isoformat(),
                'predicted_memory': round(float(base_value), 2),
                'confidence': 0.5,
                'note': 'rule-based fallback'
            })
            current_time += timedelta(minutes=1)
            
        return {
            'status': 'success',
            'predictions': predictions,
            'source': 'fallback'
        }

    def detect_memory_leak(self, historical_data, threshold=0.3):
        """
        Detect gradual memory increase using linear regression
        """
        try:
            df = pd.DataFrame(historical_data)
            if len(df) < 10:
                return {'status': 'error', 'message': 'Not enough data (need 10+ samples)'}

            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            memory_values = df['memory_usage'].values
            
            x = np.arange(len(memory_values))
            slope, _ = np.polyfit(x, memory_values, 1)
            
            is_leak = slope > threshold
            severity = "normal"
            if slope > 1.0:
                severity = "critical"
            elif slope > 0.5:
                severity = "warning"

            return {
                'status': 'success',
                'is_memory_leak': bool(is_leak),
                'growth_rate': round(float(slope), 4),
                'severity': severity,
                'message': (
                    f"Possible memory leak detected. Growth rate: {slope:.2f}% per min"
                    if is_leak else "Memory usage stable"
                )
            }
        except Exception as e:
            logger.error(f"Memory leak detection failed: {e}")
            return {'status': 'error', 'message': str(e)}

    def save_model(self):
        joblib.dump(self.model, self.model_path)

    def load_model(self):
        try:
            self.model = joblib.load(self.model_path)
            self.is_trained = True
            return True
        except:
            return False


# Global instance
memory_predictor = MemoryPredictor()
