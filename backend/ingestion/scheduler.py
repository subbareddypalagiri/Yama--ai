"""
YAMA AI — Ingestion Scheduler
Manages periodic crawl execution using threading-based scheduling.

For production, use:
    - Celery + Redis for distributed task queues
    - OS cron jobs for simple periodic execution

This module provides a lightweight in-process scheduler
suitable for development and single-server deployment.

Usage:
    from ingestion.scheduler import IngestionScheduler
    scheduler = IngestionScheduler()
    scheduler.start()   # starts background thread
    scheduler.stop()    # stops gracefully
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional

logger = logging.getLogger("yama_ai.ingestion.scheduler")


class ScheduledTask:
    """A task that runs on a schedule."""

    def __init__(
        self,
        name: str,
        func: Callable,
        interval_hours: float = 168,  # default: weekly
        enabled: bool = True,
    ):
        self.name = name
        self.func = func
        self.interval = timedelta(hours=interval_hours)
        self.enabled = enabled
        self.last_run: Optional[datetime] = None
        self.next_run: datetime = datetime.utcnow()
        self.run_count: int = 0
        self.last_error: Optional[str] = None

    @property
    def is_due(self) -> bool:
        return self.enabled and datetime.utcnow() >= self.next_run

    def execute(self):
        """Run the task and update scheduling metadata."""
        try:
            logger.info(f"[Scheduler] Running task: {self.name}")
            self.func()
            self.last_run = datetime.utcnow()
            self.next_run = self.last_run + self.interval
            self.run_count += 1
            self.last_error = None
            logger.info(f"[Scheduler] Task '{self.name}' completed. Next run: {self.next_run}")
        except Exception as e:
            self.last_error = str(e)
            # Retry after a shorter interval on failure
            self.next_run = datetime.utcnow() + timedelta(hours=1)
            logger.error(f"[Scheduler] Task '{self.name}' failed: {e}. Retrying in 1 hour.")


class IngestionScheduler:
    """
    Lightweight background scheduler for ingestion tasks.

    In development: runs in a background thread.
    In production: replace with Celery Beat or OS cron.
    """

    def __init__(self):
        self.tasks: List[ScheduledTask] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._setup_default_tasks()

    def _setup_default_tasks(self):
        """Register default crawl tasks."""
        self.add_task("india_code_crawl", self._run_india_code, interval_hours=168)      # Weekly
        self.add_task("constitution_crawl", self._run_constitution, interval_hours=720)  # Monthly
        self.add_task("court_judgments_crawl", self._run_courts, interval_hours=24)      # Daily
        self.add_task("gazette_crawl", self._run_gazette, interval_hours=24)             # Daily
        self.add_task("state_laws_crawl", self._run_state_laws, interval_hours=168)      # Weekly

    def add_task(self, name: str, func: Callable, interval_hours: float = 168, enabled: bool = True):
        """Register a new scheduled task."""
        self.tasks.append(ScheduledTask(name, func, interval_hours, enabled))
        logger.info(f"[Scheduler] Registered task: {name} (every {interval_hours}h)")

    def start(self):
        """Start the scheduler in a background thread."""
        if self._running:
            logger.warning("[Scheduler] Already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="ingestion-scheduler")
        self._thread.start()
        logger.info("[Scheduler] Started background scheduler")

    def stop(self):
        """Stop the scheduler gracefully."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)
        logger.info("[Scheduler] Stopped")

    def run_now(self, task_name: str):
        """Manually trigger a task immediately."""
        for task in self.tasks:
            if task.name == task_name:
                task.execute()
                return
        logger.warning(f"[Scheduler] Task not found: {task_name}")

    def get_status(self) -> List[Dict]:
        """Get status of all scheduled tasks."""
        return [
            {
                "name": t.name,
                "enabled": t.enabled,
                "interval_hours": t.interval.total_seconds() / 3600,
                "last_run": str(t.last_run) if t.last_run else None,
                "next_run": str(t.next_run),
                "run_count": t.run_count,
                "last_error": t.last_error,
            }
            for t in self.tasks
        ]

    def _loop(self):
        """Main scheduler loop — checks every 60 seconds for due tasks."""
        while self._running:
            for task in self.tasks:
                if task.is_due:
                    task.execute()
            time.sleep(60)

    # ── Default Task Implementations ──

    @staticmethod
    def _run_india_code():
        from ingestion.crawlers.india_code_crawler import IndiaCodeCrawler
        from ingestion.data_cleaner import DataCleaner
        from ingestion.metadata_tagger import MetadataTagger
        from ingestion.storage_pipeline import StoragePipeline

        with IndiaCodeCrawler() as crawler:
            records = crawler.crawl()

        cleaner = DataCleaner()
        tagger = MetadataTagger()
        pipeline = StoragePipeline()

        cleaned, _ = cleaner.clean_batch([r.to_dict() for r in records])
        cleaned = cleaner.deduplicate(cleaned)
        tagged = tagger.tag_batch(cleaned)
        pipeline.store(tagged, source_name="india_code")

    @staticmethod
    def _run_constitution():
        from ingestion.crawlers.constitution_crawler import ConstitutionCrawler
        from ingestion.data_cleaner import DataCleaner
        from ingestion.metadata_tagger import MetadataTagger
        from ingestion.storage_pipeline import StoragePipeline

        with ConstitutionCrawler() as crawler:
            records = crawler.crawl()

        cleaner = DataCleaner()
        tagger = MetadataTagger()
        pipeline = StoragePipeline()

        cleaned, _ = cleaner.clean_batch([r.to_dict() for r in records])
        cleaned = cleaner.deduplicate(cleaned)
        tagged = tagger.tag_batch(cleaned)
        pipeline.store(tagged, source_name="constitution")

    @staticmethod
    def _run_courts():
        from ingestion.crawlers.court_crawler import SupremeCourtCrawler
        from ingestion.data_cleaner import DataCleaner
        from ingestion.metadata_tagger import MetadataTagger
        from ingestion.storage_pipeline import StoragePipeline

        with SupremeCourtCrawler() as crawler:
            records = crawler.crawl()

        cleaner = DataCleaner()
        tagger = MetadataTagger()
        pipeline = StoragePipeline()

        cleaned, _ = cleaner.clean_batch([r.to_dict() for r in records])
        cleaned = cleaner.deduplicate(cleaned)
        tagged = tagger.tag_batch(cleaned)
        pipeline.store(tagged, source_name="supreme_court")

    @staticmethod
    def _run_gazette():
        from ingestion.crawlers.gazette_crawler import GazetteCrawler
        from ingestion.data_cleaner import DataCleaner
        from ingestion.metadata_tagger import MetadataTagger
        from ingestion.storage_pipeline import StoragePipeline

        with GazetteCrawler() as crawler:
            records = crawler.crawl()

        cleaner = DataCleaner()
        tagger = MetadataTagger()
        pipeline = StoragePipeline()

        cleaned, _ = cleaner.clean_batch([r.to_dict() for r in records])
        cleaned = cleaner.deduplicate(cleaned)
        tagged = tagger.tag_batch(cleaned)
        pipeline.store(tagged, source_name="gazette")

    @staticmethod
    def _run_state_laws():
        from ingestion.crawlers.gazette_crawler import StateLawCrawler
        from ingestion.data_cleaner import DataCleaner
        from ingestion.metadata_tagger import MetadataTagger
        from ingestion.storage_pipeline import StoragePipeline

        with StateLawCrawler() as crawler:
            records = crawler.crawl()

        cleaner = DataCleaner()
        tagger = MetadataTagger()
        pipeline = StoragePipeline()

        cleaned, _ = cleaner.clean_batch([r.to_dict() for r in records])
        cleaned = cleaner.deduplicate(cleaned)
        tagged = tagger.tag_batch(cleaned)
        pipeline.store(tagged, source_name="state_laws")


# ── Cron Expression Reference (for OS-level scheduling) ──
CRON_SCHEDULES = """
# Add these to crontab (crontab -e) for OS-level scheduling on Linux:
#
# Daily court judgment crawl (2:00 AM IST)
# 0 2 * * * cd /path/to/backend && python -m ingestion run --source court_judgments
#
# Weekly India Code crawl (Sunday 3:00 AM IST)
# 0 3 * * 0 cd /path/to/backend && python -m ingestion run --source india_code
#
# Monthly Constitution update (1st of month, 4:00 AM IST)
# 0 4 1 * * cd /path/to/backend && python -m ingestion run --source constitution
#
# Daily gazette crawl (1:00 AM IST)
# 0 1 * * * cd /path/to/backend && python -m ingestion run --source gazette
#
# Weekly state laws crawl (Saturday 3:00 AM IST)
# 0 3 * * 6 cd /path/to/backend && python -m ingestion run --source state_laws
#
# For Windows Task Scheduler, create tasks that run:
#   python -m ingestion run --source <source_name>
"""
