# pyrefly: ignore [missing-import]
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# pyrefly: ignore [missing-import]
from app import models
# pyrefly: ignore [missing-import]
from app.services.prometheus import prometheus_client
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def collect_metrics_job():
    """
    Collect metrics every minute automatically
    """
    try:
        instances = await models.Instance.find(
            models.Instance.is_monitored == True  # noqa: E712
        ).to_list()

        logger.info(f"Collecting metrics for {len(instances)} instances")

        for instance in instances:

            metrics = prometheus_client.get_all_metrics(
                instance.ip_address,
            )

            snapshot = models.MetricsSnapshot(
                instance_id=str(instance.id),
                cpu_usage=metrics.get("cpu_usage", 0),
                memory_usage=metrics.get("memory_usage", 0),
                disk_usage=metrics.get("disk_usage", 0),
                network_rx=metrics.get("network_rx", 0),
                network_tx=metrics.get("network_tx", 0),
                network_rx_errors=metrics.get("network_rx_errors", 0),
                network_tx_errors=metrics.get("network_tx_errors", 0),
                load_1min=metrics.get("load_1min", 0),
                load_5min=metrics.get("load_5min", 0),
                load_15min=metrics.get("load_15min", 0),
            )

            await snapshot.insert()

        logger.info(f"Metrics collected successfully at {datetime.now()}")

    except Exception as e:
        logger.error(f"Scheduler error: {e}")


def start_scheduler():

    scheduler.add_job(
        collect_metrics_job,
        trigger='interval',
        minutes=1,
        id='metrics_collector',
        replace_existing=True
    )

    scheduler.start()

    logger.info("Metrics scheduler started")