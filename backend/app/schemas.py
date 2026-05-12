"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: str
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# Instance Schemas
class InstanceBase(BaseModel):
    name: str
    instance_id: str
    ip_address: str
    port: int = 9100
    region: Optional[str] = None
    instance_type: Optional[str] = None


class InstanceCreate(InstanceBase):
    tags: Optional[Dict[str, Any]] = None


class InstanceUpdate(BaseModel):
    name: Optional[str] = None
    is_monitored: Optional[bool] = None
    status: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None


class Instance(InstanceBase):
    id: str
    status: str
    is_monitored: bool
    owner_id: str
    tags: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Metrics Schemas
class CPUMetrics(BaseModel):
    timestamp: float
    usage_percent: float
    per_core: Optional[List[float]] = None
    load_1min: float
    load_5min: float
    load_15min: float


class MemoryMetrics(BaseModel):
    timestamp: float
    total_bytes: float
    used_bytes: float
    available_bytes: float
    usage_percent: float
    swap_total: float
    swap_used: float


class DiskMetrics(BaseModel):
    timestamp: float
    total_bytes: float
    used_bytes: float
    available_bytes: float
    usage_percent: float
    read_bytes: float
    write_bytes: float


class NetworkMetrics(BaseModel):
    timestamp: float
    rx_bytes: float
    tx_bytes: float
    rx_packets: float
    tx_packets: float
    rx_errors: float
    tx_errors: float


class SystemMetrics(BaseModel):
    cpu: CPUMetrics
    memory: MemoryMetrics
    disk: DiskMetrics
    network: NetworkMetrics
    uptime_seconds: float


# Alert Schemas
class AlertBase(BaseModel):
    alert_type: str
    metric_name: str
    threshold_value: float
    current_value: float
    severity: str
    message: str


class AlertCreate(AlertBase):
    instance_id: str


class Alert(AlertBase):
    id: str
    instance_id: str
    status: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertConfigBase(BaseModel):
    alert_type: str
    threshold: float
    duration_minutes: int = 5
    notification_email: Optional[str] = None


class AlertConfigCreate(AlertConfigBase):
    pass


class AlertConfig(AlertConfigBase):
    id: str
    user_id: str
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Response Schemas
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]


class MetricsResponse(BaseModel):
    instance_id: str
    instance_name: str
    metrics: SystemMetrics
    timestamp: datetime


class DashboardSummary(BaseModel):
    total_instances: int
    active_instances: int
    total_alerts: int
    critical_alerts: int
    average_cpu: float
    average_memory: float
    average_disk: float
