"""
Beanie database models (MongoDB ODM)
"""
from typing import Optional, Dict, Any
from datetime import datetime
# pyrefly: ignore [missing-import]
from beanie import Document, Indexed
# pyrefly: ignore [missing-import]
from pydantic import Field

class User(Document):
    """User model for authentication"""
    # pyrefly: ignore [invalid-annotation]
    email: Indexed(str, unique=True)
    # pyrefly: ignore [invalid-annotation]
    username: Indexed(str, unique=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "users"

class Instance(Document):
    """Instance model"""
    name: str
    # pyrefly: ignore [invalid-annotation]
    instance_id: Indexed(str, unique=True)
    ip_address: str
    port: int = 9100
    region: Optional[str] = None
    instance_type: Optional[str] = None
    status: str = "active"
    is_monitored: bool = True
    owner_id: str  # Storing the string ID of the User
    tags: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "instances"

class Alert(Document):
    """Alert model"""
    instance_id: str  # string ID of Instance
    alert_type: str
    metric_name: str
    threshold_value: float
    current_value: float
    severity: str
    message: str
    status: str = "active"
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

    class Settings:
        name = "alerts"

class AlertConfig(Document):
    """Alert Configuration"""
    user_id: str  # string ID of User
    alert_type: str
    threshold: float
    duration_minutes: int = 5
    enabled: bool = True
    notification_email: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "alert_configs"

class MetricsSnapshot(Document):
    """
    Metrics snapshot for ML training - Stores historical metrics data
    """
    instance_id: str  # string ID of Instance
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_rx: float
    network_tx: float
    network_rx_errors: float = 0
    network_tx_errors: float = 0
    disk_read_bytes: float = 0
    disk_write_bytes: float = 0
    load_1min: float
    load_5min: float
    load_15min: float

    class Settings:
        name = "metrics_snapshots"
