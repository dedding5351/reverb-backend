from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.tasks.pipeline import run_pipeline
from app.tasks.generate_embeddings import generate_embeddings
import logging
import asyncio

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        
    async def run_daily_ingestion(self):
        """
        Runs the daily ingestion pipeline followed by embedding generation.
        """
        logger.info("Starting Daily Ingestion Task...")
        try:
             # Run pipeline (sync function, might need to run in executor if blocking)
             # run_pipeline is sync, but extensive IO. Better to run in thread pool
             loop = asyncio.get_running_loop()
             await loop.run_in_executor(None, run_pipeline)
             
             # Run embeddings (async)
             await generate_embeddings()
             
             logger.info("Daily Ingestion Task Completed Successfully.")
        except Exception as e:
            logger.error(f"Daily Ingestion Task Failed: {e}")

    def start(self):
        # Schedule to run daily at 00:00 PST (America/Los_Angeles)
        # We need to configure timezone. APScheduler supports it.
        # If timezone not found, install pytz or tzdata, but zoneinfo standard in 3.9+
        
        self.scheduler.add_job(
            self.run_daily_ingestion, 
            'cron', 
            hour=0, 
            minute=0, 
            timezone='America/Los_Angeles',
            id='daily_ingestion',
            replace_existing=True
        )
        self.scheduler.start()
        logger.info("Scheduler started. Daily ingestion scheduled for 00:00 PST.")

scheduler_service = SchedulerService()
