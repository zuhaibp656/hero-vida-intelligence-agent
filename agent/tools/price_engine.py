import re
from typing import Dict, List, Any, Optional

# ==============================================================================
# 1. STATE TAX & EV SUBSIDY RULES ACROSS INDIAN CITIES
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

# ==============================================================================
# 2. HERO VIDA GROUND TRUTH BASELINE MODELS (Always compared against)
# ==============================================================================
HERO_VIDA_MODELS = [
    {
        "oem": "Hero VIDA",
        "model": "VIDA VX2 Plus",
        "segment": "Mid-Range",
        "battery_kwh": 3.4,
        "range_km": 142,
        "base_price": 94800,
        "website": "https://www.vidaworld.com"
    },
    {
        "oem": "Hero VIDA",
        "model": "VIDA VX2 Go (3.1 kWh)",
        "segment": "Entry-Level",
        "battery_kwh": 3.1,
        "range_km": 127,
        "base_price": 84800,
        "website": "https://www.vidaworld.com"
    },
    {
        "oem": "Hero VIDA",
        "model": "VIDA V2 Pro",
        "segment": "Premium",
        "battery_kwh": 3.9,
        "range_km": 165,
        "base_price": 120000,
        "website": "https://www.vidaworld.com"
    }
]

# ==============================================================================
# 3. BUILT-IN DYNAMIC COMPETITOR REGISTRY (Easily matched or expanded)
# ==============================================================================
KNOWN_COMPETITORS_CATALOG = {
    "bajaj": [
        {"oem": "Bajaj Chetak", "model": "Bajaj Chetak 2901", "segment": "Entry-Level", "battery_kwh": 2.88, "range_km": 123, "base_price": 95998},
        {"oem": "Bajaj Chetak", "model": "Bajaj Chetak Premium", "segment": "Mid-Range", "battery_kwh": 3.2, "range_km": 126, "base_price": 117258}
    ],
    "chetak": [
        {"oem": "Bajaj Chetak", "model": "Bajaj Chetak 2901", "segment": "Entry-Level", "battery_kwh": 2.88, "range_km": 123, "base_price": 95998},
        {"oem": "Bajaj Chetak", "model": "Bajaj Chetak Premium", "segment": "Mid-Range", "battery_kwh": 3.2, "range_km": 126, "base_price": 117258}
    ],
    "tvs": [
        {"oem": "TVS iQube", "model": "TVS iQube 2.2 kWh", "segment": "Entry-Level", "battery_kwh": 2.2, "range_km": 75, "base_price": 94999},
        {"oem": "TVS iQube", "model": "TVS iQube 3.4 kWh", "segment": "Mid-Range", "battery_kwh": 3.4, "range_km": 100, "base_price": 117299}
    ],
    "iqube": [
        {"oem": "TVS iQube", "model": "TVS iQube 2.2 kWh", "segment": "Entry-Level", "battery_kwh": 2.2, "range_km": 75, "base_price": 94999},
        {"oem": "TVS iQube", "model": "TVS iQube 3.4 kWh", "segment": "Mid-Range", "battery_kwh": 3.4, "range_km": 100, "base_price": 117299}
    ],
    "ather": [
        {"oem": "Ather Energy", "model": "Ather Rizta S (2.9 kWh)", "segment": "Mid-Range", "battery_kwh": 2.9, "range_km": 123, "base_price": 109999},
        {"oem": "Ather Energy", "model": "Ather 450X (3.7 kWh)", "segment": "Premium", "battery_kwh": 3.7, "range_km": 150, "base_price": 154999}
    ],
    "ola": [
        {"oem": "Ola Electric", "model": "Ola S1 X (3 kWh)", "segment": "Entry-Level", "battery_kwh": 3.0, "range_km": 143, "base_price": 87999},
        {"oem": "Ola Electric", "model": "Ola S1 Air", "segment": "Mid-Range", "battery_kwh": 3.0, "range_km": 151, "base_price": 106499},
        {"oem": "Ola Electric", "model": "Ola S1 Pro Gen 2", "segment": "Premium", "battery_kwh": 4.0, "range_km": 195, "base_price": 134999}
    ],
    "simple": [
        {"oem": "Simple Energy", "model": "Simple One", "segment": "Premium", "battery_kwh": 5.0, "range_km": 212, "base_price": 145000}
    ],
    "river": [
        {"oem": "River Indie", "model": "River Indie (4 kWh)", "segment": "Mid-Range", "battery_kwh": 4.0, "range_km": 120, "base_price": 138000}
    ]
}

# ==============================================================================
# 4. DYNAMIC PRICE & SUBSIDY CALCULATION ENGINE
# ==============================================================================
def resolve_city_rules(city_query: str) -> Dict[str, Any]:
    cleaned = city_query.strip().lower().replace("-", "_").replace(" ", "_")
    for k, v in CITY_TAX_RULES.items():
        if k in cleaned or cleaned in k:
            return v
    # Default to standard Delhi-NCR policy if unknown city
    return CITY_TAX_RULES["delhi_ncr"]

def calculate_on_road_price(base_price: float, battery_kwh: float, city_rules: Dict[str, Any]) -> Dict[str, float]:
    # Central PM E-DRIVE Subsidy (₹2,500/kWh up to ₹10,000)
    pm_subsidy = min(battery_kwh * 2500, 10000)
    
    # State Subsidy
    state_subsidy = min(battery_kwh * city_rules["subsidy_kwh"], city_rules["max_subsidy"])
    
    net_ex = base_price - pm_subsidy - state_subsidy
    rto = (net_ex * (city_rules["rto_pct"] / 100.0)) + 1450 if city_rules["rto_pct"] > 0 else 1450
    insurance = city_rules["insurance"]
    orp = net_ex + rto + insurance
    
    return {
        "base_price": base_price,
        "pm_subsidy": pm_subsidy,
        "state_subsidy": state_subsidy,
        "net_ex_showroom": net_ex,
        "rto": rto,
        "insurance": insurance,
        "effective_orp": orp
    }

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

def benchmark_models_against_vida(
    competitor_query: str = "ALL",
    city_query: str = "delhi_ncr"
) -> List[Dict[str, Any]]:
    """
    Benchmarks requested competitor(s) dynamically against Hero VIDA in the requested city.
    Always uses Hero VIDA as the ground-truth benchmark baseline.
    """
    city_rules = resolve_city_rules(city_query)
    
    # 1. Compute Hero VIDA models for this city
    vida_rows = []
    for vm in HERO_VIDA_MODELS:
        cost = calculate_on_road_price(vm["base_price"], vm["battery_kwh"], city_rules)
        vida_rows.append({
            "oem": vm["oem"],
            "model": f"{vm['model']} [HERO VIDA BASELINE]",
            "segment": vm["segment"],
            "battery_kwh": vm["battery_kwh"],
            "range_km": vm["range_km"],
            "net_ex_showroom": cost["net_ex_showroom"],
            "on_road_price": cost["effective_orp"],
            "delta_vs_vida": 0.0,
            "pct_delta": 0.0,
            "value_score": round(vm["range_km"] / (cost["effective_orp"] / 100000.0), 2),
            "is_vida_baseline": True,
            "city_name": city_rules["name"]
        })

    baseline_vida_orp = vida_rows[0]["on_road_price"] # VIDA VX2 Plus baseline

    # 2. Resolve Competitor Models
    comp_models = []
    comp_lower = competitor_query.strip().lower()

    if comp_lower in ["all", "", "none", "*"]:
        for k, v in KNOWN_COMPETITORS_CATALOG.items():
            if k not in ["chetak", "iqube"]: # avoid duplicate aliases
                comp_models.extend(v)
    else:
        matched = False
        for k, v in KNOWN_COMPETITORS_CATALOG.items():
            if k in comp_lower or comp_lower in k:
                comp_models.extend(v)
                matched = True
        
        # If user typed a custom/new competitor name not in catalog, create a dynamic placeholder
        if not matched:
            clean_name = competitor_query.strip().title()
            comp_models.append({
                "oem": clean_name,
                "model": f"{clean_name} Standard",
                "segment": "Mid-Range",
                "battery_kwh": 3.0,
                "range_km": 120,
                "base_price": 105000
            })

    # 3. Calculate Competitor Prices & Deltas vs VIDA
    comp_rows = []
    for cm in comp_models:
        cost = calculate_on_road_price(cm["base_price"], cm["battery_kwh"], city_rules)
        delta = cost["effective_orp"] - baseline_vida_orp
        pct_delta = round((delta / baseline_vida_orp) * 100.0, 2)
        val_score = round(cm["range_km"] / (cost["effective_orp"] / 100000.0), 2)
        
        comp_rows.append({
            "oem": cm["oem"],
            "model": cm["model"],
            "segment": cm["segment"],
            "battery_kwh": cm["battery_kwh"],
            "range_km": cm["range_km"],
            "net_ex_showroom": cost["net_ex_showroom"],
            "on_road_price": cost["effective_orp"],
            "delta_vs_vida": delta,
            "pct_delta": pct_delta,
            "value_score": val_score,
            "is_vida_baseline": False,
            "city_name": city_rules["name"]
        })

    # Combine VIDA baseline at the top followed by competitors
    return vida_rows + comp_rows
