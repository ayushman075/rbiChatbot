import time
from scraper.rbi_scraper import scrape_rbi_documents
from utils.index_builder import IndexUpdater
import os
import json
import hashlib

def compute_md5(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def get_existing_ids(path="data/faiss_index/processed_ids.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            return set(json.load(f))
    return set()

def save_processed_ids(ids, path="data/faiss_index/processed_ids.json"):
    with open(path, "w") as f:
        json.dump(list(ids), f)

def run_update():
    print("🔄 Running RBI auto update...")
    all_docs = scrape_rbi_documents(limit=50)  # get latest

    processed_ids = get_existing_ids()
    new_docs = []

    for doc in all_docs:
        doc_id = compute_md5(doc["content"])
        if doc_id not in processed_ids:
            doc["id"] = doc_id
            new_docs.append(doc)
            processed_ids.add(doc_id)

    if new_docs:
        print(f"✅ {len(new_docs)} new documents found.")
        updater = IndexUpdater()
        updater.add_documents(new_docs)
    else:
        print("⚠️ No new documents found.")

    save_processed_ids(processed_ids)
    print("✅ Update complete.\n")

# Run every 6 hours
if __name__ == "__main__":
    while True:
        run_update()
        time.sleep(6 * 60 * 60)  # 6 hours
