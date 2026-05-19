#!/bin/bash
echo "=== YAMA AI — Legal Data Crawler v2 ==="
echo "Choose source:"
echo "1) All sources (full A-to-Z)"
echo "2) Indian Kanoon only (judgments)"
echo "3) India Code only (acts)"
echo "4) Dry run (no database)"
read -p "Enter choice (1-4): " choice

case $choice in
  1) python -m data_pipeline.crawler_v2 --source all ;;
  2) python -m data_pipeline.crawler_v2 --source indian_kanoon --pages 200 ;;
  3) python -m data_pipeline.crawler_v2 --source india_code ;;
  4) python -m data_pipeline.crawler_v2 --source all --no-store ;;
esac