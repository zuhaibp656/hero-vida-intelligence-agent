import sys
import os
import json

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from tools.price_engine import benchmark_models_against_vida, format_inr
from google.adk.agents.llm_agent import Agent

def compare_competitor_with_vida(competitor_name: str = "ALL", city_name: str = "delhi_ncr") -> str:
    """
    Benchmarks any competitor (e.g. 'Ather', 'Bajaj Chetak', 'TVS iQube', 'Ola', 'River Indie', or 'ALL') 
    against Hero MotoCorp's VIDA in any Indian city (e.g. 'Bengaluru', 'Delhi', 'Mumbai', 'Pune', 'Ahmedabad').
    Returns side-by-side pricing, state subsidies, and price deltas vs Hero VIDA.
    """
    records = benchmark_models_against_vida(competitor_query=competitor_name, city_query=city_name)
    
    formatted = []
    for r in records:
        delta_str = "Baseline" if r["is_vida_baseline"] else f"{'+' if r['delta_vs_vida'] > 0 else ''}{format_inr(r['delta_vs_vida'])}"
        pct_str = "-" if r["is_vida_baseline"] else f"{'+' if r['pct_delta'] > 0 else ''}{r['pct_delta']}%"
        
        formatted.append({
            "oem": r["oem"],
            "model": r["model"],
            "segment": r["segment"],
            "battery_kwh": f"{r['battery_kwh']} kWh",
            "range_km": f"{r['range_km']} km",
            "net_ex_showroom": format_inr(r["net_ex_showroom"]),
            "effective_on_road_price": format_inr(r["on_road_price"]),
            "price_delta_vs_vida": delta_str,
            "percentage_delta": pct_str,
            "value_score": r["value_score"],
            "city": r["city_name"]
        })
    return json.dumps(formatted, indent=2)

pricing_agent = Agent(
    name="pricing_subagent",
    model="gemini-2.5-pro",
    description="Dynamic price benchmarking agent that compares any competitor against Hero VIDA in any Indian city.",
    instruction="""
    You are the Price Benchmarking Sub-Agent.
    When asked to compare any competitor in any city, call `compare_competitor_with_vida(competitor_name, city_name)`.
    You calculate exact state subsidies, on-road prices, and price deltas against Hero VIDA.
    """,
    tools=[compare_competitor_with_vida]
)
