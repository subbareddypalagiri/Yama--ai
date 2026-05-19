"""
YAMA AI — Data Pipeline Scheduler
=============================================================================
Automated scheduling system for legal data crawling, cleaning, and storage.

Supports three scheduling backends:
    1. THREADING  — Built-in Python threading (dev / single-server)
    2. CELERY     — Distributed task queue via Celery + Redis (production)
    3. CRON       — OS-level cron / Windows Task Scheduler (simple production)

Features:
    • 7 default crawl tasks with configurable intervals
    • Full pipeline per task: crawl → clean → detect amendments → dedup → store → index
    • New-law detection via content-hash comparison
    • Amendment detection via bracket-note parsing
    • Duplicate avoidance via SHA-256 content hash
    • Run history & audit log (IngestionLog table)
    • Manual trigger, enable/disable, reschedule at runtime
    • Graceful shutdown with in-progress task completion
    • Retry with exponential backoff on failures
    • Configurable via environment variables

Usage (threading scheduler — development):
    from data_pipeline.scheduler import PipelineScheduler

    scheduler = PipelineScheduler()
    scheduler.start()              # background thread
    scheduler.run_now("india_code")
    scheduler.get_status()
    scheduler.stop()

Usage (Celery — production):
    # Start worker:   celery -A data_pipeline.scheduler worker -l info -B
    # Tasks auto-run on their beat schedule.

CLI:
    cd backend
    python -m data_pipeline.scheduler start              # Run threading scheduler
    python -m data_pipeline.scheduler run india_code     # Run one task now
    python -m data_pipeline.scheduler run all             # Run all tasks now
    python -m data_pipeline.scheduler status              # Show task status
    python -m data_pipeline.scheduler cron                # Print cron expressions
=============================================================================
"""

import json
import logging
import os
import signal
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("yama_ai.scheduler")

_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)


# ═══════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

class Interval:
    """Named schedule intervals in hours."""
    HOURLY   = 1.0
    DAILY    = 24.0
    WEEKLY   = 168.0
    BIWEEKLY = 336.0
    MONTHLY  = 720.0


# Default schedule for each source
DEFAULT_SCHEDULES: Dict[str, Dict[str, Any]] = {
    "india_code": {
        "description": "Central acts from India Code",
        "interval_hours": Interval.WEEKLY,
        "crawler_method": "crawl_india_code",
        "enabled": True,
        "priority": 1,
    },
    "constitution": {
        "description": "Constitution articles and amendments",
        "interval_hours": Interval.MONTHLY,
        "crawler_method": "crawl_constitution",
        "enabled": True,
        "priority": 2,
    },
    "supreme_court": {
        "description": "Supreme Court judgments",
        "interval_hours": Interval.DAILY,
        "crawler_method": "crawl_supreme_court",
        "enabled": True,
        "priority": 1,
    },
    "high_courts": {
        "description": "High Court judgments (all courts)",
        "interval_hours": Interval.DAILY,
        "crawler_method": "crawl_high_courts",
        "enabled": True,
        "priority": 2,
    },
    "gazette": {
        "description": "Government Gazette notifications",
        "interval_hours": Interval.DAILY,
        "crawler_method": "crawl_gazette",
        "enabled": True,
        "priority": 1,
    },
    "state_laws": {
        "description": "State legislation portals",
        "interval_hours": Interval.WEEKLY,
        "crawler_method": "crawl_state_laws",
        "enabled": True,
        "priority": 3,
    },
    "legislative_dept": {
        "description": "Legislative Department (bills, ordinances)",
        "interval_hours": Interval.WEEKLY,
        "crawler_method": "crawl_legislative_dept",
        "enabled": True,
        "priority": 2,
    },
}


# ═══════════════════════════════════════════════════════════════════════════
#  TASK DATA MODEL
# ═══════════════════════════════════════════════════════════════════════════

class TaskStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DISABLED = "disabled"


@dataclass
class TaskResult:
    """Result of a single task execution."""
    source: str
    status: TaskStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    records_crawled: int = 0
    records_new: int = 0
    records_updated: int = 0
    records_skipped: int = 0
    amendments_detected: int = 0
    duplicates_removed: int = 0
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": round(self.duration_seconds, 2),
            "records_crawled": self.records_crawled,
            "records_new": self.records_new,
            "records_updated": self.records_updated,
            "records_skipped": self.records_skipped,
            "amendments_detected": self.amendments_detected,
            "duplicates_removed": self.duplicates_removed,
            "errors": self.errors,
        }


@dataclass
class ScheduledTask:
    """A crawl task with scheduling metadata."""
    name: str
    description: str
    crawler_method: str
    interval: timedelta
    enabled: bool = True
    priority: int = 1

    # Runtime state
    status: TaskStatus = TaskStatus.IDLE
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    consecutive_failures: int = 0
    last_result: Optional[TaskResult] = None
    history: List[TaskResult] = field(default_factory=list)

    def __post_init__(self):
        if self.next_run is None:
            self.next_run = datetime.now(timezone.utc)

    @property
    def is_due(self) -> bool:
        if not self.enabled:
            return False
        if self.status == TaskStatus.RUNNING:
            return False
        return self.next_run is not None and datetime.now(timezone.utc) >= self.next_run

    def schedule_next(self, failed: bool = False):
        """Compute next run time. Backoff on repeated failures."""
        now = datetime.now(timezone.utc)
        if failed:
            self.consecutive_failures += 1
            # Exponential backoff: 1h, 2h, 4h, 8h, max 24h
            backoff_hours = min(2 ** (self.consecutive_failures - 1), 24)
            self.next_run = now + timedelta(hours=backoff_hours)
            logger.warning(
                "Task '%s' failed (%d consecutive). Next retry in %dh",
                self.name, self.consecutive_failures, backoff_hours,
            )
        else:
            self.consecutive_failures = 0
            self.next_run = now + self.interval

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "status": self.status.value,
            "interval_hours": self.interval.total_seconds() / 3600,
            "priority": self.priority,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "run_count": self.run_count,
            "consecutive_failures": self.consecutive_failures,
            "last_result": self.last_result.to_dict() if self.last_result else None,
        }


# ═══════════════════════════════════════════════════════════════════════════
#  PIPELINE EXECUTOR — runs crawl → clean → store for one source
# ═══════════════════════════════════════════════════════════════════════════

def execute_pipeline(source_name: str, crawler_method: str) -> TaskResult:
    """
    Full pipeline for a single source:
        1. Crawl via LegalCrawler
        2. Clean via LegalDataCleaner (normalize, detect amendments, generate keywords)
        3. Deduplicate via content hash
        4. Store into DB + ChromaDB via LegalStore

    Returns:
        TaskResult with full statistics.
    """
    from data_pipeline.crawler import LegalCrawler
    from data_pipeline.cleaner import LegalDataCleaner
    from legal_database.store import LegalStore

    result = TaskResult(source=source_name, status=TaskStatus.RUNNING, started_at=datetime.now(timezone.utc))
    logger.info("═" * 50)
    logger.info("  Pipeline: %s", source_name)
    logger.info("═" * 50)

    try:
        # ── Step 1: Crawl ──
        logger.info("[1/4] Crawling %s...", source_name)
        with LegalCrawler(delay=2.0) as crawler:
            method = getattr(crawler, crawler_method)
            raw_records = method()

        result.records_crawled = len(raw_records)
        logger.info("  Crawled %d records", result.records_crawled)

        if not raw_records:
            result.status = TaskStatus.COMPLETED
            result.completed_at = datetime.now(timezone.utc)
            result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
            logger.info("  No records found — pipeline complete")
            return result

        # ── Step 2: Clean & Enrich ──
        logger.info("[2/4] Cleaning & enriching...")
        cleaner = LegalDataCleaner(min_description_length=15)
        raw_dicts = [r.to_dict() for r in raw_records]
        cleaned = cleaner.process(raw_dicts)

        result.duplicates_removed = len(raw_dicts) - len(cleaned)
        result.amendments_detected = cleaner.report.amendments_detected
        logger.info(
            "  Cleaned: %d → %d  (amendments: %d, dupes removed: %d)",
            len(raw_dicts), len(cleaned), result.amendments_detected, result.duplicates_removed,
        )

        # ── Step 3: Store ──
        logger.info("[3/4] Storing into database...")
        store = LegalStore()
        store.init_db()
        stats = store.insert_batch(cleaned, index_vectors=False)

        result.records_new = stats.get("inserted", 0)
        result.records_updated = stats.get("updated", 0)
        result.records_skipped = stats.get("skipped", 0)
        logger.info(
            "  DB: +%d new, ~%d updated, =%d skipped",
            result.records_new, result.records_updated, result.records_skipped,
        )

        # ── Step 4: Index vectors ──
        if result.records_new > 0 or result.records_updated > 0:
            logger.info("[4/4] Indexing vectors in ChromaDB...")
            try:
                store.index_vectors()
                logger.info("  Vectors indexed")
            except Exception as vec_err:
                result.errors.append(f"Vector indexing: {vec_err}")
                logger.warning("  Vector indexing skipped: %s", vec_err)
        else:
            logger.info("[4/4] No changes — vector indexing skipped")

        # ── Log to ingestion_logs table ──
        _log_ingestion(source_name, result)

        result.status = TaskStatus.COMPLETED

    except Exception as exc:
        result.status = TaskStatus.FAILED
        result.errors.append(str(exc))
        logger.error("Pipeline failed for %s: %s", source_name, exc)
        _log_ingestion(source_name, result, error=str(exc))

    result.completed_at = datetime.now(timezone.utc)
    result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
    logger.info(
        "  Pipeline %s in %.1fs",
        result.status.value, result.duration_seconds,
    )
    return result


def _log_ingestion(source_name: str, result: TaskResult, error: Optional[str] = None):
    """Write an IngestionLog record for audit trail."""
    try:
        from app.db.database import SessionLocal, engine
        from app.db.models import Base, IngestionLog

        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        log = IngestionLog(
            source_name=source_name,
            run_type="scheduled",
            status=result.status.value,
            records_found=result.records_crawled,
            records_inserted=result.records_new,
            records_updated=result.records_updated,
            records_skipped=result.records_skipped,
            error_message=error,
            completed_at=result.completed_at,
        )
        db.add(log)
        db.commit()
        db.close()
    except Exception as exc:
        logger.warning("Could not write ingestion log: %s", exc)


# ═══════════════════════════════════════════════════════════════════════════
#  THREADING SCHEDULER (development / single-server)
# ═══════════════════════════════════════════════════════════════════════════

class PipelineScheduler:
    """
    Background scheduler that runs crawl pipelines on configurable intervals.

    Uses Python threading — suitable for development and single-server deployment.
    For distributed production, use Celery (see CeleryConfig below).

    Example:
        scheduler = PipelineScheduler()
        scheduler.start()
        # ... runs in background ...
        scheduler.run_now("india_code")
        print(scheduler.get_status())
        scheduler.stop()
    """

    def __init__(self, check_interval: int = 60):
        """
        Args:
            check_interval: Seconds between schedule checks (default 60).
        """
        self.check_interval = check_interval
        self.tasks: Dict[str, ScheduledTask] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._shutdown_event = threading.Event()

        self._register_default_tasks()

    def _register_default_tasks(self):
        """Register all default crawl tasks from config."""
        for name, cfg in DEFAULT_SCHEDULES.items():
            task = ScheduledTask(
                name=name,
                description=cfg["description"],
                crawler_method=cfg["crawler_method"],
                interval=timedelta(hours=cfg["interval_hours"]),
                enabled=cfg["enabled"],
                priority=cfg["priority"],
            )
            self.tasks[name] = task
            logger.info(
                "Registered: %-20s every %5.0fh  (priority %d)",
                name, cfg["interval_hours"], cfg["priority"],
            )

    # ── Lifecycle ──

    def start(self):
        """Start the scheduler in a background daemon thread."""
        if self._running:
            logger.warning("Scheduler already running")
            return

        self._running = True
        self._shutdown_event.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="pipeline-scheduler",
        )
        self._thread.start()
        logger.info("Scheduler started (check every %ds)", self.check_interval)

    def stop(self):
        """Stop the scheduler gracefully, waiting for in-progress tasks."""
        logger.info("Scheduler stopping...")
        self._running = False
        self._shutdown_event.set()
        if self._thread:
            self._thread.join(timeout=30)
        logger.info("Scheduler stopped")

    def _loop(self):
        """Main loop — checks for due tasks and executes them by priority."""
        while self._running:
            due_tasks = sorted(
                [t for t in self.tasks.values() if t.is_due],
                key=lambda t: t.priority,
            )

            for task in due_tasks:
                if not self._running:
                    break
                self._execute_task(task)

            # Wait for check_interval or until shutdown
            self._shutdown_event.wait(timeout=self.check_interval)

    def _execute_task(self, task: ScheduledTask):
        """Execute a single scheduled task through the full pipeline."""
        with self._lock:
            task.status = TaskStatus.RUNNING

        try:
            result = execute_pipeline(task.name, task.crawler_method)

            with self._lock:
                task.status = result.status
                task.last_run = result.started_at
                task.run_count += 1
                task.last_result = result
                task.history.append(result)
                # Keep only last 20 results
                if len(task.history) > 20:
                    task.history = task.history[-20:]
                task.schedule_next(failed=(result.status == TaskStatus.FAILED))

        except Exception as exc:
            logger.error("Task '%s' crashed: %s", task.name, exc)
            with self._lock:
                task.status = TaskStatus.FAILED
                task.schedule_next(failed=True)

    # ── Manual control ──

    def run_now(self, task_name: str) -> Optional[TaskResult]:
        """Manually trigger a task immediately (blocking)."""
        task = self.tasks.get(task_name)
        if not task:
            logger.error("Unknown task: %s", task_name)
            return None

        logger.info("Manual trigger: %s", task_name)
        result = execute_pipeline(task.name, task.crawler_method)

        with self._lock:
            task.status = result.status
            task.last_run = result.started_at
            task.run_count += 1
            task.last_result = result
            task.history.append(result)
            task.schedule_next(failed=(result.status == TaskStatus.FAILED))

        return result

    def run_all(self) -> List[TaskResult]:
        """Run all enabled tasks sequentially (blocking)."""
        results = []
        for name, task in sorted(self.tasks.items(), key=lambda x: x[1].priority):
            if task.enabled:
                result = self.run_now(name)
                if result:
                    results.append(result)
        return results

    # ── Configuration ──

    def enable_task(self, name: str):
        if name in self.tasks:
            self.tasks[name].enabled = True
            if self.tasks[name].status == TaskStatus.DISABLED:
                self.tasks[name].status = TaskStatus.IDLE

    def disable_task(self, name: str):
        if name in self.tasks:
            self.tasks[name].enabled = False
            self.tasks[name].status = TaskStatus.DISABLED

    def reschedule(self, name: str, interval_hours: float):
        """Change the interval for a task."""
        if name in self.tasks:
            self.tasks[name].interval = timedelta(hours=interval_hours)
            logger.info("Rescheduled '%s' to every %.1fh", name, interval_hours)

    def add_custom_task(
        self, name: str, description: str, crawler_method: str,
        interval_hours: float = 168, priority: int = 3,
    ):
        """Register a custom crawl task at runtime."""
        self.tasks[name] = ScheduledTask(
            name=name, description=description, crawler_method=crawler_method,
            interval=timedelta(hours=interval_hours), priority=priority,
        )

    # ── Status ──

    def get_status(self) -> Dict[str, Any]:
        """Full scheduler status for API / CLI."""
        return {
            "scheduler_running": self._running,
            "total_tasks": len(self.tasks),
            "enabled_tasks": sum(1 for t in self.tasks.values() if t.enabled),
            "tasks": {name: task.to_dict() for name, task in self.tasks.items()},
        }

    def get_task_status(self, name: str) -> Optional[Dict[str, Any]]:
        task = self.tasks.get(name)
        return task.to_dict() if task else None

    def get_history(self, name: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get execution history for one or all tasks."""
        if name:
            task = self.tasks.get(name)
            if not task:
                return []
            return [r.to_dict() for r in task.history[-limit:]]

        all_history = []
        for task in self.tasks.values():
            all_history.extend(task.history)
        all_history.sort(key=lambda r: r.started_at, reverse=True)
        return [r.to_dict() for r in all_history[:limit]]


# ═══════════════════════════════════════════════════════════════════════════
#  CELERY CONFIGURATION (production)
# ═══════════════════════════════════════════════════════════════════════════

CELERY_CONFIG = """
# ═══════════════════════════════════════════════════════════════════════════
#  Celery Configuration for YAMA AI Scheduled Crawls
# ═══════════════════════════════════════════════════════════════════════════
#
#  Prerequisites:
#      pip install celery[redis]
#      # Redis running on localhost:6379
#
#  Start worker + beat:
#      celery -A data_pipeline.scheduler.celery_app worker -l info -B
#
#  Or separate:
#      celery -A data_pipeline.scheduler.celery_app worker -l info
#      celery -A data_pipeline.scheduler.celery_app beat -l info
# ═══════════════════════════════════════════════════════════════════════════
"""

# Celery app (only created if celery is installed)
celery_app = None

try:
    from celery import Celery
    from celery.schedules import crontab

    celery_app = Celery(
        "yama_ai",
        broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
        backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Asia/Kolkata",
        enable_utc=True,
        task_track_started=True,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        task_soft_time_limit=3600,    # 1 hour soft limit
        task_time_limit=7200,         # 2 hour hard limit
    )

    # Beat schedule — automatic periodic tasks
    celery_app.conf.beat_schedule = {
        "crawl-india-code-weekly": {
            "task": "data_pipeline.scheduler.celery_crawl",
            "schedule": crontab(hour=3, minute=0, day_of_week="sunday"),
            "args": ("india_code", "crawl_india_code"),
        },
        "crawl-constitution-monthly": {
            "task": "data_pipeline.scheduler.celery_crawl",
            "schedule": crontab(hour=4, minute=0, day_of_month="1"),
            "args": ("constitution", "crawl_constitution"),
        },
        "crawl-supreme-court-daily": {
            "task": "data_pipeline.scheduler.celery_crawl",
            "schedule": crontab(hour=2, minute=0),
            "args": ("supreme_court", "crawl_supreme_court"),
        },
        "crawl-high-courts-daily": {
            "task": "data_pipeline.scheduler.celery_crawl",
            "schedule": crontab(hour=2, minute=30),
            "args": ("high_courts", "crawl_high_courts"),
        },
        "crawl-gazette-daily": {
            "task": "data_pipeline.scheduler.celery_crawl",
            "schedule": crontab(hour=1, minute=0),
            "args": ("gazette", "crawl_gazette"),
        },
        "crawl-state-laws-weekly": {
            "task": "data_pipeline.scheduler.celery_crawl",
            "schedule": crontab(hour=3, minute=0, day_of_week="saturday"),
            "args": ("state_laws", "crawl_state_laws"),
        },
        "crawl-legislative-weekly": {
            "task": "data_pipeline.scheduler.celery_crawl",
            "schedule": crontab(hour=3, minute=30, day_of_week="saturday"),
            "args": ("legislative_dept", "crawl_legislative_dept"),
        },
    }

    @celery_app.task(name="data_pipeline.scheduler.celery_crawl", bind=True, max_retries=3)
    def celery_crawl(self, source_name: str, crawler_method: str):
        """Celery task that runs the full pipeline for a source."""
        try:
            result = execute_pipeline(source_name, crawler_method)
            return result.to_dict()
        except Exception as exc:
            logger.error("Celery task %s failed: %s", source_name, exc)
            raise self.retry(exc=exc, countdown=300)  # retry in 5 minutes

except ImportError:
    logger.debug("Celery not installed — Celery scheduler unavailable. Install with: pip install celery[redis]")


# ═══════════════════════════════════════════════════════════════════════════
#  CRON EXPRESSIONS (OS-level scheduling)
# ═══════════════════════════════════════════════════════════════════════════

CRON_EXPRESSIONS = """
# ═══════════════════════════════════════════════════════════════════════════
#  YAMA AI — Cron Schedule for Legal Data Crawls
# ═══════════════════════════════════════════════════════════════════════════
#
#  Add to crontab:  crontab -e
#  All times in IST (UTC+5:30). Adjust for your server timezone.
#
# ── Daily tasks ──
#
# Supreme Court judgments (2:00 AM IST daily)
0 2 * * *   cd /path/to/backend && python -m data_pipeline.scheduler run supreme_court >> /var/log/yama/supreme_court.log 2>&1
#
# High Court judgments (2:30 AM IST daily)
30 2 * * *  cd /path/to/backend && python -m data_pipeline.scheduler run high_courts >> /var/log/yama/high_courts.log 2>&1
#
# Gazette notifications (1:00 AM IST daily)
0 1 * * *   cd /path/to/backend && python -m data_pipeline.scheduler run gazette >> /var/log/yama/gazette.log 2>&1
#
# ── Weekly tasks ──
#
# India Code central acts (Sunday 3:00 AM IST)
0 3 * * 0   cd /path/to/backend && python -m data_pipeline.scheduler run india_code >> /var/log/yama/india_code.log 2>&1
#
# State laws (Saturday 3:00 AM IST)
0 3 * * 6   cd /path/to/backend && python -m data_pipeline.scheduler run state_laws >> /var/log/yama/state_laws.log 2>&1
#
# Legislative Department (Saturday 3:30 AM IST)
30 3 * * 6  cd /path/to/backend && python -m data_pipeline.scheduler run legislative_dept >> /var/log/yama/legislative.log 2>&1
#
# ── Monthly tasks ──
#
# Constitution (1st of month, 4:00 AM IST)
0 4 1 * *   cd /path/to/backend && python -m data_pipeline.scheduler run constitution >> /var/log/yama/constitution.log 2>&1
#
# ── Full crawl (monthly, 1st Sunday at 5:00 AM IST) ──
0 5 * * 0   [ $(date +\\%d) -le 7 ] && cd /path/to/backend && python -m data_pipeline.scheduler run all >> /var/log/yama/full_crawl.log 2>&1
#
# ═══════════════════════════════════════════════════════════════════════════

# ── Windows Task Scheduler (PowerShell equivalent) ──
#
# For each task, create a Scheduled Task:
#   Action:  python -m data_pipeline.scheduler run <source_name>
#   Start in: C:\\path\\to\\backend
#   Trigger:  Daily/Weekly as per schedule above
#
# Example PowerShell to create a task:
#   $action = New-ScheduledTaskAction -Execute "python" -Argument "-m data_pipeline.scheduler run supreme_court" -WorkingDirectory "C:\\path\\to\\backend"
#   $trigger = New-ScheduledTaskTrigger -Daily -At "2:00AM"
#   Register-ScheduledTask -TaskName "YAMA-SupremeCourt" -Action $action -Trigger $trigger -Description "YAMA AI Supreme Court crawl"
"""


# ═══════════════════════════════════════════════════════════════════════════
#  CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    import argparse

    ap = argparse.ArgumentParser(
        prog="python -m data_pipeline.scheduler",
        description="YAMA AI — Data Pipeline Scheduler: Automated legal data crawling.",
    )
    sub = ap.add_subparsers(dest="command", required=True)

    # start — run threading scheduler
    p_start = sub.add_parser("start", help="Start background threading scheduler (blocks)")
    p_start.add_argument("--interval", type=int, default=60, help="Check interval in seconds")

    # run — run one task now
    p_run = sub.add_parser("run", help="Run a specific crawl task now")
    p_run.add_argument(
        "source",
        choices=list(DEFAULT_SCHEDULES.keys()) + ["all"],
        help="Source to crawl",
    )

    # status
    sub.add_parser("status", help="Show current task configuration and schedule")

    # cron
    sub.add_parser("cron", help="Print cron expressions for OS-level scheduling")

    # history
    p_hist = sub.add_parser("history", help="Show recent execution history")
    p_hist.add_argument("--source", default=None, help="Filter by source")
    p_hist.add_argument("--limit", type=int, default=20)

    args = ap.parse_args()

    if args.command == "start":
        print()
        print("═" * 60)
        print("  YAMA AI — Pipeline Scheduler")
        print("═" * 60)
        print(f"  Check interval: {args.interval}s")
        print(f"  Tasks: {len(DEFAULT_SCHEDULES)}")
        print("  Press Ctrl+C to stop")
        print("═" * 60)
        print()

        scheduler = PipelineScheduler(check_interval=args.interval)
        scheduler.start()

        # Block main thread until Ctrl+C
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹  Shutting down...")
            scheduler.stop()
            print("✅ Scheduler stopped")

    elif args.command == "run":
        if args.source == "all":
            print("\n🚀 Running all tasks...\n")
            scheduler = PipelineScheduler()
            results = scheduler.run_all()
            print("\n" + "═" * 60)
            print("  Results Summary")
            print("═" * 60)
            for r in results:
                status_icon = "✅" if r.status == TaskStatus.COMPLETED else "❌"
                print(
                    f"  {status_icon} {r.source:20s}  "
                    f"+{r.records_new} new  ~{r.records_updated} upd  "
                    f"={r.records_skipped} skip  "
                    f"({r.duration_seconds:.1f}s)"
                )
            print("═" * 60)
        else:
            print(f"\n🚀 Running: {args.source}\n")
            cfg = DEFAULT_SCHEDULES[args.source]
            result = execute_pipeline(args.source, cfg["crawler_method"])
            print(f"\n{'✅' if result.status == TaskStatus.COMPLETED else '❌'} {result.source}")
            print(f"  Status:     {result.status.value}")
            print(f"  Duration:   {result.duration_seconds:.1f}s")
            print(f"  Crawled:    {result.records_crawled}")
            print(f"  New:        {result.records_new}")
            print(f"  Updated:    {result.records_updated}")
            print(f"  Skipped:    {result.records_skipped}")
            print(f"  Amendments: {result.amendments_detected}")
            print(f"  Dupes:      {result.duplicates_removed}")
            if result.errors:
                print(f"  Errors:     {result.errors}")

    elif args.command == "status":
        print()
        print("═" * 70)
        print("  YAMA AI — Scheduled Tasks")
        print("═" * 70)
        print(f"  {'Task':<22s} {'Interval':>10s}  {'Priority':>8s}  {'Enabled':>7s}")
        print("  " + "─" * 64)
        for name, cfg in DEFAULT_SCHEDULES.items():
            interval = cfg["interval_hours"]
            if interval >= 720:
                label = f"{interval/720:.0f} month"
            elif interval >= 168:
                label = f"{interval/168:.0f} week"
            elif interval >= 24:
                label = f"{interval/24:.0f} day"
            else:
                label = f"{interval:.0f} hour"
            print(
                f"  {name:<22s} {label:>10s}  "
                f"{'P'+str(cfg['priority']):>8s}  "
                f"{'yes' if cfg['enabled'] else 'no':>7s}"
            )
        print("═" * 70)
        print()
        print("  Backends available:")
        print(f"    Threading:  ✅ always available")
        print(f"    Celery:     {'✅' if celery_app else '❌'} {'installed' if celery_app else 'pip install celery[redis]'}")
        print(f"    Cron:       ✅ use 'python -m data_pipeline.scheduler cron'")
        print()

    elif args.command == "cron":
        print(CRON_EXPRESSIONS)

    elif args.command == "history":
        scheduler = PipelineScheduler()
        history = scheduler.get_history(name=args.source, limit=args.limit)
        if not history:
            print("\nNo execution history yet.")
        else:
            print(f"\n📜 Last {len(history)} runs:\n")
            for h in history:
                print(json.dumps(h, indent=2))


if __name__ == "__main__":
    main()
