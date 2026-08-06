import sys
import os
import json
import re

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from tools.price_engine import calculate_dynamic_benchmark, format_inr
from google.adk.agents.llm_agent import Agent

def compute_city_ev_pricing(crawled_models_json_str: str = "[]", city_name: str = "delhi_ncr") -> str:
    """
    Takes live model objects (extracted dynamically from the web crawler context) and city_name (e.g. 'Bengaluru', 'Pune', 'Delhi').
    Calculates PM E-Drive central subsidies, state EV policy subsidies, RTO tax waivers, insurance costs, and promotional savings in real time.
    """
    try:
        crawled_models = json.loads(crawled_models_json_str) if isinstance(crawled_models_json_str, str) and crawled_models_json_str.strip() else []
    except Exception:
        crawled_models = []

    # Detect multi-city queries (e.g. "bengaluru and pune")
    cities = [c.strip() for c in re.split(r',| and |&', city_name.strip()) if c.strip()]
    if not cities:
        cities = ["delhi_ncr"]

    all_records = []
    for city in cities:
        city_records = calculate_dynamic_benchmark(crawled_models_json=crawled_models, city_query=city)
        all_records.extend(city_records)
    
    formatted = []
    for r in all_records:
        delta_str = "Baseline" if r.get("is_vida_baseline") else f"{'+' if r['delta_vs_vida'] > 0 else ''}{format_inr(r['delta_vs_vida'])}"
        pct_str = "-" if r.get("is_vida_baseline") else f"{'+' if r['pct_delta'] > 0 else ''}{r['pct_delta']}%"
        
        formatted.append({
            "oem": r["oem"],
            "model": r["model"],
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
            "price_delta_vs_vida": delta_str,
            "percentage_delta": pct_str,
            "value_score": r["value_score"],
            "city": r["city_name"]
        })
    return json.dumps(formatted, indent=2)

pricing_agent = Agent(
    name="pricing_subagent",
    model="gemini-2.5-pro",
    description="Dynamic price benchmarking agent that takes live crawled model data and computes city tax & subsidies.",
    instruction="""
    You are the Price Benchmarking Sub-Agent.
    When passed live web crawl model data, extract model base prices, battery kWh, and range, then call `compute_city_ev_pricing(crawled_models_json_str, city_name)`.
    You calculate exact state subsidies (PM E-Drive + State policy), RTO exemptions, on-road prices, active brand promotional offers, and price deltas.
    """,
    tools=[compute_city_ev_pricing]
)
