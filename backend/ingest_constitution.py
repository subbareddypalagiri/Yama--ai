import os
import sys
import json
import urllib.request
import hashlib

# Ensure backend root is on sys.path
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ingestion.storage_pipeline import StoragePipeline

def compute_hash(act_name, section_number, title, description) -> str:
    payload = f"{act_name}|{section_number}|{title}|{description}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def extract_keywords(title: str, description: str) -> str:
    combined = f"{title} {description}".lower()
    stop_words = {"the", "of", "and", "in", "to", "a", "is", "or", "for", "be",
                  "an", "as", "by", "on", "at", "it", "that", "this", "with",
                  "any", "shall", "may", "such", "which", "who", "not", "from",
                  "under", "been", "has", "have", "his", "her", "its", "state"}
    import re
    words = re.findall(r"[a-z]{3,}", combined)
    keywords = [w for w in dict.fromkeys(words) if w not in stop_words][:15]
    return ", ".join(keywords)

def main():
    # Attempt to download from civictech-India main branch, then master
    urls = [
        "https://raw.githubusercontent.com/civictech-India/constitution-of-india/main/constitution_of_india.json",
        "https://raw.githubusercontent.com/civictech-India/constitution-of-india/master/constitution_of_india.json"
    ]
    
    data = None
    for url in urls:
        try:
            print(f"Downloading from {url}...")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8')
            data = json.loads(html)
            print(f"Successfully downloaded {len(data)} articles!")
            break
        except Exception as e:
            print(f"Failed to download from {url}: {e}")
            
    if data is None:
        print("Error: Could not retrieve Constitution JSON data from GitHub.")
        sys.exit(1)
        
    records = []
    for item in data:
        art_num = item.get("article")
        title = item.get("title", "").strip()
        description = item.get("description", "").strip()
        
        if art_num == 0 or title.lower() == "preamble":
            section_number = "Preamble"
        else:
            section_number = f"Article {art_num}"
            
        if not title:
            title = section_number
            
        content_hash = compute_hash("Constitution of India", section_number, title, description)
        keywords = extract_keywords(title, description)
        
        records.append({
            "act_name": "Constitution of India",
            "section_number": section_number,
            "title": title,
            "description": description,
            "keywords": keywords,
            "category": "constitutional",
            "jurisdiction": "central",
            "law_type": "article",
            "source_url": "https://legislative.gov.in/constitution-of-india",
            "content_hash": content_hash,
            "is_active": True
        })
        
    print(f"Prepared {len(records)} records for pipeline storage.")
    pipeline = StoragePipeline()
    stats = pipeline.store(records, source_name="constitution")
    
    print("\n🎉 Ingestion Complete:")
    print(f"   Inserted: {stats['inserted']} new articles")
    print(f"   Updated: {stats['updated']} changed articles")
    print(f"   Skipped: {stats['skipped']} unchanged articles")
    print(f"   Vector Indexed: {stats['vector_indexed']} total sections")

if __name__ == "__main__":
    main()
