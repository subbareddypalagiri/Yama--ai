"""
YAMA AI — Ingestion CLI Runner
Command-line interface for running crawlers, pipelines, and exports.

Usage:
    # Run a specific crawler
    python -m ingestion run --source india_code

    # Run all crawlers
    python -m ingestion run --all

    # Load local dataset file
    python -m ingestion load --file datasets/example_laws.json

    # Export data
    python -m ingestion export --format all

    # Show scheduler status
    python -m ingestion scheduler --status

    # Start background scheduler
    python -m ingestion scheduler --start
"""

import argparse
import json
import logging
import os
import sys

# Ensure backend root is on sys.path so `app.*` and `ingestion.*` imports work
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ingestion.data_cleaner import DataCleaner
from ingestion.metadata_tagger import MetadataTagger
from ingestion.storage_pipeline import StoragePipeline
from ingestion.exporter import DataExporter
from ingestion.config import SOURCES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("yama_ai.ingestion.cli")


# ── Crawler registry ──

def _get_crawler(source_name: str):
    """Return an instantiated crawler for the given source."""
    if source_name == "india_code":
        from ingestion.crawlers.india_code_crawler import IndiaCodeCrawler
        return IndiaCodeCrawler()
    elif source_name == "constitution":
        from ingestion.crawlers.constitution_crawler import ConstitutionCrawler
        return ConstitutionCrawler()
    elif source_name in ("supreme_court", "court_judgments"):
        from ingestion.crawlers.court_crawler import SupremeCourtCrawler
        return SupremeCourtCrawler()
    elif source_name == "high_courts":
        from ingestion.crawlers.court_crawler import HighCourtCrawler
        return HighCourtCrawler()
    elif source_name == "gazette":
        from ingestion.crawlers.gazette_crawler import GazetteCrawler
        return GazetteCrawler()
    elif source_name == "state_laws":
        from ingestion.crawlers.gazette_crawler import StateLawCrawler
        return StateLawCrawler()
    else:
        raise ValueError(f"Unknown source: {source_name}. Available: {list(SOURCES.keys())}")


# ── Commands ──

def cmd_run(args):
    """Run one or more crawlers through the full pipeline."""
    sources = list(SOURCES.keys()) if args.all else [args.source]

    cleaner = DataCleaner()
    tagger = MetadataTagger()
    pipeline = StoragePipeline()

    for source_name in sources:
        print(f"\n{'='*60}")
        print(f"  Crawling: {source_name}")
        print(f"{'='*60}")

        try:
            crawler = _get_crawler(source_name)
            with crawler:
                raw_records = crawler.crawl()

            print(f"  ✅ Crawled {len(raw_records)} raw records")

            # Clean
            dicts = [r.to_dict() for r in raw_records]
            cleaned, skipped = cleaner.clean_batch(dicts)
            cleaned = cleaner.deduplicate(cleaned)
            print(f"  🧹 Cleaned: {len(cleaned)} records ({skipped} skipped)")

            # Tag
            tagged = tagger.tag_batch(cleaned)
            print(f"  🏷️  Tagged: {len(tagged)} records")

            # Store
            stats = pipeline.store(tagged, source_name=source_name)
            print(f"  💾 Stored: {stats['inserted']} new, {stats['updated']} updated, "
                  f"{stats['skipped']} unchanged")
            print(f"  📚 Vector indexed: {stats.get('vector_indexed', 0)} documents")

        except Exception as e:
            logger.error(f"Failed to process {source_name}: {e}")
            print(f"  ❌ Error: {e}")

    print(f"\n{'='*60}")
    print("  Pipeline complete!")
    print(f"{'='*60}")


def cmd_load(args):
    """Load a local JSON dataset file into the database."""
    filepath = args.file
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        sys.exit(1)

    print(f"📂 Loading dataset from: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Support both {"laws": [...]} and bare [...]
    records = data.get("laws", data) if isinstance(data, dict) else data

    if not isinstance(records, list):
        print("❌ Invalid format: expected a list of law records")
        sys.exit(1)

    print(f"  Found {len(records)} records")

    cleaner = DataCleaner()
    tagger = MetadataTagger()
    pipeline = StoragePipeline()

    cleaned, skipped = cleaner.clean_batch(records)
    cleaned = cleaner.deduplicate(cleaned)
    print(f"  🧹 Cleaned: {len(cleaned)} records ({skipped} skipped)")

    tagged = tagger.tag_batch(cleaned)
    print(f"  🏷️  Tagged: {len(tagged)} records")

    stats = pipeline.store(tagged, source_name=f"file:{os.path.basename(filepath)}")
    print(f"  💾 Stored: {stats['inserted']} new, {stats['updated']} updated, "
          f"{stats['skipped']} unchanged")
    print(f"  📚 Vector indexed: {stats.get('vector_indexed', 0)} documents")
    print("✅ Load complete!")


def cmd_export(args):
    """Export data from the database to files."""
    exporter = DataExporter()
    fmt = args.format

    print(f"📤 Exporting data in format: {fmt}")

    if fmt == "all":
        paths = exporter.export_all()
        for fmt_name, path in paths.items():
            print(f"  ✅ {fmt_name}: {path}")
    elif fmt == "json":
        path = exporter.export_json()
        print(f"  ✅ JSON: {path}")
    elif fmt == "csv":
        path = exporter.export_csv()
        print(f"  ✅ CSV: {path}")
    elif fmt == "sql":
        path = exporter.export_sql()
        print(f"  ✅ SQL: {path}")
    elif fmt == "embeddings":
        path = exporter.export_embeddings()
        print(f"  ✅ Embeddings: {path}")
    else:
        print(f"❌ Unknown format: {fmt}")
        sys.exit(1)

    print("✅ Export complete!")


def cmd_scheduler(args):
    """Manage the background scheduler."""
    from ingestion.scheduler import IngestionScheduler

    scheduler = IngestionScheduler()

    if args.status:
        print("\n📅 Ingestion Scheduler — Task Status:")
        print(f"{'Task':<30} {'Enabled':<10} {'Interval':<12} {'Runs':<6} {'Last Error'}")
        print("-" * 90)
        for task in scheduler.get_status():
            err = task["last_error"][:30] + "..." if task["last_error"] else "None"
            print(f"{task['name']:<30} {str(task['enabled']):<10} "
                  f"{task['interval_hours']:<12.0f}h {task['run_count']:<6} {err}")
        return

    if args.run_task:
        print(f"▶️  Running task: {args.run_task}")
        scheduler.run_now(args.run_task)
        print("✅ Task completed")
        return

    if args.start:
        print("🚀 Starting background scheduler...")
        print("   Press Ctrl+C to stop.")
        scheduler.start()
        try:
            import time
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            scheduler.stop()
            print("\n⏹️  Scheduler stopped.")
        return


def cmd_info(args):
    """Show information about available data sources."""
    print("\n📚 YAMA AI — Available Data Sources:\n")
    for key, src in SOURCES.items():
        print(f"  {key}")
        print(f"    Name:     {src['name']}")
        print(f"    URL:      {src['base_url']}")
        print(f"    Types:    {', '.join(src['data_types'])}")
        print(f"    Schedule: {src['schedule']}")
        print()


# ── Argument Parser ──

def main():
    parser = argparse.ArgumentParser(
        prog="python -m ingestion",
        description="YAMA AI — Legal Knowledge Ingestion System",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # run
    p_run = subparsers.add_parser("run", help="Run crawlers through the full pipeline")
    p_run.add_argument("--source", type=str, help="Source to crawl (e.g., india_code)")
    p_run.add_argument("--all", action="store_true", help="Crawl all sources")
    p_run.set_defaults(func=cmd_run)

    # load
    p_load = subparsers.add_parser("load", help="Load a local JSON dataset file")
    p_load.add_argument("--file", type=str, required=True, help="Path to JSON file")
    p_load.set_defaults(func=cmd_load)

    # export
    p_export = subparsers.add_parser("export", help="Export data to files")
    p_export.add_argument("--format", type=str, default="all",
                          choices=["json", "csv", "sql", "embeddings", "all"],
                          help="Export format")
    p_export.set_defaults(func=cmd_export)

    # scheduler
    p_sched = subparsers.add_parser("scheduler", help="Manage the ingestion scheduler")
    p_sched.add_argument("--status", action="store_true", help="Show task status")
    p_sched.add_argument("--start", action="store_true", help="Start background scheduler")
    p_sched.add_argument("--run-task", type=str, help="Run a specific task now")
    p_sched.set_defaults(func=cmd_scheduler)

    # info
    p_info = subparsers.add_parser("info", help="Show available data sources")
    p_info.set_defaults(func=cmd_info)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
