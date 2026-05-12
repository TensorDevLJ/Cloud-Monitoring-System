"""
CPU Usage Prediction using RandomForestRegressor
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


class CPUPredictor:
    """
    CPU usage prediction using RandomForestRegressor
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
        self.model_path = os.path.join(self.model_dir, 'cpu_randomforest_model.pkl')

    def prepare_data(self, historical_data):
        """
        Prepare training data with lag features
        """
        df = pd.DataFrame(historical_data)
        if len(df) < 20:
            raise ValueError("Not enough historical data (need at least 20 samples)")

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        # Create lag features
        df['cpu_lag_1'] = df['cpu_usage'].shift(1)
        df['cpu_lag_2'] = df['cpu_usage'].shift(2)
        df['cpu_lag_3'] = df['cpu_usage'].shift(3)

        # Rolling averages
        df['cpu_mean_5'] = df['cpu_usage'].rolling(window=5).mean()
        df['cpu_mean_10'] = df['cpu_usage'].rolling(window=10).mean()

        # Time features
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute

        df = df.dropna()

        features = [
            'cpu_lag_1', 'cpu_lag_2', 'cpu_lag_3',
            'cpu_mean_5', 'cpu_mean_10',
            'hour', 'minute'
        ]

        X = df[features]
        y = df['cpu_usage']

        return X, y

    def train(self, historical_data):
        """
        Train CPU prediction model
        """
        try:
            X, y = self.prepare_data(historical_data)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            self.model.fit(X_train, y_train)
            self.is_trained = True
            joblib.dump(self.model, self.model_path)
            
            logger.info(f"CPU prediction model trained on {len(X)} samples")
            return {'status': 'success', 'samples_trained': len(X)}
        except Exception as e:
            logger.error(f"CPU training failed: {e}")
            return {'status': 'error', 'message': str(e)}

    def predict(self, historical_data=None, minutes_ahead=30):
        """
        Predict future CPU usage. 
        If historical_data is missing or model not trained, returns rule-based projection.
        """
        if not self.is_trained:
            if os.path.exists(self.model_path):
                try:
                    self.model = joblib.load(self.model_path)
                    self.is_trained = True
                except:
                    pass

        # Fallback if no model or no data
        if not self.is_trained or not historical_data or len(historical_data) < 10:
            return self._predict_fallback(historical_data, minutes_ahead)

        try:
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # We need at least the last 10 samples to generate features
            latest = df.tail(10).copy()
            cpu_values = latest['cpu_usage'].tolist()
            
            predictions = []
            current_time = datetime.now()

            for i in range(minutes_ahead):
                feature_row = pd.DataFrame([{
                    'cpu_lag_1': cpu_values[-1],
                    'cpu_lag_2': cpu_values[-2],
                    'cpu_lag_3': cpu_values[-3],
                    'cpu_mean_5': np.mean(cpu_values[-5:]),
                    'cpu_mean_10': np.mean(cpu_values[-10:]),
                    'hour': current_time.hour,
                    'minute': current_time.minute
                }])

                predicted_cpu = self.model.predict(feature_row)[0]
                predicted_cpu = max(0, min(100, predicted_cpu))

                predictions.append({
                    'timestamp': current_time.isoformat(),
                    'predicted_cpu': round(float(predicted_cpu), 2),
                    'confidence': 0.85
                })

                cpu_values.append(predicted_cpu)
                current_time += timedelta(minutes=1)

            return {
                'status': 'success',
                'predictions': predictions,
                'source': 'ml'
            }

        except Exception as e:
            logger.error(f"CPU Prediction failed: {e}")
            return self._predict_fallback(historical_data, minutes_ahead)

    def _predict_fallback(self, historical_data, minutes_ahead):
        """Simple linear projection or flat line if no data"""
        predictions = []
        current_time = datetime.now()
        
        base_value = 20.0
        if historical_data and len(historical_data) > 0:
            base_value = historical_data[-1].get('cpu_usage', base_value)
            
        for i in range(minutes_ahead):
            predictions.append({
                'timestamp': current_time.isoformat(),
                'predicted_cpu': round(float(base_value), 2),
                'confidence': 0.5,
                'note': 'rule-based fallback'
            })
            current_time += timedelta(minutes=1)
            
        return {
            'status': 'success',
            'predictions': predictions,
            'source': 'fallback'
        }


# Global instance
cpu_predictor = CPUPredictor()
