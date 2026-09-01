import pytest
import os
import json
from agent.agent import root_agent
from agent.tools.web_crawler import (
    resolve_official_oem_url,
    run_crawler_tool,
    parse_cities,
    match_model_filter,
    fetch_live_vida_master_data
)
from agent.tools.sandbox_manager import save_to_sandbox, load_from_sandbox, query_sandbox_models
from agent.tools.price_engine import resolve_city_rules, calculate_on_road_price, calculate_dynamic_benchmark
from agent.sub_agents.pricing_agent import compare_competitor_with_vida, compute_city_ev_pricing

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

def test_city_parsing_and_aliases():
    cities1 = parse_cities("Delhi banaglore and chennai")
    assert cities1 == ["DELHI", "BENGALURU", "CHENNAI"]

    cities2 = parse_cities("delhi, bangalore and chennai")
    assert cities2 == ["DELHI", "BENGALURU", "CHENNAI"]

    cities3 = parse_cities("in Pune, Mumbai and Ahmedabad")
    assert cities3 == ["PUNE", "MUMBAI", "AHMEDABAD"]

    cities4 = parse_cities("new delhi and blr")
    assert cities4 == ["DELHI", "BENGALURU"]

def test_model_filter_matching():
    assert match_model_filter("V2 PRO", "vida v2 pro") is True
    assert match_model_filter("V2 PRO", "Hero VIDA V2 Pro") is True
    assert match_model_filter("V2 PRO", "v2 pro") is True
    assert match_model_filter("VX2 PLUS", "vx2 plus") is True
    assert match_model_filter("VX2 Plus 4.4 kwh", "4.4") is True
    assert match_model_filter("VX2 Plus 4.4 kwh", "v2 pro") is False
    assert match_model_filter("V2 LITE", "v2 lite") is True

def test_vida_multi_city_crawler():
    output = run_crawler_tool(
        target_query_or_url="https://www.vidaworld.com",
        city_name="Delhi banaglore and chennai",
        model_filter="vida v2 pro"
    )
    assert "Delhi" in output
    assert "Bengaluru" in output
    assert "Chennai" in output
    assert "Hero VIDA V2 PRO" in output
    assert "🟢 ₹120,000" in output
    assert "🟢 ₹150,000" in output
    assert "Download" in output

def test_vida_single_string_query():
    output = run_crawler_tool(
        target_query_or_url="compare prices for vida v2 pro in Delhi banaglore and chennai"
    )
    assert "Delhi" in output
    assert "Bengaluru" in output
    assert "Chennai" in output
    assert "Hero VIDA V2 PRO" in output

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

def test_compute_city_ev_pricing():
    res_json_str = compute_city_ev_pricing(
        crawled_models_json_str=json.dumps([{
            "oem": "Hero VIDA",
            "model": "Hero VIDA V2 Pro",
            "battery_kwh": 3.9,
            "range_km": 165,
            "base_price": 155000.0,
            "effective_price": 150000.0,
            "is_vida": True
        }]),
        city_name="Delhi banaglore and chennai"
    )
    data = json.loads(res_json_str)
    assert len(data) == 3
    cities = [d["city"] for d in data]
    assert "Delhi-NCR" in cities
    assert "Bengaluru" in cities
    assert "Chennai" in cities

def test_agent_structure():
    assert root_agent.name == "hero_vida_main_agent"
    assert len(root_agent.sub_agents) == 3
    subagent_names = [sa.name for sa in root_agent.sub_agents]
    assert "crawler_subagent" in subagent_names
    assert "pricing_subagent" in subagent_names
    assert "report_subagent" in subagent_names

def test_vida_vs_competitor_comparison():
    output1 = run_crawler_tool(
        target_query_or_url="compare prices of vida v2 pro with aether rizta in bangalore and delhi"
    )
    assert "Hero VIDA V2 PRO" in output1
    assert "Ather Rizta" in output1
    assert "Bengaluru" in output1
    assert "Delhi" in output1
    assert "🟢 ₹150,000" in output1
    assert "🟢 ₹120,000" in output1

    output2 = run_crawler_tool(
        target_query_or_url="https://www.vidaworld.com",
        city_name="Bengaluru",
        model_filter="vida v2 pro with aether rizta"
    )
    assert "Hero VIDA V2 PRO" in output2
    assert "Ather Rizta" in output2
    assert "Bengaluru" in output2

def test_crawler_execution():
    output = run_crawler_tool("vida", "pune", "")
    assert "Hero VIDA" in output
    assert "Pune" in output
    assert "Download" in output

def test_slangs_and_colloquial_cities():
    cities = parse_cities("what is the price in dilli, blr, bombay, poona, hyd and amdavad?")
    assert "DELHI" in cities
    assert "BENGALURU" in cities
    assert "MUMBAI" in cities
    assert "PUNE" in cities
    assert "HYDERABAD" in cities
    assert "AHMEDABAD" in cities

def test_csv_generation_and_storage_links():
    from agent.tools.storage_manager import export_and_upload_csv, export_csv_report_tool
    sample_records = [
        {
            "city": "Delhi",
            "oem": "Hero VIDA",
            "model": "Hero VIDA V2 Pro",
            "battery_kwh": 3.9,
            "range_km": 165,
            "top_speed": "90 kmph",
            "base_price": 155000,
            "effective_price": 120000,
            "active_offers": "• ₹35,000 Total Benefits",
            "source_url": "https://www.vidaworld.com"
        },
        {
            "city": "Bengaluru",
            "oem": "Ather",
            "model": "Ather Rizta S",
            "battery_kwh": 2.9,
            "range_km": 123,
            "top_speed": "80 kmph",
            "base_price": 130998,
            "effective_price": 146004,
            "active_offers": "Standard Ex-Showroom",
            "source_url": "https://www.atherenergy.com/rizta"
        }
    ]
    res = export_and_upload_csv(sample_records, query_context="test_export")
    assert res["filename"].endswith(".csv")
    assert os.path.exists(res["local_path"])
    assert "console.cloud.google.com/storage/browser/_details" in res["console_file_url"]
    assert "storage.cloud.google.com" in res["storage_direct_url"]
    assert res["gs_uri"].startswith("gs://")
    assert "City,OEM_Brand,Model_Variant" in res["csv_content"]

def test_same_company_different_models_different_cities():
    # Same company: Hero VIDA, multiple variants across multiple cities
    output = run_crawler_tool(
        target_query_or_url="https://www.vidaworld.com",
        city_name="Delhi and Bengaluru",
        model_filter="v2 pro and vx2 plus"
    )
    assert "Delhi" in output
    assert "Bengaluru" in output
    assert "Hero VIDA V2 PRO" in output
    assert "VX2 PLUS" in output
    assert "Cloud Storage Console" in output
    assert "```csv" in output


