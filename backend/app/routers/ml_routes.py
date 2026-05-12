"""
ML-Enhanced API Routes   ml_routes.py
"""

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime, timedelta
# pyrefly: ignore [missing-import]
from app import models, auth
# pyrefly: ignore [missing-import]
from app.ml_models.anomaly_detector import anomaly_detector
# pyrefly: ignore [missing-import]
from app.ml_models.cpu_predictor import cpu_predictor
# pyrefly: ignore [missing-import]
from app.ml_models.memory_predictor import memory_predictor
# pyrefly: ignore [missing-import]
from app.ml_models.root_cause_analyzer import root_cause_analyzer
# pyrefly: ignore [missing-import]
from app.ml_models.capacity_planner import capacity_planner
# pyrefly: ignore [missing-import]
from app.services.prometheus import prometheus_client
# pyrefly: ignore [missing-import]
from app.ml_models.health_model import health_model
# pyrefly: ignore [missing-import]
from app.ml_models.failure_model import failure_model
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

async def get_instance_by_id(instance_id: str):
    instance = await models.Instance.find_one(models.Instance.instance_id == instance_id)
    if not instance:
        try:
            # pyrefly: ignore [missing-import]
            from bson import ObjectId
            if ObjectId.is_valid(instance_id):
                instance = await models.Instance.get(instance_id)
        except Exception:
            pass
    return instance

@router.post("/anomaly/train/{instance_id}")
async def train_anomaly_detector(
    instance_id: str,
    current_user: Optional[models.User] = Depends(auth.get_optional_current_user)
):
    """Train anomaly detection model for an instance"""
    instance = await get_instance_by_id(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Get historical metrics (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    historical_data = await models.MetricsSnapshot.find(
        models.MetricsSnapshot.instance_id == str(instance.id),
        models.MetricsSnapshot.timestamp >= seven_days_ago
    ).to_list()
    
    if len(historical_data) < 100:
        raise HTTPException(status_code=400, detail="Insufficient historical data (need at least 100 samples)")
    
    # Prepare training data
    training_data = [{
        'cpu_usage': m.cpu_usage,
        'memory_usage': m.memory_usage,
        'disk_usage': m.disk_usage,
        'network_rx': m.network_rx,
        'network_tx': m.network_tx,
        'load_1min': m.load_1min,
        'load_5min': m.load_5min,
        'load_15min': m.load_15min
    } for m in historical_data]
    
    # Train model
    result = anomaly_detector.train(training_data)
    
    return {
        **result,
        'instance_id': instance.instance_id,
        'instance_name': instance.name
    }


@router.get("/anomaly/detect/{instance_id}")
async def detect_anomaly(
    instance_id: str,
    current_user: Optional[models.User] = Depends(auth.get_optional_current_user)
):
    """Detect anomalies in current metrics"""
    instance = await get_instance_by_id(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Get current metrics from Prometheus
    target = f"{instance.ip_address}:{instance.port}"
    cpu_usage = prometheus_client.get_cpu_usage(target)
    memory_metrics = prometheus_client.get_memory_usage(target)
    disk_metrics = prometheus_client.get_disk_usage(target)
    network_metrics = prometheus_client.get_network_usage(target)
    load_avg = prometheus_client.get_load_average(target)
    
    current_metrics = {
        'cpu_usage': cpu_usage,
        'memory_usage': memory_metrics.get('usage_percent', 0),
        'disk_usage': disk_metrics.get('usage_percent', 0),
        'network_rx': network_metrics.get('rx_bytes', 0),
        'network_tx': network_metrics.get('tx_bytes', 0),
        'load_1min': load_avg.get('load_1min', 0),
        'load_5min': load_avg.get('load_5min', 0),
        'load_15min': load_avg.get('load_15min', 0)
    }
    
    # Detect anomaly
    result = anomaly_detector.detect(current_metrics)
    
    return {
        **result,
        'instance_id': instance.instance_id,
        'instance_name': instance.name,
        'current_metrics': current_metrics
    }


@router.post("/cpu/train/{instance_id}")
async def train_cpu_predictor(
    instance_id: str,
    current_user: Optional[models.User] = Depends(auth.get_optional_current_user)
):
    """Train CPU prediction model"""
    instance = await get_instance_by_id(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Get historical data
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    historical_data = await models.MetricsSnapshot.find(
        models.MetricsSnapshot.instance_id == str(instance.id),
        models.MetricsSnapshot.timestamp >= seven_days_ago
    ).to_list()
    
    if len(historical_data) < 100:
        raise HTTPException(status_code=400, detail="Insufficient data")
    
    training_data = [{
        'timestamp': m.timestamp,
        'cpu_usage': m.cpu_usage
    } for m in historical_data]
    
    result = cpu_predictor.train(training_data)
    return result


@router.get("/cpu/predict/{instance_id}")
async def predict_cpu(
    instance_id: str,
    minutes: int = 30,
    current_user: Optional[models.User] = Depends(auth.get_optional_current_user)
):
    """Predict CPU usage for next N minutes"""
    instance = await get_instance_by_id(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    predictions = cpu_predictor.predict(minutes_ahead=minutes)
    
    return {
        **predictions,
        'instance_id': instance.instance_id,
        'instance_name': instance.name
    }


@router.post("/memory/train/{instance_id}")
async def train_memory_predictor(
    instance_id: str,
    current_user: Optional[models.User] = Depends(auth.get_optional_current_user)
):
    """Train memory prediction model"""
    instance = await get_instance_by_id(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    historical_data = await models.MetricsSnapshot.find(
        models.MetricsSnapshot.instance_id == str(instance.id),
        models.MetricsSnapshot.timestamp >= seven_days_ago
    ).to_list()
    
    if len(historical_data) < 100:
        raise HTTPException(status_code=400, detail="Insufficient data")
    
    training_data = [{
        'timestamp': m.timestamp,
        'memory_usage': m.memory_usage
    } for m in historical_data]
    
    result = memory_predictor.train(training_data)
    return result


@router.get("/memory/predict/{instance_id}")
async def predict_memory(
    instance_id: str,
    minutes: int = 30,
    current_user: Optional[models.User] = Depends(auth.get_optional_current_user)
):
    """Predict memory usage"""
    instance = await get_instance_by_id(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    predictions = memory_predictor.predict(minutes_ahead=minutes)
    
    return {
        **predictions,
        'instance_id': instance.instance_id,
        'instance_name': instance.name
    }


@router.get("/memory/leak-detection/{instance_id}")
async def detect_memory_leak(
    instance_id: str,
    current_user: Optional[models.User] = Depends(auth.get_optional_current_user)
):
    """Detect memory leaks"""
    instance = await get_instance_by_id(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Get recent data (last 24 hours)
    one_day_ago = datetime.utcnow() - timedelta(hours=24)
    historical_data = await models.MetricsSnapshot.find(
        models.MetricsSnapshot.instance_id == str(instance.id),
        models.MetricsSnapshot.timestamp >= one_day_ago
    ).to_list()
    
    if len(historical_data) < 10:
        raise HTTPException(status_code=400, detail="Insufficient data")
    
    data = [{'timestamp': m.timestamp, 'memory_usage': m.memory_usage} for m in historical_data]
    result = memory_predictor.detect_memory_leak(data)
    
    return {
        **result,
        'instance_id': instance.instance_id,
        'instance_name': instance.name
    }



@router.get("/health-score/{instance_id}")
async def get_health_score(
    instance_id: str
):
    instance = await get_instance_by_id(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")

    historical_data = await models.MetricsSnapshot.find(
        models.MetricsSnapshot.instance_id == str(instance.id)
    ).to_list()

    if len(historical_data) < 50:
        raise HTTPException(status_code=400, detail="Not enough data for ML")

    target = f"{instance.ip_address}:{instance.port}"

    current_metrics = {
        'cpu_usage': prometheus_client.get_cpu_usage(target),
        'memory_usage': prometheus_client.get_memory_usage(target).get('usage_percent', 0),
        'disk_usage': prometheus_client.get_disk_usage(target).get('usage_percent', 0),
        'network_rx': prometheus_client.get_network_usage(target).get('rx_bytes', 0),
        'network_tx': prometheus_client.get_network_usage(target).get('tx_bytes', 0),
        'load_1min': prometheus_client.get_load_average(target).get('load_1min', 0)
    }

    health_model.train(historical_data)
    result = health_model.predict(current_metrics)

    return {
        "instanceId": instance.instance_id,
        "healthScore": result.get("health_score", 0)
    }

@router.get("/failure/predict/{instance_id}")
async def predict_failure(
    instance_id: str,
    current_user: Optional[models.User] = Depends(auth.get_optional_current_user)
):
    """Predict system failure"""
    instance = await get_instance_by_id(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")

    target = f"{instance.ip_address}:{instance.port}"

    cpu_usage = prometheus_client.get_cpu_usage(target)
    memory_metrics = prometheus_client.get_memory_usage(target)
    disk_metrics = prometheus_client.get_disk_usage(target)
    network_metrics = prometheus_client.get_network_usage(target)
    load_avg = prometheus_client.get_load_average(target)

    current_metrics = {
        'cpu_usage': cpu_usage,
        'memory_usage': memory_metrics.get('usage_percent', 0),
        'disk_usage': disk_metrics.get('usage_percent', 0),
        'load_1min': load_avg.get('load_1min', 0),
        'load_5min': load_avg.get('load_5min', 0),
        'network_rx_errors': network_metrics.get('rx_errors', 0),
        'network_tx_errors': network_metrics.get('tx_errors', 0)
    }

    historical_data = await models.MetricsSnapshot.find(
        models.MetricsSnapshot.instance_id == str(instance.id)
    ).to_list()

    if len(historical_data) < 50:
        raise HTTPException(status_code=400, detail="Not enough data for ML")

    failure_model.train(historical_data)
    result = failure_model.predict(current_metrics)

    return {
        "instanceId": instance.instance_id,
        "instanceName": instance.name,
        "failureProbability": result.get("failure_probability", 0),
        "status": result.get("status", "normal")
    }

@router.get("/autoscale/recommend/{instance_id}")
async def get_autoscale_recommendation(
    instance_id: str,
    current_user: Optional[models.User] = Depends(auth.get_optional_current_user)
):
    """Get auto-scaling recommendations"""
    instance = await get_instance_by_id(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    target = f"{instance.ip_address}:{instance.port}"
    cpu_usage = prometheus_client.get_cpu_usage(target)
    memory_metrics = prometheus_client.get_memory_usage(target)
    
    current_metrics = {
        'cpu_usage': cpu_usage,
        'memory_usage': memory_metrics.get('usage_percent', 0)
    }
    
    result = capacity_planner.get_autoscaling_recommendation(current_metrics)
    
    return {
        **result,
        'instance_id': instance.instance_id,
        'instance_name': instance.name
    }


@router.get("/dashboard/ml-summary/{instance_id}")
async def get_ml_dashboard_summary(
    instance_id: str,
    current_user: Optional[models.User] = Depends(auth.get_optional_current_user)
):
    """Get comprehensive ML analysis for dashboard"""
    instance = await get_instance_by_id(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    target = f"{instance.ip_address}:{instance.port}"
    cpu_usage = prometheus_client.get_cpu_usage(target)
    memory_metrics = prometheus_client.get_memory_usage(target)
    disk_metrics = prometheus_client.get_disk_usage(target)
    network_metrics = prometheus_client.get_network_usage(target)
    load_avg = prometheus_client.get_load_average(target)
    
    metrics = {
        'cpu_usage': cpu_usage,
        'memory_usage': memory_metrics.get('usage_percent', 0),
        'disk_usage': disk_metrics.get('usage_percent', 0),
        'network_rx': network_metrics.get('rx_bytes', 0),
        'network_tx': network_metrics.get('tx_bytes', 0),
        'network_rx_errors': network_metrics.get('rx_errors', 0),
        'network_tx_errors': network_metrics.get('tx_errors', 0),
        'disk_write_bytes': disk_metrics.get('write_bytes', 0),
        'load_1min': load_avg.get('load_1min', 0),
        'load_5min': load_avg.get('load_5min', 0),
        'cpu_count': 4
    }
    
    anomaly = anomaly_detector.detect(metrics)
    historical_data = await models.MetricsSnapshot.find(
          models.MetricsSnapshot.instance_id == str(instance.id)
    ).to_list()

    if len(historical_data) >= 50:
         health_model.train(historical_data)
         failure_model.train(historical_data)
         health = health_model.predict(metrics)
         failure = failure_model.predict(metrics)
    else:
        health = {
            "health_score": 50,
            "status": "insufficient_data"
        }
        failure = {
            "failure_probability": 0,
            "status": "insufficient_data"
        }

    root_cause = root_cause_analyzer.analyze(metrics)
    autoscale = capacity_planner.get_autoscaling_recommendation(metrics)
    
    try:
        cpu_pred = cpu_predictor.predict(minutes_ahead=30)
        memory_pred = memory_predictor.predict(minutes_ahead=30)
    except Exception:
        cpu_pred = {'predictions': []}
        memory_pred = {'predictions': []}
    
    return {
        'instanceId': instance.instance_id,
        'instanceName': instance.name,
        'healthScore': health.get('health_score', 0),
        'failureProbability': failure.get('failure_probability', 0),
        'failureStatus': failure.get('status', 'normal'),
        'anomaly': anomaly.get('is_anomaly', False),
        'cpuPrediction': cpu_pred.get('predictions', [])[:10],
        'memoryPrediction': memory_pred.get('predictions', [])[:10],
        'rootCause': root_cause,
        'autoscale': autoscale,
        'timestamp': datetime.now().isoformat()
    }
