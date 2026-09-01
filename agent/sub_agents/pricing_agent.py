import sys
import os
import json
import re
from typing import Optional, List, Dict, Any

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from tools.price_engine import calculate_dynamic_benchmark, format_inr, benchmark_models_against_vida
from tools.sandbox_manager import query_sandbox_models, load_from_sandbox
from tools.storage_manager import export_and_upload_csv, format_csv_download_section
from google.adk.agents.llm_agent import Agent

def compute_city_ev_pricing(crawled_models_json_str: str = "[]", city_name: str = "delhi_ncr") -> str:
    """
    Takes live model objects (from sandbox or web crawler) and city_name (e.g. 'Bengaluru', 'Pune', 'Delhi').
    Calculates PM E-Drive central subsidies, state EV policy subsidies, RTO tax waivers, insurance costs, and promotional savings in real time.
    Also exports the dataset to CSV and uploads to Cloud Storage bucket.
    """
    try:
        crawled_models = json.loads(crawled_models_json_str) if isinstance(crawled_models_json_str, str) and crawled_models_json_str.strip() else []
    except Exception:
        crawled_models = []

    if not crawled_models:
        crawled_models = query_sandbox_models()

    from tools.web_crawler import parse_cities
    cities = parse_cities(city_name)
    if not cities:
        cities = ["DELHI"]

    all_records = []
    for city in cities:
        city_records = calculate_dynamic_benchmark(crawled_models_json=crawled_models, city_query=city)
        all_records.extend(city_records)
    
    # Export to CSV & Cloud Storage bucket
    export_res = export_and_upload_csv(all_records, query_context=f"pricing_{'_'.join(cities[:3])}")

    formatted = []
    for r in all_records:
        formatted.append({
            "oem": r["oem"],
            "model": r["model"],
            "segment": r.get("segment", f"{r['battery_kwh']} kWh"),
            "battery_kwh": f"{r['battery_kwh']} kWh",
            "range_km": f"{r['range_km']} km",
            "base_ex_showroom": r["base_ex_showroom"],
            "pm_edrive_subsidy": r["pm_subsidy"],
            "state_ev_subsidy": r["state_subsidy"],
            "net_ex_showroom": r["net_ex_showroom"],
            "rto_cost": r["rto_cost"],
            "insurance_cost": r["insurance_cost"],
            "effective_on_road_price": r["effective_on_road_price"],
            "promotional_on_road_price": r["promotional_on_road_price"],
            "active_promotional_offers": r["active_offers"],
            "complimentary_perks": r["complimentary_perks"],
            "max_potential_savings": r["max_potential_savings"],
            "price_delta_vs_vida": r["price_delta_vs_vida"],
            "percentage_delta": f"{r['pct_delta']}%" if not r.get("is_vida_baseline") else "-",
            "value_score": r["value_score"],
            "city": r["city_name"],
            "csv_cloud_console_download": export_res.get("console_file_url"),
            "csv_storage_uri": export_res.get("gs_uri")
        })

    return json.dumps(formatted, indent=2)

def compare_competitor_with_vida(competitor_name: str = "ALL", city_name: str = "delhi_ncr") -> str:
    """
    Direct function used by CLI and tools to benchmark competitors with Hero VIDA in any city.
    """
    models = query_sandbox_models(competitor_name if competitor_name.upper() != "ALL" else None)
    if not models:
        from tools.web_crawler import run_crawler_tool
        run_crawler_tool(competitor_name, city_name, "")
        models = query_sandbox_models(competitor_name if competitor_name.upper() != "ALL" else None)
    
    records = calculate_dynamic_benchmark(crawled_models_json=models, city_query=city_name)
    return json.dumps(records, indent=2)

pricing_agent = Agent(
    name="pricing_subagent",
    model="gemini-2.5-pro",
    description="Dynamic price benchmarking agent that takes live crawled model data from sandbox and computes city tax & subsidies across 15+ Indian cities.",
    instruction="""
    You are the Price Benchmarking Sub-Agent.
    When passed live web crawl model data, extract model base prices, battery kWh, and range, then call `compute_city_ev_pricing(crawled_models_json_str, city_name)`.
    You calculate exact state subsidies (PM E-Drive + State EV policy across Delhi, Bengaluru, Mumbai, Pune, Ahmedabad, Chandigarh, etc.), RTO tax exemptions, insurance, on-road prices, active promotional offers, and price deltas against Hero VIDA baseline.
    Ensure that CSV export details and storage bucket links from the tool are preserved and returned.
    """,
    tools=[compute_city_ev_pricing]
)
