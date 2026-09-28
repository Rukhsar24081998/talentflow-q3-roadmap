#!/usr/bin/env python3
"""
scripts/fetch_airtable.py

Connects to the TalentFlow - Acme Corp Airtable base and extracts all records
across all eight tables, handling rate limits, pagination, and local caching.

Security: Never logs or exposes the API token.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

# Tables to extract
TABLES = [
    "Departments",
    "People",
    "Job Openings",
    "Candidates",
    "Applications",
    "Interviews",
    "Offers",
    "Findings",
]

# Throttling & Retry configuration
REQUEST_DELAY = 0.25  # 250ms = 4 req/sec maximum (below the 5 req/sec limit)
MAX_RETRIES = 5
LOCKOUT_WAIT_SECONDS = 30.0

def load_dotenv(dotenv_path=".env"):
    """Simple parser to load .env into os.environ without third-party dependencies."""
    path = Path(dotenv_path)
    if not path.is_file():
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception as e:
        print(f"[WARN] Could not parse .env file: {e}", file=sys.stderr)

def get_credentials():
    """Retrieve and validate Airtable credentials from environment."""
    load_dotenv()
    token = os.environ.get("AIRTABLE_TOKEN")
    base_id = os.environ.get("AIRTABLE_BASE_ID")

    if not token or not base_id:
        missing = []
        if not token:
            missing.append("AIRTABLE_TOKEN")
        if not base_id:
            missing.append("AIRTABLE_BASE_ID")
        print(f"[ERROR] Missing required configuration: {', '.join(missing)}", file=sys.stderr)
        print("[ERROR] Please configure them in your environment or a local .env file.", file=sys.stderr)
        return None, None

    return token.strip(), base_id.strip()

def sanitize_filename(table_name):
    """Convert table name to a clean snake_case filename."""
    return table_name.lower().replace(" ", "_") + ".json"

def fetch_table(table_name, base_id, token, output_dir):
    """
    Fetch all pages for a given table using Airtable's offset pagination.
    Uses GET requests only. Preserves full records without modification.
    """
    encoded_table = urllib.parse.quote(table_name)
    base_url = f"https://api.airtable.com/v0/{base_id}/{encoded_table}"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "TalentFlow-DataExtractor/1.0",
    }

    records = []
    offset = None
    page_count = 0
    errors = []
    pagination_completed = False

    print(f"[*] Starting extraction for table: {table_name}")

    while True:
        page_count += 1
        query_params = {"pageSize": "100"}
        if offset:
            query_params["offset"] = offset

        url = f"{base_url}?{urllib.parse.urlencode(query_params)}"

        retries = 0
        success = False
        response_data = None

        while retries <= MAX_RETRIES:
            try:
                time.sleep(REQUEST_DELAY)  # Proactive rate-limit throttle
                req = urllib.request.Request(url, headers=headers, method="GET")
                with urllib.request.urlopen(req, timeout=30) as resp:
                    if resp.status == 200:
                        response_data = json.loads(resp.read().decode("utf-8"))
                        success = True
                        break
                    else:
                        raise urllib.error.HTTPError(
                            url, resp.status, f"Unexpected HTTP status {resp.status}", resp.headers, None
                        )

            except urllib.error.HTTPError as e:
                if e.code == 429:
                    retries += 1
                    retry_after = e.headers.get("Retry-After")
                    wait_time = float(retry_after) if retry_after else LOCKOUT_WAIT_SECONDS
                    print(
                        f"    [!] Rate limited (429) on {table_name} page {page_count}. "
                        f"Waiting {wait_time}s (attempt {retries}/{MAX_RETRIES})...",
                        file=sys.stderr
                    )
                    time.sleep(wait_time)
                elif e.code in (500, 502, 503, 504):
                    retries += 1
                    backoff = 2 ** retries
                    print(
                        f"    [!] Server error ({e.code}) on {table_name} page {page_count}. "
                        f"Retrying in {backoff}s (attempt {retries}/{MAX_RETRIES})...",
                        file=sys.stderr
                    )
                    time.sleep(backoff)
                else:
                    error_msg = f"HTTP {e.code} error fetching {table_name}: {e.reason}"
                    print(f"    [ERROR] {error_msg}", file=sys.stderr)
                    errors.append(error_msg)
                    break
            except Exception as e:
                retries += 1
                backoff = 2 ** retries
                print(
                    f"    [!] Network error on {table_name} page {page_count}: {e}. "
                    f"Retrying in {backoff}s...",
                    file=sys.stderr
                )
                time.sleep(backoff)

        if not success or response_data is None:
            err = f"Failed to fetch page {page_count} for table {table_name} after retries."
            errors.append(err)
            print(f"    [ERROR] {err}", file=sys.stderr)
            break

        page_records = response_data.get("records", [])
        records.extend(page_records)
        offset = response_data.get("offset")

        print(f"    Page {page_count}: Retrieved {len(page_records)} records (Cumulative: {len(records)})")

        if not offset:
            pagination_completed = True
            break

    # Save records to JSON
    filename = sanitize_filename(table_name)
    output_path = output_dir / filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    status = "SUCCESS" if (pagination_completed and not errors) else "PARTIAL_OR_FAILED"

    print(f"[✓] Completed {table_name}: {len(records)} total records saved to {output_path.name}\n")

    return {
        "table_name": table_name,
        "filename": filename,
        "total_records": len(records),
        "pages_retrieved": page_count,
        "pagination_completed": pagination_completed,
        "status": status,
        "errors": errors,
    }

def main():
    token, base_id = get_credentials()
    if not token or not base_id:
        sys.exit(1)

    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    start_time = datetime.now(timezone.utc).isoformat()
    table_summaries = {}
    total_records = 0
    all_successful = True

    print("==================================================")
    print(" TalentFlow Airtable Data Extractor")
    print(f" Base ID: {base_id}")
    print(f" Tables to fetch: {len(TABLES)}")
    print(f" Output directory: {output_dir.resolve()}")
    print("==================================================\n")

    for table in TABLES:
        summary = fetch_table(table, base_id, token, output_dir)
        table_summaries[table] = summary
        total_records += summary["total_records"]
        if summary["status"] != "SUCCESS" or not summary["pagination_completed"]:
            all_successful = False

    end_time = datetime.now(timezone.utc).isoformat()

    manifest = {
        "extraction_started_at": start_time,
        "extraction_completed_at": end_time,
        "base_id": base_id,
        "total_records_all_tables": total_records,
        "all_tables_successful": all_successful,
        "tables": table_summaries,
    }

    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("==================================================")
    print(" Extraction Manifest Summary")
    print(f" Total records across all tables: {total_records}")
    print(f" All paginations verified complete: {all_successful}")
    print(f" Manifest written to: {manifest_path}")
    print("==================================================")

if __name__ == "__main__":
    main()
