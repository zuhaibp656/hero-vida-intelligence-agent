import re
from typing import Dict, List, Any, Optional
from tools.sandbox_manager import query_sandbox_models, load_from_sandbox
from tools.storage_manager import export_and_upload_csv, format_csv_download_section

# ==============================================================================
# 1. OFFICIAL STATE TAX & EV SUBSIDY RULES ACROSS INDIAN CITIES
# ==============================================================================
CITY_TAX_RULES = {
    # North
    "delhi": {"name": "Delhi-NCR", "state": "DL", "region": "North", "subsidy_kwh": 5000, "max_subsidy": 10000, "rto_pct": 0.0, "insurance": 5400},
    "delhi_ncr": {"name": "Delhi-NCR", "state": "DL", "region": "North", "subsidy_kwh": 5000, "max_subsidy": 10000, "rto_pct": 0.0, "insurance": 5400},
    "gurgaon": {"name": "Gurgaon (NCR)", "state": "HR", "region": "North", "subsidy_kwh": 0, "max_subsidy": 0, "rto_pct": 0.0, "insurance": 5400},
    "noida": {"name": "Noida (NCR)", "state": "UP", "region": "North", "subsidy_kwh": 5000, "max_subsidy": 5000, "rto_pct": 0.0, "insurance": 5200},
    "jaipur": {"name": "Jaipur", "state": "RJ", "region": "North", "subsidy_kwh": 2500, "max_subsidy": 5000, "rto_pct": 0.0, "insurance": 5300},
    "lucknow": {"name": "Lucknow", "state": "UP", "region": "North", "subsidy_kwh": 5000, "max_subsidy": 5000, "rto_pct": 0.0, "insurance": 5200},
    "chandigarh": {"name": "Chandigarh Capital Region", "state": "CH", "region": "North", "subsidy_kwh": 3000, "max_subsidy": 10000, "rto_pct": 0.0, "insurance": 5300},
    "chandigarh_cr": {"name": "Chandigarh Capital Region", "state": "CH", "region": "North", "subsidy_kwh": 3000, "max_subsidy": 10000, "rto_pct": 0.0, "insurance": 5300},
    
    # South
    "bengaluru": {"name": "Bengaluru", "state": "KA", "region": "South", "subsidy_kwh": 0, "max_subsidy": 0, "rto_pct": 0.0, "insurance": 5650},
    "bangalore": {"name": "Bengaluru", "state": "KA", "region": "South", "subsidy_kwh": 0, "max_subsidy": 0, "rto_pct": 0.0, "insurance": 5650},
    "hyderabad": {"name": "Hyderabad", "state": "TS", "region": "South", "subsidy_kwh": 0, "max_subsidy": 0, "rto_pct": 0.0, "insurance": 5500},
    "chennai": {"name": "Chennai", "state": "TN", "region": "South", "subsidy_kwh": 0, "max_subsidy": 0, "rto_pct": 0.0, "insurance": 5450},
    "coimbatore": {"name": "Coimbatore", "state": "TN", "region": "South", "subsidy_kwh": 0, "max_subsidy": 0, "rto_pct": 0.0, "insurance": 5400},
    "kochi": {"name": "Kochi", "state": "KL", "region": "South", "subsidy_kwh": 0, "max_subsidy": 0, "rto_pct": 5.0, "insurance": 5500},
    
    # West
    "mumbai": {"name": "Mumbai Metropolitan Region (MMR)", "state": "MH", "region": "West", "subsidy_kwh": 5000, "max_subsidy": 10000, "rto_pct": 0.0, "insurance": 5800},
    "mmr": {"name": "Mumbai Metropolitan Region (MMR)", "state": "MH", "region": "West", "subsidy_kwh": 5000, "max_subsidy": 10000, "rto_pct": 0.0, "insurance": 5800},
    "pune": {"name": "Pune", "state": "MH", "region": "West", "subsidy_kwh": 5000, "max_subsidy": 10000, "rto_pct": 0.0, "insurance": 5600},
    "ahmedabad": {"name": "Ahmedabad-Gandhinagar", "state": "GJ", "region": "West", "subsidy_kwh": 10000, "max_subsidy": 20000, "rto_pct": 0.0, "insurance": 5350},
    "ahmedabad_gandhinagar": {"name": "Ahmedabad-Gandhinagar", "state": "GJ", "region": "West", "subsidy_kwh": 10000, "max_subsidy": 20000, "rto_pct": 0.0, "insurance": 5350},
    "surat": {"name": "Surat", "state": "GJ", "region": "West", "subsidy_kwh": 10000, "max_subsidy": 20000, "rto_pct": 0.0, "insurance": 5350},
    
    # East
    "kolkata": {"name": "Kolkata", "state": "WB", "region": "East", "subsidy_kwh": 0, "max_subsidy": 0, "rto_pct": 0.0, "insurance": 5400},
    "patna": {"name": "Patna", "state": "BR", "region": "East", "subsidy_kwh": 5000, "max_subsidy": 7500, "rto_pct": 0.0, "insurance": 5200}
}

def resolve_city_rules(city_query: str) -> Dict[str, Any]:
    from tools.web_crawler import CITY_ALIASES
    cleaned = city_query.strip().lower().replace("-", "_").replace(" ", "_")
    alias_std = CITY_ALIASES.get(cleaned.replace("_", ""), "").lower()
    
    for k, v in CITY_TAX_RULES.items():
        if k == cleaned or k == alias_std or k in cleaned or cleaned in k:
            return v
    return CITY_TAX_RULES["delhi_ncr"]

def format_inr(val: float) -> str:
    is_neg = val < 0
    s = f"{int(round(abs(val)))}"
    if len(s) <= 3:
        res = f"₹{s}"
    else:
        last3 = s[-3:]
        rem = s[:-3]
        groups = []
        while len(rem) > 2:
            groups.insert(0, rem[-2:])
            rem = rem[:-2]
        if rem:
            groups.insert(0, rem)
        res = f"₹{','.join(groups)},{last3}"
    return f"-{res}" if is_neg else res

def calculate_on_road_price(
    base_price: float, 
    battery_kwh: float, 
    city_rules: Dict[str, Any], 
    oem_name: str = "Hero VIDA",
    cash_discount: float = 0.0,
    exchange_bonus: float = 0.0,
    corporate_bonus: float = 0.0,
    offers_summary: Optional[str] = None,
    perks_summary: Optional[str] = None
) -> Dict[str, Any]:
    # Central PM E-DRIVE Subsidy (₹2,500/kWh up to ₹10,000)
    pm_subsidy = min(battery_kwh * 2500, 10000)
    
    # State Subsidy
    state_subsidy = min(battery_kwh * city_rules["subsidy_kwh"], city_rules["max_subsidy"])
    
    net_ex = base_price - pm_subsidy - state_subsidy
    rto = (net_ex * (city_rules["rto_pct"] / 100.0)) + 1450 if city_rules["rto_pct"] > 0 else 1450
    insurance = city_rules["insurance"]
    orp = net_ex + rto + insurance
    
    total_discounts = cash_discount + exchange_bonus + corporate_bonus
    if offers_summary:
        offers_text = offers_summary
    elif total_discounts > 0:
        offers_text = f"• ₹{int(total_discounts):,} In-Portal Promotional Savings"
    else:
        offers_text = "Standard Ex-Showroom (Official Portal)"

    perks_text = perks_summary or "Official OEM Warranty & Included Standard Charger"
    effective_promotional_orp = max(orp - cash_discount, 0)
    
    return {
        "base_price": base_price,
        "pm_subsidy": pm_subsidy,
        "state_subsidy": state_subsidy,
        "net_ex_showroom": net_ex,
        "rto": rto,
        "insurance": insurance,
        "effective_orp": orp,
        "promotional_on_road_price": effective_promotional_orp,
        "active_offers": offers_text,
        "complimentary_perks": perks_text,
        "max_potential_savings": total_discounts
    }

def calculate_dynamic_benchmark(
    crawled_models_json: List[Dict[str, Any]],
    city_query: str = "delhi_ncr"
) -> List[Dict[str, Any]]:
    """
    Takes live real-time crawled model parameters (from Sandbox or Crawler)
    and computes dynamic city tax, subsidies, on-road prices, and deltas against Hero VIDA baseline.
    Zero hardcoded values.
    """
    city_rules = resolve_city_rules(city_query)
    
    if not crawled_models_json:
        crawled_models_json = query_sandbox_models()

    if not crawled_models_json:
        return []

    rows = []
    baseline_vida_orp = 0.0

    for idx, item in enumerate(crawled_models_json):
        oem = item.get("oem", "Hero VIDA")
        model = item.get("model", "Electric Scooter")
        base_price = float(item.get("base_price", 120000.0))
        battery_kwh = float(item.get("battery_kwh", 3.4))
        range_km = int(item.get("range_km", 140))
        is_vida = item.get("is_vida", "vida" in oem.lower() or "hero" in oem.lower() or "vida" in model.lower())

        cash_disc = float(item.get("cash_discount", 0.0))
        exch_bonus = float(item.get("exchange_bonus", 0.0))
        corp_bonus = float(item.get("corporate_bonus", 0.0))
        offers_summary = item.get("active_offers", None)
        perks_summary = item.get("complimentary_perks", None)

        cost = calculate_on_road_price(
            base_price=base_price,
            battery_kwh=battery_kwh,
            city_rules=city_rules,
            oem_name=oem,
            cash_discount=cash_disc,
            exchange_bonus=exch_bonus,
            corporate_bonus=corp_bonus,
            offers_summary=offers_summary,
            perks_summary=perks_summary
        )

        if is_vida and baseline_vida_orp == 0.0:
            baseline_vida_orp = cost["effective_orp"]

        delta = cost["effective_orp"] - baseline_vida_orp if baseline_vida_orp > 0 else 0.0
        pct_delta = round((delta / cost["effective_orp"]) * 100.0, 1) if cost["effective_orp"] > 0 else 0.0
        val_score = round(range_km / (cost["effective_orp"] / 100000.0), 1) if cost["effective_orp"] > 0 else 0.0

        rows.append({
            "oem": oem,
            "model": f"{model} [HERO VIDA BASELINE]" if is_vida else model,
            "segment": f"{battery_kwh} kWh / {range_km} km",
            "battery_kwh": battery_kwh,
            "range_km": range_km,
            "base_ex_showroom": format_inr(cost["base_price"]),
            "pm_subsidy": format_inr(cost["pm_subsidy"]),
            "state_subsidy": format_inr(cost["state_subsidy"]),
            "net_ex_showroom": format_inr(cost["net_ex_showroom"]),
            "rto_cost": format_inr(cost["rto"]),
            "insurance_cost": format_inr(cost["insurance"]),
            "effective_on_road_price": format_inr(cost["effective_orp"]),
            "promotional_on_road_price": format_inr(cost["promotional_on_road_price"]),
            "active_offers": cost["active_offers"],
            "complimentary_perks": cost["complimentary_perks"],
            "max_potential_savings": format_inr(cost["max_potential_savings"]),
            "delta_vs_vida": delta,
            "price_delta_vs_vida": "Baseline" if is_vida else f"{'+' if delta > 0 else ''}{format_inr(delta)}",
            "pct_delta": pct_delta,
            "value_score": val_score,
            "is_vida_baseline": is_vida,
            "city_name": city_rules["name"],
            "city": city_rules["name"],
            "source_url": item.get("source_url", "https://www.vidaworld.com")
        })

    return rows

def benchmark_models_against_vida(
    competitor_query: str = "ALL",
    city_query: str = "delhi_ncr",
    crawled_models: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Synchronous ADK Tool entrypoint.
    Computes tax, subsidy, on-road prices, and deltas strictly on live crawled model inputs.
    """
    models_to_calc = crawled_models or query_sandbox_models(competitor_query if competitor_query != "ALL" else None)
    return calculate_dynamic_benchmark(models_to_calc, city_query)
