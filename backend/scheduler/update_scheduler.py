"""
YAMA AI — Automatic Legal Knowledge Update Scheduler
=============================================================================
Orchestrates all crawlers on a configurable schedule. Runs continuously
as a background service, detecting new laws, judgments, and amendments.

Architecture:
    ┌─────────────────────────────────────────────────────────┐
    │                   UpdateScheduler                       │
    │                                                         │
    │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐│
    │  │ APScheduler│  │ Celery     │  │ Simple Cron        ││
    │  │ (default)  │  │ (optional) │  │ (lightweight)      ││
    │  └────────────┘  └────────────┘  └────────────────────┘│
    │         ↓                                               │
    │  ┌──────────────────────────────────────────────────┐   │
    │  │              Job Queue                           │   │
    │  │  constitution  (monthly)                        │   │
    │  │  central_laws  (weekly)                         │   │
    │  │  state_laws    (weekly)                         │   │
    │  │  judgments     (daily)                          │   │
    │  └──────────────────────────────────────────────────┘   │
    │         ↓                                               │
    │  ┌──────────────────────────────────────────────────┐   │
    │  │          Pipeline Per Job Run                    │   │
    │  │  Crawl → Parse → Clean → Store → Embed          │   │
    │  └──────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────┘

Schedule Defaults:
    • Constitution     — monthly    (amendments are rare)
    • Central Acts     — weekly     (India Code updates weekly)
    • State Acts       — weekly
    • Court Judgments  — daily      (SCI publishes daily)
    • eGazette         — daily

Deduplication:
    • Content-hash based — unchanged sections are skipped
    • Ingestion log records every run in the DB
    • Amendment detection compares hash of existing vs new text

Usage:
    # Run with APScheduler (recommended for production)
    python -m scheduler.update_scheduler

    # Run once immediately (all sources)
    python -m scheduler.update_scheduler --run-now

    # Run specific source
    python -m scheduler.update_scheduler --run-now --source judgments

    # Show schedule
    python -m scheduler.update_scheduler --status

    # Celery mode (requires Redis/RabbitMQ)
    python -m scheduler.update_scheduler --mode celery

Environment Variables:
    SCHEDULER_MODE       apscheduler | celery | simple  (default: apscheduler)
    SCHEDULE_JUDGMENTS   cron expression (default: 0 2 * * *)   [2 AM daily]
    SCHEDULE_LAWS        cron expression (default: 0 3 * * 0)   [3 AM Sunday]
    SCHEDULE_CONSTITUTION cron expression (default: 0 4 1 * *)  [4 AM 1st of month]
    CRAWL_DELAY          seconds between requests (default: 2.0)
    DB_URL               PostgreSQL DSN (default: SQLite)
    CELERY_BROKER        Redis/RabbitMQ URL (if using Celery)
=============================================================================
"""

import argparse
import json
import logging
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# ── Path setup ──
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("yama_ai.scheduler")


# ═══════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

class SchedulerConfig:
    """Runtime configuration for the update scheduler."""

    # Cron schedule for each source (minute hour day month weekday)
    SCHEDULE_JUDGMENTS    = os.getenv("SCHEDULE_JUDGMENTS",    "0 2 * * *")   # 2:00 AM daily
    SCHEDULE_LAWS         = os.getenv("SCHEDULE_LAWS",         "0 3 * * 0")   # 3:00 AM Sunday
    SCHEDULE_STATE_LAWS   = os.getenv("SCHEDULE_STATE_LAWS",   "0 4 * * 0")   # 4:00 AM Sunday
    SCHEDULE_CONSTITUTION = os.getenv("SCHEDULE_CONSTITUTION", "0 4 1 * *")   # 4:00 AM 1st of month
    SCHEDULE_GAZETTE      = os.getenv("SCHEDULE_GAZETTE",      "0 1 * * *")   # 1:00 AM daily

    # Crawler settings
    CRAWL_DELAY     = float(os.getenv("CRAWL_DELAY", "2.0"))
    CRAWL_TIMEOUT   = int(os.getenv("CRAWL_TIMEOUT", "30"))
    MAX_RETRIES     = int(os.getenv("CRAWL_MAX_RETRIES", "3"))

    # Output
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join(_BACKEND_ROOT, "data_pipeline", "datasets"))
    EXPORT_JSON = os.getenv("EXPORT_JSON", "true").lower() == "true"

    # Celery
    CELERY_BROKER = os.getenv("CELERY_BROKER", "redis://localhost:6379/0")
    CELERY_BACKEND = os.getenv("CELERY_BACKEND", "redis://localhost:6379/0")

    # Notifications
    NOTIFY_ON_ERROR = os.getenv("NOTIFY_ON_ERROR", "false").lower() == "true"


config = SchedulerConfig()


# ═══════════════════════════════════════════════════════════════════════════
#  RUN STATISTICS
# ═══════════════════════════════════════════════════════════════════════════

class RunStats:
    """Tracks statistics for one scheduler run."""

    def __init__(self, source: str):
        self.source = source
        self.started_at = datetime.now(timezone.utc)
        self.completed_at: Optional[datetime] = None
        self.status = "running"
        self.records_found = 0
        self.records_inserted = 0
        self.records_updated = 0
        self.records_skipped = 0
        self.error_message: Optional[str] = None

    def complete(self, status: str = "success"):
        self.completed_at = datetime.now(timezone.utc)
        self.status = status

    @property
    def duration_seconds(self) -> float:
        end = self.completed_at or datetime.now(timezone.utc)
        return (end - self.started_at).total_seconds()

    def to_dict(self) -> Dict:
        return {
            "source": self.source,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": round(self.duration_seconds, 2),
            "records_found": self.records_found,
            "records_inserted": self.records_inserted,
            "records_updated": self.records_updated,
            "records_skipped": self.records_skipped,
            "error_message": self.error_message,
        }

    def __str__(self) -> str:
        return (
            f"[{self.source}] {self.status.upper()} | "
            f"found={self.records_found} inserted={self.records_inserted} "
            f"updated={self.records_updated} skipped={self.records_skipped} "
            f"duration={self.duration_seconds:.1f}s"
        )


# ═══════════════════════════════════════════════════════════════════════════
#  PIPELINE RUNNER
# ═══════════════════════════════════════════════════════════════════════════

class LegalIngestionPipeline:
    """
    Runs the full ingestion pipeline for one source:
        Crawl → Parse → Clean → Store → Embed
    """

    def __init__(self):
        self._store = None
        self._embedder = None
        self._store_initialized = False

    def _get_store(self):
        """Lazy-initialize database store."""
        if not self._store_initialized:
            try:
                from legal_database.store import LegalStore
                self._store = LegalStore()
                self._store.init_db()
                self._store_initialized = True
                logger.info("Database store initialized")
            except Exception as exc:
                logger.warning("DB store unavailable: %s — running in file-only mode", exc)
                self._store = None
                self._store_initialized = True
        return self._store

    def _get_embedder(self):
        """Lazy-initialize embedding generator."""
        if self._embedder is None:
            try:
                from retrieval_engine.embedding_generator import LegalEmbeddingGenerator
                self._embedder = LegalEmbeddingGenerator()
                logger.info("Embedding generator initialized")
            except Exception as exc:
                logger.warning("Embedder unavailable: %s", exc)
                self._embedder = None
        return self._embedder

    def _store_records(self, records: List[Dict], source: str) -> Dict[str, int]:
        """Store records in DB and return insert/update/skip counts."""
        counts = {"inserted": 0, "updated": 0, "skipped": 0}
        store = self._get_store()
        if not store:
            return counts

        try:
            result = store.insert_batch(records)
            counts.update(result)
        except Exception as exc:
            logger.error("DB store error for %s: %s", source, exc)

        return counts

    def _generate_embeddings(self, records: List[Dict]) -> None:
        """Generate and store embeddings for a batch of records."""
        embedder = self._get_embedder()
        if not embedder:
            return

        try:
            texts = [
                f"{r.get('act_name', '')} {r.get('title', '')} {r.get('description', '')}"
                for r in records
            ]
            ids = [r.get("content_hash", str(i)) for i, r in enumerate(records)]
            metadatas = [{
                "act_name": r.get("act_name", ""),
                "section_number": r.get("section_number", ""),
                "category": r.get("category", "general"),
                "jurisdiction": r.get("jurisdiction", "central"),
                "law_type": r.get("law_type", "act"),
            } for r in records]
            embedder.upsert_batch(texts, ids, metadatas)
        except Exception as exc:
            logger.error("Embedding error: %s", exc)

    def _export_json(self, records: List[Dict], source: str) -> None:
        """Save records as JSON dataset file."""
        if not config.EXPORT_JSON:
            return

        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        fname = {
            "constitution":  "constitution.json",
            "central_laws":  "laws.json",
            "state_laws":    "state_laws.json",
            "judgments":     "court_judgments.json",
            "gazette":       "gazette.json",
        }.get(source, f"{source}.json")

        path = os.path.join(config.OUTPUT_DIR, fname)
        data = {
            "metadata": {
                "source": source,
                "total_records": len(records),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            "records": records,
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("Exported %d records → %s", len(records), path)
        except Exception as exc:
            logger.error("JSON export error: %s", exc)

    def run_constitution(self, offline: bool = False) -> RunStats:
        """Run Constitution crawler pipeline."""
        stats = RunStats("constitution")
        logger.info("=" * 60)
        logger.info("Starting Constitution ingestion")
        logger.info("=" * 60)

        try:
            from data_pipeline.crawler_constitution import ConstitutionCrawler
            crawler = ConstitutionCrawler(
                delay=config.CRAWL_DELAY,
                timeout=config.CRAWL_TIMEOUT,
                max_retries=config.MAX_RETRIES,
            )
            if offline:
                records_obj = crawler._get_seed_data()
            else:
                records_obj = crawler.crawl()

            records = [r.to_dict() for r in records_obj]
            stats.records_found = len(records)

            # Store
            counts = self._store_records(records, "constitution")
            stats.records_inserted = counts.get("inserted", 0)
            stats.records_updated = counts.get("updated", 0)
            stats.records_skipped = counts.get("skipped", len(records))

            # Embeddings
            self._generate_embeddings(records)

            # Export
            self._export_json(records, "constitution")

            stats.complete("success")
            logger.info(stats)

        except Exception as exc:
            stats.error_message = str(exc)
            stats.complete("failed")
            logger.error("Constitution ingestion FAILED: %s\n%s", exc, traceback.format_exc())

        return stats

    def run_central_laws(
        self,
        acts: Optional[List[str]] = None,
        offline: bool = False,
    ) -> RunStats:
        """Run Central Laws crawler pipeline."""
        stats = RunStats("central_laws")
        logger.info("=" * 60)
        logger.info("Starting Central Laws ingestion")
        logger.info("=" * 60)

        try:
            from data_pipeline.crawler_central_laws import CentralLawsCrawler
            crawler = CentralLawsCrawler(
                delay=config.CRAWL_DELAY,
                timeout=config.CRAWL_TIMEOUT,
                max_retries=config.MAX_RETRIES,
            )
            if offline:
                records_obj = crawler._get_seed_data()
            else:
                records_obj = crawler.crawl(acts=acts)

            records = [r.to_dict() for r in records_obj]
            stats.records_found = len(records)

            counts = self._store_records(records, "central_laws")
            stats.records_inserted = counts.get("inserted", 0)
            stats.records_updated = counts.get("updated", 0)
            stats.records_skipped = counts.get("skipped", len(records))

            self._generate_embeddings(records)
            self._export_json(records, "central_laws")

            stats.complete("success")
            logger.info(stats)

        except Exception as exc:
            stats.error_message = str(exc)
            stats.complete("failed")
            logger.error("Central Laws ingestion FAILED: %s\n%s", exc, traceback.format_exc())

        return stats

    def run_state_laws(
        self,
        states: Optional[List[str]] = None,
        offline: bool = False,
    ) -> RunStats:
        """Run State Laws crawler pipeline."""
        stats = RunStats("state_laws")
        logger.info("=" * 60)
        logger.info("Starting State Laws ingestion")
        logger.info("=" * 60)

        try:
            from data_pipeline.crawler_state_laws import StateLawsCrawler
            crawler = StateLawsCrawler(
                delay=config.CRAWL_DELAY,
                timeout=config.CRAWL_TIMEOUT,
                max_retries=config.MAX_RETRIES,
            )
            if offline:
                records_obj = crawler._get_seed_data()
            else:
                records_obj = crawler.crawl(states=states)

            records = [r.to_dict() for r in records_obj]
            stats.records_found = len(records)

            counts = self._store_records(records, "state_laws")
            stats.records_inserted = counts.get("inserted", 0)
            stats.records_updated = counts.get("updated", 0)
            stats.records_skipped = counts.get("skipped", len(records))

            self._generate_embeddings(records)
            self._export_json(records, "state_laws")

            stats.complete("success")
            logger.info(stats)

        except Exception as exc:
            stats.error_message = str(exc)
            stats.complete("failed")
            logger.error("State Laws ingestion FAILED: %s\n%s", exc, traceback.format_exc())

        return stats

    def run_judgments(
        self,
        courts: Optional[List[str]] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        offline: bool = False,
    ) -> RunStats:
        """Run Court Judgments crawler pipeline."""
        stats = RunStats("judgments")
        logger.info("=" * 60)
        logger.info("Starting Court Judgments ingestion")
        logger.info("=" * 60)

        try:
            from data_pipeline.crawler_court_judgments import CourtJudgmentCrawler
            crawler = CourtJudgmentCrawler(
                delay=max(config.CRAWL_DELAY, 3.0),  # Court portals need longer delays
                timeout=config.CRAWL_TIMEOUT,
                max_retries=config.MAX_RETRIES,
            )
            if offline:
                records_obj = crawler._get_seed_data()
            else:
                records_obj = crawler.crawl(
                    courts=courts,
                    from_date=from_date,
                    to_date=to_date,
                )

            records = [r.to_dict() for r in records_obj]
            stats.records_found = len(records)

            counts = self._store_records(records, "judgments")
            stats.records_inserted = counts.get("inserted", 0)
            stats.records_updated = counts.get("updated", 0)
            stats.records_skipped = counts.get("skipped", len(records))

            self._generate_embeddings(records)
            self._export_json(records, "judgments")

            stats.complete("success")
            logger.info(stats)

        except Exception as exc:
            stats.error_message = str(exc)
            stats.complete("failed")
            logger.error("Judgments ingestion FAILED: %s\n%s", exc, traceback.format_exc())

        return stats

    def run_all(self, offline: bool = False) -> List[RunStats]:
        """
        Run all crawlers in sequence.

        Order:
        1. Constitution (least frequent)
        2. Central Acts
        3. State Acts
        4. Court Judgments (most frequent)
        """
        all_stats = []

        all_stats.append(self.run_constitution(offline=offline))
        time.sleep(5)  # Pause between source types

        all_stats.append(self.run_central_laws(offline=offline))
        time.sleep(5)

        all_stats.append(self.run_state_laws(offline=offline))
        time.sleep(5)

        all_stats.append(self.run_judgments(offline=offline))

        return all_stats


# ═══════════════════════════════════════════════════════════════════════════
#  APSCHEDULER ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class APSchedulerEngine:
    """
    Production scheduler using APScheduler.
    Runs jobs on cron schedules with persistence.

    Install: pip install apscheduler
    """

    def __init__(self):
        self.pipeline = LegalIngestionPipeline()
        self.scheduler = None
        self._run_log: List[Dict] = []

    def _parse_cron(self, cron_expr: str) -> Dict:
        """Parse cron expression '0 2 * * *' into APScheduler kwargs."""
        parts = cron_expr.strip().split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {cron_expr}")
        minute, hour, day, month, day_of_week = parts
        kwargs = {}
        if minute != "*":
            kwargs["minute"] = minute
        if hour != "*":
            kwargs["hour"] = hour
        if day != "*":
            kwargs["day"] = day
        if month != "*":
            kwargs["month"] = month
        if day_of_week != "*":
            kwargs["day_of_week"] = day_of_week
        return kwargs

    def _log_run(self, stats: RunStats):
        entry = stats.to_dict()
        self._run_log.append(entry)
        # Keep last 200 entries in memory
        if len(self._run_log) > 200:
            self._run_log = self._run_log[-200:]
        # Persist to file
        log_path = os.path.join(config.OUTPUT_DIR, "scheduler_log.json")
        try:
            os.makedirs(config.OUTPUT_DIR, exist_ok=True)
            existing = []
            if os.path.exists(log_path):
                with open(log_path) as f:
                    existing = json.load(f)
            existing.append(entry)
            with open(log_path, "w") as f:
                json.dump(existing[-500:], f, indent=2)  # Keep last 500 entries
        except Exception as exc:
            logger.warning("Could not write scheduler log: %s", exc)

    def _job_constitution(self):
        stats = self.pipeline.run_constitution()
        self._log_run(stats)
        if stats.status == "failed" and config.NOTIFY_ON_ERROR:
            self._notify_error("constitution", stats.error_message)

    def _job_central_laws(self):
        stats = self.pipeline.run_central_laws()
        self._log_run(stats)
        if stats.status == "failed" and config.NOTIFY_ON_ERROR:
            self._notify_error("central_laws", stats.error_message)

    def _job_state_laws(self):
        stats = self.pipeline.run_state_laws()
        self._log_run(stats)

    def _job_judgments(self):
        stats = self.pipeline.run_judgments()
        self._log_run(stats)

    def _notify_error(self, source: str, message: Optional[str]):
        """Hook for error notifications (extend to email/Slack/webhook)."""
        logger.error("SCHEDULER ERROR NOTIFICATION — source=%s: %s", source, message)

    def start(self):
        """Start the APScheduler background scheduler."""
        try:
            from apscheduler.schedulers.blocking import BlockingScheduler
            from apscheduler.triggers.cron import CronTrigger
        except ImportError:
            logger.error(
                "APScheduler not installed. Install with: pip install apscheduler\n"
                "Or use --mode simple for the built-in simple scheduler."
            )
            sys.exit(1)

        self.scheduler = BlockingScheduler(timezone="Asia/Kolkata")

        # Constitution: monthly
        cron_c = self._parse_cron(config.SCHEDULE_CONSTITUTION)
        self.scheduler.add_job(
            self._job_constitution,
            CronTrigger(**cron_c),
            id="constitution",
            name="Constitution Crawler",
            replace_existing=True,
            misfire_grace_time=3600,
        )

        # Central Laws: weekly
        cron_l = self._parse_cron(config.SCHEDULE_LAWS)
        self.scheduler.add_job(
            self._job_central_laws,
            CronTrigger(**cron_l),
            id="central_laws",
            name="Central Laws Crawler",
            replace_existing=True,
            misfire_grace_time=3600,
        )

        # State Laws: weekly
        cron_sl = self._parse_cron(config.SCHEDULE_STATE_LAWS)
        self.scheduler.add_job(
            self._job_state_laws,
            CronTrigger(**cron_sl),
            id="state_laws",
            name="State Laws Crawler",
            replace_existing=True,
            misfire_grace_time=3600,
        )

        # Judgments: daily
        cron_j = self._parse_cron(config.SCHEDULE_JUDGMENTS)
        self.scheduler.add_job(
            self._job_judgments,
            CronTrigger(**cron_j),
            id="judgments",
            name="Court Judgment Crawler",
            replace_existing=True,
            misfire_grace_time=1800,
        )

        self._print_schedule()
        logger.info("Scheduler started. Press Ctrl+C to stop.")

        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user.")
            self.scheduler.shutdown()

    def _print_schedule(self):
        print("\n" + "=" * 65)
        print("  YAMA AI — Legal Knowledge Update Scheduler")
        print("=" * 65)
        print(f"  Mode        : APScheduler (blocking, IST timezone)")
        print(f"  Constitution: {config.SCHEDULE_CONSTITUTION} (monthly)")
        print(f"  Central Laws: {config.SCHEDULE_LAWS} (weekly)")
        print(f"  State Laws  : {config.SCHEDULE_STATE_LAWS} (weekly)")
        print(f"  Judgments   : {config.SCHEDULE_JUDGMENTS} (daily)")
        print(f"  Output dir  : {config.OUTPUT_DIR}")
        print("=" * 65 + "\n")

    def status(self):
        """Print current job statuses."""
        if not self.scheduler:
            print("Scheduler not running.")
            return
        for job in self.scheduler.get_jobs():
            next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M %Z") if job.next_run_time else "N/A"
            print(f"  {job.name:<30} next run: {next_run}")


# ═══════════════════════════════════════════════════════════════════════════
#  SIMPLE SCHEDULER (no external deps)
# ═══════════════════════════════════════════════════════════════════════════

class SimpleScheduler:
    """
    Lightweight scheduler using Python's built-in time.sleep.
    Suitable for dev/testing. Does not survive system restarts.
    For production, use APScheduler or Celery.
    """

    INTERVALS = {
        "constitution": 30 * 24 * 3600,  # 30 days
        "central_laws": 7 * 24 * 3600,   # 7 days
        "state_laws":   7 * 24 * 3600,   # 7 days
        "judgments":    24 * 3600,        # 1 day
    }

    def __init__(self):
        self.pipeline = LegalIngestionPipeline()
        self._last_run: Dict[str, float] = {}
        self._running = True

    def _should_run(self, source: str) -> bool:
        last = self._last_run.get(source, 0)
        return (time.time() - last) >= self.INTERVALS[source]

    def start(self):
        """Run the simple blocking scheduler loop."""
        print("\n" + "=" * 65)
        print("  YAMA AI — Simple Legal Knowledge Scheduler")
        print("=" * 65)
        print("  Constitution : every 30 days")
        print("  Central Laws : every 7 days")
        print("  State Laws   : every 7 days")
        print("  Judgments    : every 24 hours")
        print("  Press Ctrl+C to stop")
        print("=" * 65 + "\n")

        # Run immediately on start
        self._run_all_due()

        while self._running:
            time.sleep(60)  # Check every minute
            self._run_all_due()

    def _run_all_due(self):
        """Run all sources that are due for an update."""
        sources = {
            "constitution": self.pipeline.run_constitution,
            "central_laws": self.pipeline.run_central_laws,
            "state_laws":   self.pipeline.run_state_laws,
            "judgments":    self.pipeline.run_judgments,
        }
        for source, runner in sources.items():
            if self._should_run(source):
                logger.info("Running scheduled job: %s", source)
                try:
                    runner()
                    self._last_run[source] = time.time()
                except Exception as exc:
                    logger.error("Job %s failed: %s", source, exc)


# ═══════════════════════════════════════════════════════════════════════════
#  CELERY TASKS (optional — requires Redis/RabbitMQ)
# ═══════════════════════════════════════════════════════════════════════════

def get_celery_app():
    """
    Create and return a configured Celery application.

    Usage:
        # Start Celery worker
        celery -A scheduler.update_scheduler.celery_app worker --loglevel=info

        # Start Celery beat (scheduler)
        celery -A scheduler.update_scheduler.celery_app beat --loglevel=info
    """
    try:
        from celery import Celery
        from celery.schedules import crontab

        app = Celery(
            "yama_legal",
            broker=config.CELERY_BROKER,
            backend=config.CELERY_BACKEND,
        )

        pipeline = LegalIngestionPipeline()

        @app.task(name="yama.crawl_constitution", bind=True, max_retries=2)
        def crawl_constitution(self):
            pipeline.run_constitution()

        @app.task(name="yama.crawl_central_laws", bind=True, max_retries=2)
        def crawl_central_laws(self):
            pipeline.run_central_laws()

        @app.task(name="yama.crawl_state_laws", bind=True, max_retries=2)
        def crawl_state_laws(self):
            pipeline.run_state_laws()

        @app.task(name="yama.crawl_judgments", bind=True, max_retries=2)
        def crawl_judgments(self):
            pipeline.run_judgments()

        # Celery Beat schedule
        app.conf.beat_schedule = {
            "constitution-monthly": {
                "task": "yama.crawl_constitution",
                "schedule": crontab(hour=4, day_of_month=1),
            },
            "central-laws-weekly": {
                "task": "yama.crawl_central_laws",
                "schedule": crontab(hour=3, day_of_week=0),
            },
            "state-laws-weekly": {
                "task": "yama.crawl_state_laws",
                "schedule": crontab(hour=4, day_of_week=0),
            },
            "judgments-daily": {
                "task": "yama.crawl_judgments",
                "schedule": crontab(hour=2, minute=0),
            },
        }

        app.conf.timezone = "Asia/Kolkata"
        return app

    except ImportError:
        logger.warning("Celery not installed. Install with: pip install celery redis")
        return None


# Expose celery app at module level for Celery CLI
try:
    celery_app = get_celery_app()
except Exception:
    celery_app = None


# ═══════════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="YAMA AI — Automatic Legal Knowledge Update Scheduler",
    )
    parser.add_argument(
        "--mode",
        choices=["apscheduler", "celery", "simple"],
        default=os.getenv("SCHEDULER_MODE", "apscheduler"),
        help="Scheduler mode (default: apscheduler)",
    )
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Run crawlers immediately (once) and exit",
    )
    parser.add_argument(
        "--source",
        choices=["all", "constitution", "central_laws", "state_laws", "judgments"],
        default="all",
        help="Source to crawl when using --run-now",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Use embedded seed data (no network requests)",
    )
    parser.add_argument(
        "--states",
        nargs="*",
        help="Filter state crawl (e.g. Maharashtra Karnataka)",
    )
    parser.add_argument(
        "--acts",
        nargs="*",
        help="Filter central law crawl (e.g. BNS IPC consumer)",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show scheduler job status and exit",
    )
    args = parser.parse_args()

    pipeline = LegalIngestionPipeline()

    # ── Status ──
    if args.status:
        log_path = os.path.join(config.OUTPUT_DIR, "scheduler_log.json")
        if os.path.exists(log_path):
            with open(log_path) as f:
                log = json.load(f)
            print(f"\nLast {min(10, len(log))} scheduler runs:\n")
            for entry in log[-10:]:
                print(f"  [{entry['source']}] {entry['status']} | "
                      f"found={entry['records_found']} inserted={entry['records_inserted']} "
                      f"at={entry.get('started_at', '?')}")
        else:
            print("No scheduler log found. Run --run-now first.")
        return

    # ── Run Now (one-shot) ──
    if args.run_now:
        print(f"\nRunning one-shot ingestion: source={args.source}, offline={args.offline}\n")

        all_stats = []
        if args.source in ("all", "constitution"):
            all_stats.append(pipeline.run_constitution(offline=args.offline))
        if args.source in ("all", "central_laws"):
            all_stats.append(pipeline.run_central_laws(acts=args.acts, offline=args.offline))
        if args.source in ("all", "state_laws"):
            all_stats.append(pipeline.run_state_laws(states=args.states, offline=args.offline))
        if args.source in ("all", "judgments"):
            all_stats.append(pipeline.run_judgments(offline=args.offline))

        print("\n" + "=" * 65)
        print("  Ingestion Summary")
        print("=" * 65)
        total_found = total_inserted = 0
        for s in all_stats:
            print(f"  {s}")
            total_found += s.records_found
            total_inserted += s.records_inserted
        print("─" * 65)
        print(f"  TOTAL: found={total_found} inserted={total_inserted}")
        print("=" * 65 + "\n")
        return

    # ── Continuous Scheduler ──
    if args.mode == "apscheduler":
        engine = APSchedulerEngine()
        engine.start()

    elif args.mode == "simple":
        scheduler = SimpleScheduler()
        try:
            scheduler.start()
        except KeyboardInterrupt:
            print("\nSimple scheduler stopped.")

    elif args.mode == "celery":
        print("\nTo use Celery mode:")
        print("  # Start worker:")
        print("  celery -A scheduler.update_scheduler.celery_app worker --loglevel=info")
        print("  # Start beat (scheduler):")
        print("  celery -A scheduler.update_scheduler.celery_app beat --loglevel=info")
        print("\n  Make sure Redis is running: redis-server")
        print("  Install Celery: pip install celery redis\n")


if __name__ == "__main__":
    main()
