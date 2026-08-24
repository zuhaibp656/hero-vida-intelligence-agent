import pytest
import os
import json
from agent.agent import root_agent
from agent.tools.web_crawler import resolve_official_oem_url, run_crawler_tool
from agent.tools.sandbox_manager import save_to_sandbox, load_from_sandbox, query_sandbox_models
from agent.tools.price_engine import resolve_city_rules, calculate_on_road_price, calculate_dynamic_benchmark
from agent.sub_agents.pricing_agent import compare_competitor_with_vida

def test_official_url_resolution():
    url, brand = resolve_official_oem_url("ather")
    assert "atherenergy.com" in url
    assert brand == "ATHER"

    url, brand = resolve_official_oem_url("https://www.bikewale.com/ather-scooters/")
    assert "bikewale" not in url
    assert "ather" in url.lower() or "vida" in url.lower()

    url, brand = resolve_official_oem_url("chetak")
    assert "chetak.com" in url

    url, brand = resolve_official_oem_url("tvs iqube")
    assert "tvsmotor.com" in url

def test_sandbox_persistence():
    sample_data = {
        "models": [
            {
                "oem": "Test Brand",
                "model": "Test Model 3.0",
                "battery_kwh": 3.0,
                "range_km": 120,
                "base_price": 110000.0,
                "is_vida": False
            }
        ]
    }
    save_to_sandbox("Test Brand", sample_data)
    loaded = load_from_sandbox("Test Brand")
    assert loaded is not None
    assert loaded["oem"] == "Test Brand"
    assert len(loaded["data"]["models"]) == 1

def test_city_pricing_engine():
    delhi_rules = resolve_city_rules("delhi")
    assert delhi_rules["subsidy_kwh"] == 5000
    assert delhi_rules["rto_pct"] == 0.0

    pune_rules = resolve_city_rules("pune")
    assert pune_rules["state"] == "MH"

    price_res = calculate_on_road_price(
        base_price=140000.0,
        battery_kwh=3.4,
        city_rules=delhi_rules
    )
    assert price_res["pm_subsidy"] == 8500.0
    assert price_res["state_subsidy"] == 10000.0
    assert price_res["net_ex_showroom"] == 121500.0

def test_agent_structure():
    assert root_agent.name == "hero_vida_main_agent"
    assert len(root_agent.sub_agents) == 3
    subagent_names = [sa.name for sa in root_agent.sub_agents]
    assert "crawler_subagent" in subagent_names
    assert "pricing_subagent" in subagent_names
    assert "report_subagent" in subagent_names

def test_crawler_execution():
    output = run_crawler_tool("vida", "pune", "")
    assert "Hero VIDA" in output
    assert "Pune" in output
    assert "Download" in output
