"""
YAMA AI — Ingestion System Configuration
Central configuration for all crawlers, pipelines, and schedulers.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List

# ── Data Source Registry ──
# Each source has a name, base URL, crawler class, and schedule

SOURCES: Dict[str, dict] = {
    "india_code": {
        "name": "India Code — Central Legislation",
        "base_url": "https://www.indiacode.nic.in",
        "description": "Official repository of all Central Acts and subordinate legislation",
        "data_types": ["central_acts", "sections", "amendments"],
        "schedule": "weekly",
    },
    "constitution": {
        "name": "Constitution of India",
        "base_url": "https://www.india.gov.in/my-government/constitution-india",
        "description": "Full text of the Constitution including articles, amendments, schedules",
        "data_types": ["articles", "amendments", "schedules"],
        "schedule": "monthly",
    },
    "supreme_court": {
        "name": "Supreme Court of India",
        "base_url": "https://main.sci.gov.in",
        "description": "Supreme Court judgments and orders",
        "data_types": ["judgments"],
        "schedule": "daily",
    },
    "ecourts": {
        "name": "eCourts Services",
        "base_url": "https://services.ecourts.gov.in",
        "description": "National portal for district and high court case status",
        "data_types": ["case_status", "orders"],
        "schedule": "daily",
    },
    "legislative_dept": {
        "name": "Legislative Department",
        "base_url": "https://legislative.gov.in",
        "description": "Bills, Acts, Ordinances from the Legislative Department",
        "data_types": ["bills", "acts", "ordinances"],
        "schedule": "weekly",
    },
    "gazette": {
        "name": "eGazette of India",
        "base_url": "https://egazette.gov.in",
        "description": "Official notifications, rules, and regulations",
        "data_types": ["notifications", "rules"],
        "schedule": "daily",
    },
}

# ── Indian States (for state-level crawling) ──

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal",
]

UNION_TERRITORIES = [
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry",
]

# ── Legal Categories Mapping ──

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "criminal": ["penal", "crime", "offence", "punishment", "murder", "theft", "assault",
                  "nyaya sanhita", "criminal", "bns", "ipc"],
    "civil": ["contract", "property", "tort", "damages", "civil", "suit", "decree"],
    "constitutional": ["constitution", "fundamental", "article", "amendment", "directive",
                        "writ", "habeas", "mandamus"],
    "consumer": ["consumer", "deficiency", "goods", "services", "complaint", "redressal"],
    "cyber": ["information technology", "cyber", "computer", "electronic", "data",
              "hacking", "it act"],
    "family": ["marriage", "divorce", "maintenance", "custody", "adoption", "dowry",
               "domestic violence", "hindu", "muslim"],
    "motor_vehicle": ["motor", "vehicle", "driving", "accident", "licence", "traffic",
                       "road", "insurance"],
    "labour": ["labour", "labor", "worker", "employment", "wage", "industrial",
               "factory", "trade union"],
    "property": ["property", "land", "registration", "transfer", "tenancy", "rent",
                  "succession", "inheritance"],
    "tax": ["tax", "income", "gst", "customs", "excise", "revenue"],
    "environmental": ["environment", "pollution", "forest", "wildlife", "water", "air"],
    "corporate": ["company", "corporate", "director", "shareholder", "insolvency",
                   "bankruptcy", "sebi"],
}

# ── Pipeline Settings ──


@dataclass
class IngestionSettings:
    """Runtime settings for the ingestion pipeline."""
    # Paths
    data_dir: str = os.path.join(os.path.dirname(__file__), "datasets")
    export_dir: str = os.path.join(os.path.dirname(__file__), "export")

    # Crawler behavior
    request_delay: float = 2.0       # seconds between HTTP requests (be polite)
    max_retries: int = 3
    request_timeout: int = 30        # seconds
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Batch sizes
    db_batch_size: int = 100         # rows per DB commit
    vector_batch_size: int = 50      # docs per ChromaDB upsert

    # Scheduler
    default_schedule: str = "weekly"

    # Logging
    log_level: str = "INFO"


ingestion_settings = IngestionSettings()
