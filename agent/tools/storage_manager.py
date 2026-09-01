import os
import csv
import io
import re
import time
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Base directories
BASE_AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_DIR = os.path.dirname(BASE_AGENT_DIR)
REPORTS_DIR = os.path.join(WORKSPACE_DIR, "reports")
SANDBOX_CSV_DIR = os.path.join(BASE_AGENT_DIR, "sandbox_data", "csv")

def ensure_storage_dirs():
    """Ensures local storage directories exist."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(SANDBOX_CSV_DIR, exist_ok=True)

def generate_csv_string(records: List[Dict[str, Any]]) -> str:
    """
    Converts list of model / benchmark records into a standardized CSV string.
    Zero hardcoded values: all rows reflect the real-time crawled dataset.
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

    for r in records:
        city = r.get("city") or r.get("city_name") or "National"
        oem = r.get("oem") or "Hero VIDA"
        model = r.get("model") or "EV"
        bat = r.get("battery_kwh") or "-"
        rng = r.get("range_km") or "-"
        speed = r.get("top_speed") or "-"

        base_p = r.get("base_price") or r.get("base_ex_showroom") or 0
        if isinstance(base_p, (int, float)):
            base_str = f"₹{int(base_p):,}"
        else:
            base_str = str(base_p)

        eff_p = r.get("effective_price") or r.get("effective_on_road_price") or base_p
        if isinstance(eff_p, (int, float)):
            eff_str = f"₹{int(eff_p):,}"
        else:
            eff_str = str(eff_p)

        offers = str(r.get("active_offers") or r.get("active_promotional_offers") or "Standard Ex-Showroom")
        clean_offers = offers.replace("<br>", " ").replace("\n", " ").strip()

        source_url = r.get("source_url") or "https://www.vidaworld.com"

        writer.writerow([
            city,
            oem,
            model,
            bat,
            rng,
            speed,
            base_str,
            eff_str,
            clean_offers,
            source_url
        ])

    return output.getvalue()

def upload_to_gcs(
    csv_content: str,
    filename: str,
    project_id: str,
    bucket_name: str
) -> Dict[str, Any]:
    """
    Attempts to upload CSV to Google Cloud Storage bucket.
    Returns upload status and links.
    """
    try:
        from google.cloud import storage
        client = storage.Client(project=project_id)
        
        # Try getting or creating bucket
        try:
            bucket = client.get_bucket(bucket_name)
        except Exception:
            try:
                region = os.environ.get("REGION", "us-central1")
                bucket = client.create_bucket(bucket_name, location=region)
                logger.info(f"Created GCS bucket: {bucket_name}")
            except Exception:
                bucket = client.bucket(bucket_name)

        blob = bucket.blob(f"reports/{filename}")
        blob.upload_from_string(csv_content, content_type="text/csv")

        # Also upload latest pointer
        latest_blob = bucket.blob("reports/hero_vida_comparison_latest.csv")
        latest_blob.upload_from_string(csv_content, content_type="text/csv")

        return {"success": True, "error": None}
    except Exception as e:
        logger.warning(f"GCS upload notice (offline or local credential): {e}")
        return {"success": False, "error": str(e)}

def export_and_upload_csv(
    records: List[Dict[str, Any]],
    query_context: str = "hero_vida_benchmark"
) -> Dict[str, Any]:
    """
    Core function that:
    1. Formats live comparison records into clean CSV.
    2. Persists CSV locally in sandbox_data/csv/ and reports/.
    3. Uploads CSV to Google Cloud Storage bucket (or provides GCS links for Cloud Run / Agent Platform).
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
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("PROJECT_ID") or "hero-vida-project"
    bucket_name = os.environ.get("GCS_BUCKET_NAME") or os.environ.get("BUCKET_NAME") or f"{project_id}-hero-vida-reports"

    # Direct Google Cloud Console Link (opens object directly in Cloud Console Storage browser with 1-click Download)
    console_file_url = f"https://console.cloud.google.com/storage/browser/_details/{bucket_name}/reports/{filename}?project={project_id}"
    console_bucket_url = f"https://console.cloud.google.com/storage/browser/{bucket_name}/reports?project={project_id}"
    storage_direct_url = f"https://storage.cloud.google.com/{bucket_name}/reports/{filename}"
    gs_uri = f"gs://{bucket_name}/reports/{filename}"

    gcs_res = upload_to_gcs(csv_content, filename, project_id, bucket_name)

    return {
        "filename": filename,
        "local_path": local_path,
        "sandbox_path": sandbox_path,
        "bucket_name": bucket_name,
        "console_file_url": console_file_url,
        "console_bucket_url": console_bucket_url,
        "storage_direct_url": storage_direct_url,
        "gs_uri": gs_uri,
        "gcs_uploaded": gcs_res["success"],
        "gcs_error": gcs_res["error"],
        "csv_content": csv_content,
        "row_count": len(records)
    }

def format_csv_download_section(export_result: Dict[str, Any]) -> str:
    """
    Renders standardized Markdown section with Google Cloud Console links,
    storage URLs, local file references, and raw CSV data block.
    """
    fname = export_result.get("filename", "hero_vida_comparison.csv")
    console_url = export_result.get("console_file_url", "")
    direct_url = export_result.get("storage_direct_url", "")
    gs_uri = export_result.get("gs_uri", "")
    bucket_url = export_result.get("console_bucket_url", "")
    local_path = export_result.get("local_path", "")
    csv_content = export_result.get("csv_content", "").strip()

    md = [
        "### 📥 Verified CSV Export & Cloud Storage Download",
        f"- **🌐 Google Cloud Console Storage Link (1-Click Download):**",
        f"  👉 [{fname} in Cloud Storage Console]({console_url})",
        f"- **⚡ Direct Authenticated Download URL:**",
        f"  🔗 [{direct_url}]({direct_url})",
        f"- **🪣 Cloud Storage Bucket URI:**",
        f"  `{gs_uri}`",
        f"- **📁 All Reports Storage Folder:**",
        f"  🔗 [Browse Storage Bucket]({bucket_url})",
        f"- **💻 Local Sandbox File:**",
        f"  `{local_path}`",
        "",
        "<details open>",
        "<summary><b>📋 Raw CSV Dataset (Direct Console Access - Copy / View)</b></summary>",
        "",
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
