
# /services/alerting.py   

"""
Alert management and notification service
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from datetime import datetime
from app.config import settings
from app import models
import logging

logger = logging.getLogger(__name__)


class AlertService:
    """Service for managing alerts and notifications"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.ALERT_EMAIL_FROM
        self.email_to = settings.ALERT_EMAIL_TO
    
    def send_email_alert(self, subject: str, body: str, to_email: str = None):
        """Send email alert"""
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured, skipping email")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = to_email or self.email_to
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.email_from, msg['To'], text)
            server.quit()
            
            logger.info(f"Alert email sent to {msg['To']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    async def check_cpu_threshold(self, instance: models.Instance, cpu_usage: float):
        """Check if CPU usage exceeds threshold"""
        threshold = settings.CPU_THRESHOLD
        
        if cpu_usage > threshold:
            # Check if alert already exists
            existing_alert = await models.Alert.find_one(
                models.Alert.instance_id == str(instance.id),
                models.Alert.alert_type == "cpu",
                models.Alert.status == "active"
            )
            
            if not existing_alert:
                # Create new alert
                alert = models.Alert(
                    instance_id=str(instance.id),
                    alert_type="cpu",
                    metric_name="CPU Usage",
                    threshold_value=threshold,
                    current_value=cpu_usage,
                    severity="critical" if cpu_usage > 90 else "warning",
                    message=f"CPU usage on {instance.name} is {cpu_usage:.2f}%"
                )
                await alert.insert()
                
                # Send email notification
                self._send_alert_notification(instance, alert)
                
                return alert
        else:
            # Resolve existing alerts
            await self._resolve_alerts(str(instance.id), "cpu")
        
        return None
    
    async def check_memory_threshold(self, instance: models.Instance, memory_usage: float):
        """Check if memory usage exceeds threshold"""
        threshold = settings.MEMORY_THRESHOLD
        
        if memory_usage > threshold:
            existing_alert = await models.Alert.find_one(
                models.Alert.instance_id == str(instance.id),
                models.Alert.alert_type == "memory",
                models.Alert.status == "active"
            )
            
            if not existing_alert:
                alert = models.Alert(
                    instance_id=str(instance.id),
                    alert_type="memory",
                    metric_name="Memory Usage",
                    threshold_value=threshold,
                    current_value=memory_usage,
                    severity="critical" if memory_usage > 95 else "warning",
                    message=f"Memory usage on {instance.name} is {memory_usage:.2f}%"
                )
                await alert.insert()
                
                self._send_alert_notification(instance, alert)
                
                return alert
        else:
            await self._resolve_alerts(str(instance.id), "memory")
        
        return None
    
    async def check_disk_threshold(self, instance: models.Instance, disk_usage: float):
        """Check if disk usage exceeds threshold"""
        threshold = settings.DISK_THRESHOLD
        
        if disk_usage > threshold:
            existing_alert = await models.Alert.find_one(
                models.Alert.instance_id == str(instance.id),
                models.Alert.alert_type == "disk",
                models.Alert.status == "active"
            )
            
            if not existing_alert:
                alert = models.Alert(
                    instance_id=str(instance.id),
                    alert_type="disk",
                    metric_name="Disk Usage",
                    threshold_value=threshold,
                    current_value=disk_usage,
                    severity="critical" if disk_usage > 95 else "warning",
                    message=f"Disk usage on {instance.name} is {disk_usage:.2f}%"
                )
                await alert.insert()
                
                self._send_alert_notification(instance, alert)
                
                return alert
        else:
            await self._resolve_alerts(str(instance.id), "disk")
        
        return None
    
    async def _resolve_alerts(self, instance_id: str, alert_type: str):
        """Resolve active alerts of a specific type"""
        alerts = await models.Alert.find(
            models.Alert.instance_id == instance_id,
            models.Alert.alert_type == alert_type,
            models.Alert.status == "active"
        ).to_list()
        
        for alert in alerts:
            alert.status = "resolved"
            alert.resolved_at = datetime.utcnow()
            await alert.save()
    
    def _send_alert_notification(self, instance: models.Instance, alert: models.Alert):
        """Send notification for alert"""
        subject = f"🚨 Alert: {alert.metric_name} - {instance.name}"
        
        body = f"""
        <html>
        <body>
            <h2>System Alert Triggered</h2>
            <p><strong>Instance:</strong> {instance.name} ({instance.instance_id})</p>
            <p><strong>Alert Type:</strong> {alert.alert_type.upper()}</p>
            <p><strong>Metric:</strong> {alert.metric_name}</p>
            <p><strong>Current Value:</strong> {alert.current_value:.2f}%</p>
            <p><strong>Threshold:</strong> {alert.threshold_value:.2f}%</p>
            <p><strong>Severity:</strong> {alert.severity.upper()}</p>
            <p><strong>Time:</strong> {alert.triggered_at}</p>
            <p><strong>Message:</strong> {alert.message}</p>
            <hr>
            <p>Please take necessary action to resolve this issue.</p>
        </body>
        </html>
        """
        
        self.send_email_alert(subject, body)
    
    async def get_active_alerts(self, instance_id: str = None) -> List[models.Alert]:
        """Get active alerts"""
        query = models.Alert.find(models.Alert.status == "active")
        
        if instance_id:
            query = query.find(models.Alert.instance_id == instance_id)
        
        return await query.sort(-models.Alert.triggered_at).to_list()


# Global alert service instance
alert_service = AlertService()

