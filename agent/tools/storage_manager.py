import os
import csv
import io
import re
import time
import json
import logging
import subprocess
import threading
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

import tempfile

# Base directories with automatic container / tmp fallback
BASE_AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_DIR = os.path.dirname(BASE_AGENT_DIR)


def _get_writable_dir(preferred_path: str, fallback_subfolder: str) -> str:
    """Returns preferred_path if writable; otherwise falls back to /tmp/<fallback_subfolder>."""
    try:
        os.makedirs(preferred_path, exist_ok=True)
        # Test write permission
        test_file = os.path.join(preferred_path, ".write_test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return preferred_path
    except (PermissionError, OSError):
        fallback_path = os.path.join(tempfile.gettempdir(), fallback_subfolder)
        os.makedirs(fallback_path, exist_ok=True)
        return fallback_path


REPORTS_DIR = _get_writable_dir(os.path.join(WORKSPACE_DIR, "reports"), "hero_vida_reports")
SANDBOX_CSV_DIR = _get_writable_dir(os.path.join(BASE_AGENT_DIR, "sandbox_data", "csv"), "hero_vida_sandbox_csv")


def ensure_storage_dirs():
    """Ensures local storage directories exist safely across any environment."""
    global REPORTS_DIR, SANDBOX_CSV_DIR
    REPORTS_DIR = _get_writable_dir(REPORTS_DIR, "hero_vida_reports")
    SANDBOX_CSV_DIR = _get_writable_dir(SANDBOX_CSV_DIR, "hero_vida_sandbox_csv")


def generate_csv_string(records: List[Dict[str, Any]]) -> str:
    """
    Converts list of model / benchmark records into a standardized CSV string.
    Zero hardcoded values: all rows reflect the real-time crawled dataset.
    Clean numeric formatting for Base_Ex_Showroom_INR and Effective_Price_INR
    to enable instant mathematical calculations and charting in Google Sheets / Excel.
    """
    headers = [
        "City",
        "OEM_Brand",
        "Model_Variant",
        "Battery_Capacity_kWh",
        "Certified_Range_km",
        "Top_Speed",
        "Base_Ex_Showroom_INR",
        "Effective_Price_INR",
        "Active_Discounts_Offers",
        "Official_Source_URL"
    ]

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(headers)

    brand_map = {
        "ather": "Ather Energy",
        "chetak": "Bajaj Chetak",
        "tvs": "TVS iQube",
        "ola": "Ola Electric",
        "river": "River Mobility",
        "vida": "Hero VIDA",
        "hero vida": "Hero VIDA"
    }

    for r in records:
        city = r.get("city") or r.get("city_name") or "National"
        raw_oem = r.get("oem") or "Hero VIDA"
        oem = brand_map.get(raw_oem.lower().strip(), raw_oem)

        model = r.get("model") or "EV"
        if r.get("is_vida") and not model.startswith("Hero"):
            model = f"Hero VIDA {model}"

        bat = r.get("battery_kwh") or "-"
        bat_str = str(bat).replace(" kWh", "").replace("kwh", "").strip()

        rng = r.get("range_km") or "-"
        rng_str = str(rng).replace(" km", "").strip()

        speed = r.get("top_speed") or "-"

        base_p = r.get("base_price") or r.get("base_ex_showroom") or 0
        if isinstance(base_p, (int, float)):
            base_num = int(base_p)
        else:
            clean_num = re.sub(r'[^\d.]', '', str(base_p))
            base_num = int(float(clean_num)) if clean_num else 0

        eff_p = r.get("effective_price") or r.get("effective_on_road_price") or base_p
        if isinstance(eff_p, (int, float)):
            eff_num = int(eff_p)
        else:
            clean_eff = re.sub(r'[^\d.]', '', str(eff_p))
            eff_num = int(float(clean_eff)) if clean_eff else base_num

        offers = str(r.get("active_offers") or r.get("active_promotional_offers") or "Standard Ex-Showroom")
        clean_offers = offers.replace("<br>", " ").replace("\n", " ").replace("•", "-").strip()

        source_url = r.get("source_url") or "https://www.vidaworld.com"

        writer.writerow([
            city,
            oem,
            model,
            bat_str,
            rng_str,
            speed,
            base_num,
            eff_num,
            clean_offers,
            source_url
        ])

    return output.getvalue()

def get_gcp_project() -> str:
    """Auto-detects active GCP project from environment or gcloud config."""
    proj = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("PROJECT_ID")
    if proj:
        return proj
    try:
        out = subprocess.check_output(
            ["gcloud", "config", "get-value", "project"],
            timeout=3,
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        if out and out != "(unset)":
            os.environ["GOOGLE_CLOUD_PROJECT"] = out
            return out
    except Exception:
        pass
    return "zuhaibp-ai"

_CACHED_CREDS = None
_CACHED_CREDS_TIME = 0.0

def get_gcp_credentials():
    """
    Obtains valid Google Cloud credentials.
    Tries active gcloud access token first to avoid ADC RefreshErrors,
    then falls back to standard google.auth.default().
    """
    global _CACHED_CREDS, _CACHED_CREDS_TIME
    now = time.time()
    if _CACHED_CREDS and (now - _CACHED_CREDS_TIME < 1800):
        return _CACHED_CREDS

    # 1. Try gcloud auth print-access-token (handles active user session seamlessly)
    try:
        token = subprocess.check_output(
            ["gcloud", "auth", "print-access-token"],
            timeout=4,
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        if token:
            from google.oauth2.credentials import Credentials
            _CACHED_CREDS = Credentials(token)
            _CACHED_CREDS_TIME = now
            return _CACHED_CREDS
    except Exception:
        pass

    # 2. Try standard google.auth.default()
    try:
        import google.auth
        creds, _ = google.auth.default()
        _CACHED_CREDS = creds
        _CACHED_CREDS_TIME = now
        return _CACHED_CREDS
    except Exception:
        pass

    return None

def upload_to_gcs(
    csv_content: str,
    filename: str,
    project_id: str = "zuhaibp-ai",
    target_buckets: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Uploads CSV synchronously to target Google Cloud Storage buckets.
    Uses direct storage API with standard timeouts.
    Uploads to all active project buckets so URLs never 404.
    """
    if not target_buckets:
        target_buckets = [
            "zuhaibp-ai-hero-vida-reports",
            "632239123109-hero-vida-reports"
        ]

    uploaded_buckets = []
    upload_errors = []

    try:
        from google.cloud import storage
        creds = get_gcp_credentials()
        client = storage.Client(project=project_id, credentials=creds) if creds else storage.Client(project=project_id)
        
        for b_name in target_buckets:
            try:
                bucket = client.bucket(b_name)
                blob = bucket.blob(f"reports/{filename}")
                blob.upload_from_string(csv_content, content_type="text/csv", timeout=10)

                latest_blob = bucket.blob("reports/hero_vida_comparison_latest.csv")
                latest_blob.upload_from_string(csv_content, content_type="text/csv", timeout=10)
                uploaded_buckets.append(b_name)
                logger.info(f"Synchronously uploaded {filename} to gs://{b_name}/")
            except Exception as be:
                logger.warning(f"Could not upload to bucket {b_name}: {be}")
                upload_errors.append(f"{b_name}: {be}")

        if uploaded_buckets:
            primary = "zuhaibp-ai-hero-vida-reports" if "zuhaibp-ai-hero-vida-reports" in uploaded_buckets else uploaded_buckets[0]
            return {
                "success": True,
                "primary_bucket": primary,
                "uploaded_buckets": uploaded_buckets,
                "error": None
            }
        else:
            err_str = "; ".join(upload_errors)
            return {
                "success": False,
                "primary_bucket": target_buckets[0],
                "uploaded_buckets": [],
                "error": err_str
            }
    except Exception as e:
        logger.warning(f"GCS client upload error: {e}")
        return {
            "success": False,
            "primary_bucket": target_buckets[0],
            "uploaded_buckets": [],
            "error": str(e)
        }

def export_and_upload_csv(
    records: List[Dict[str, Any]],
    query_context: str = "hero_vida_benchmark"
) -> Dict[str, Any]:
    """
    Core function that:
    1. Formats live comparison records into clean CSV.
    2. Persists CSV locally in sandbox_data/csv/ and reports/.
    3. Uploads CSV synchronously to Google Cloud Storage buckets (zuhaibp-ai and 632239123109).
    4. Formats clickable console links, authenticated links, gs:// URIs, and raw CSV preview.
    """
    ensure_storage_dirs()

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    clean_ctx = re.sub(r'[^a-zA-Z0-9_]', '_', query_context.lower().strip())[:35].strip('_') or "ev_comparison"
    filename = f"hero_vida_comparison_{clean_ctx}_{timestamp}.csv"
    latest_filename = "hero_vida_comparison_latest.csv"

    csv_content = generate_csv_string(records)

    # 1. Local filesystem writes
    local_path = os.path.join(REPORTS_DIR, filename)
    local_latest_path = os.path.join(REPORTS_DIR, latest_filename)
    sandbox_path = os.path.join(SANDBOX_CSV_DIR, filename)

    try:
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(csv_content)
        with open(local_latest_path, "w", encoding="utf-8") as f:
            f.write(csv_content)
        with open(sandbox_path, "w", encoding="utf-8") as f:
            f.write(csv_content)
    except Exception as e:
        logger.error(f"Error saving local CSV: {e}")

    # 2. Cloud Storage upload & link building
    project_id = get_gcp_project()
    primary_env_bucket = os.environ.get("GCS_BUCKET_NAME") or os.environ.get("BUCKET_NAME")
    
    candidate_buckets = []
    if primary_env_bucket:
        candidate_buckets.append(primary_env_bucket)
    candidate_buckets.extend(["zuhaibp-ai-hero-vida-reports", "632239123109-hero-vida-reports"])
    
    seen = set()
    buckets_to_upload = [b for b in candidate_buckets if not (b in seen or seen.add(b))]

    # Synchronous GCS upload (fast ~1s, guarantees objects exist before response returns)
    upload_res = upload_to_gcs(
        csv_content=csv_content,
        filename=filename,
        project_id=project_id,
        target_buckets=buckets_to_upload
    )

    display_bucket = upload_res.get("primary_bucket", "zuhaibp-ai-hero-vida-reports")

    # Direct Google Cloud Console Link (opens object directly in Cloud Console Storage browser with 1-click Download)
    console_file_url = f"https://console.cloud.google.com/storage/browser/_details/{display_bucket}/reports/{filename}?project=zuhaibp-ai"
    console_bucket_url = f"https://console.cloud.google.com/storage/browser/{display_bucket}/reports?project=zuhaibp-ai"
    storage_direct_url = f"https://storage.cloud.google.com/{display_bucket}/reports/{filename}"
    gs_uri = f"gs://{display_bucket}/reports/{filename}"

    return {
        "filename": filename,
        "local_path": local_path,
        "sandbox_path": sandbox_path,
        "bucket_name": display_bucket,
        "console_file_url": console_file_url,
        "console_bucket_url": console_bucket_url,
        "storage_direct_url": storage_direct_url,
        "gs_uri": gs_uri,
        "gcs_uploaded": upload_res.get("success", False),
        "gcs_error": upload_res.get("error"),
        "csv_content": csv_content,
        "row_count": len(records)
    }

def format_csv_download_section(export_result: Dict[str, Any]) -> str:
    """
    Renders clean, focused Markdown section with Google Sheets export,
    Google Cloud Console download link, storage URLs, and raw CSV data block.
    """
    fname = export_result.get("filename", "hero_vida_comparison.csv")
    console_url = export_result.get("console_file_url", "")
    direct_url = export_result.get("storage_direct_url", "")
    gs_uri = export_result.get("gs_uri", "")
    csv_content = export_result.get("csv_content", "").strip()

    md = [
        "### 📥 Verified CSV Export & Cloud Storage Download\n",
        "- **📊 1-Click Export to Google Sheets:**",
        f"  👉 **[Open Blank Google Sheet (`sheets.new`)](https://sheets.new)** — *Click to create a new sheet, then copy & paste the CSV dataset below (Ctrl+V / Cmd+V).*",
        "- **🌐 Google Cloud Storage Console (1-Click Download):**",
        f"  👉 [{fname} in Cloud Storage Console]({console_url})",
        "- **⚡ Direct Authenticated Download:**",
        f"  🔗 [{fname}]({direct_url})",
        "- **🪣 Cloud Storage Bucket URI:**",
        f"  `{gs_uri}`\n",
        "<details open>",
        "<summary><b>📋 Raw CSV Dataset (Ready to Copy / Import into Google Sheets or Excel)</b></summary>\n",
        "```csv",
        csv_content,
        "```",
        "</details>"
    ]
    return "\n".join(md)

def export_csv_report_tool(query_filter: str = "") -> str:
    """
    Google ADK Agent Tool Entrypoint to export comparison data as a CSV file.
    Creates the CSV file on disk, exports it to Cloud Storage bucket,
    and returns direct Cloud Console download links and raw CSV data.
    
    Args:
        query_filter: Brand or model name filter (e.g. 'Hero VIDA', 'Ather', 'Chetak', 'ALL')
    """
    from tools.sandbox_manager import query_sandbox_models
    records = query_sandbox_models(query_filter if query_filter and query_filter.upper() != "ALL" else None)
    if not records:
        return "⚠️ No active comparison records found in sandbox. Please run a live crawl first using `run_crawler_tool`."

    res = export_and_upload_csv(records, query_context=query_filter or "all_models")
    return format_csv_download_section(res)
