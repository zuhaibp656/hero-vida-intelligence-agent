# 📊 Token Consumption, Cost Modeling & Volume Projections Guide
### Hero MotoCorp VIDA — Competitor Intelligence Agent on Google Cloud Vertex AI

---

## 1. Executive Summary

This empirical report models token consumption, latency, and financial operating costs for the **Hero VIDA Competitor Intelligence Agent** running on **Google Cloud Vertex AI** with **Google ADK (`google.adk`)**.

The agent features a hierarchical multi-agent architecture:
- **Root Orchestrator Agent (`gemini-2.5-pro`)**: Handles natural language queries, slang normalization, context continuity across multi-turn sessions, and strategic sales synthesis.
- **Crawler Sub-Agent (`gemini-2.5-flash`)**: High-speed web scraping engine that extracts real-time DOM feeds from `vidaworld.com` and rival OEM portals.
- **Pricing Sub-Agent (`gemini-2.5-pro`)**: Dynamic math engine computing central PM E-Drive subsidies and state EV policy rules.
- **Report Sub-Agent (`gemini-2.5-pro`)**: Formats executive tables and uploads CSV datasets to Google Cloud Storage (`gs://zuhaibp-ai-hero-vida-reports`).

---

## 2. Vertex AI Pricing Reference (Standard Tier)

| Model | Architectural Role | Input Tokens ($ / 1M) | Output Tokens ($ / 1M) | Context Window |
| :--- | :--- | :---: | :---: | :---: |
| **Gemini 2.5 Pro** | Root Orchestrator, Subsidy Engine, Strategic Report | **$1.25** | **$5.00** | Up to 1M / 2M |
| **Gemini 2.5 Flash** | Web Crawler Sub-Agent, Real-time DOM Data Extraction | **$0.15** | **$0.60** | Up to 1M |

*Note: USD to INR conversion applied at standard rate: 1 USD = ₹86.50 INR.*

---

## 3. Base Conversation & Framework Overhead

Before query-specific crawling or data synthesis takes place, each session carries agent configuration instructions:
- **Root System Instruction (`MAIN_AGENT_INSTRUCTION`)**: ~1,050 tokens
- **Tool Schemas (`run_crawler_tool`, `compute_city_ev_pricing`, `export_csv_report_tool`)**: ~620 tokens
- **Sub-Agent Schema Declarations**: ~380 tokens
- **Baseline Framework Context Overhead**: **~2,050 input tokens per invocation**

---

## 4. Empirical Query Complexity Matrix

| Complexity Tier | Archetype User Query | Agent Routing Path | Input Tokens | Output Tokens | Total Tokens | Gemini 2.5 Pro Cost (USD) | Gemini 2.5 Pro Cost (INR) | Gemini 2.5 Flash Cost (USD) | Gemini 2.5 Flash Cost (INR) | Typical Latency |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tier 1: Simple Single-Variant** | *"What is the on-road price of Hero VIDA V2 Pro in Delhi?"* | Root -> Crawler Subagent (Flash) -> Response | 2,500 | 350 | 2,850 | **$0.00488** | **₹0.42** | $0.00059 | ₹0.05 | ~1.4s |
| **Tier 2: Moderate 1v1 Compare** | *"Compare Ather Rizta with Hero VIDA V2 Plus in Bengaluru across battery and price"* | Root -> Parallel Crawler Subagent -> Pricing Subagent -> Report Subagent | 3,350 | 600 | 3,950 | **$0.00719** | **₹0.62** | $0.00086 | ₹0.07 | ~2.1s |
| **Tier 3: Complex Multi-City Benchmark** | *"Benchmark Hero VIDA against Ather 450X and Chetak in Delhi, Bengaluru, and Pune with CSV export"* | Root -> Concurrent Multi-OEM Crawl -> Pricing Subagent -> GCS CSV Upload -> Report Subagent | 6,800 | 1,100 | 7,900 | **$0.01400** | **₹1.21** | $0.00168 | ₹0.15 | ~3.8s |
| **Tier 4: Multi-Turn Executive Session** | *Full 4-turn follow-up dialogue adding cities, battery specs, and subsidy comparisons* | Root Agent with Conversation History Memory -> Dynamic Crawl -> Updated Benchmark | 14,500 | 2,400 | 16,900 | **$0.03013** | **₹2.61** | $0.00362 | ₹0.31 | ~4.5s |

---

## 5. Enterprise Monthly Volume Projections

Assuming a typical enterprise dealer/executive workload distribution:
- **40% Simple Lookups** (Tier 1)
- **35% Direct 1v1 Comparisons** (Tier 2)
- **15% Multi-City / Multi-Competitor Benchmarks** (Tier 3)
- **10% Multi-Turn Deep Consultations** (Tier 4)

**Weighted Blended Average Cost per Query:**
- **Gemini 2.5 Pro:** **$0.00958 (~0.96¢ / ₹0.83 INR)**
- **Gemini 2.5 Flash:** **$0.00115 (~0.12¢ / ₹0.10 INR)**

### Volume Scaling Table

| Monthly Invocations | Est. Total Monthly Tokens | Vertex AI Monthly Cost (Gemini 2.5 Pro) | Vertex AI Monthly Cost (Gemini 2.5 Flash) |
| :--- | :---: | :---: | :---: |
| **1,000 Queries / Mo** | ~5.3M Tokens | **$9.58 (₹828)** | **$1.15 (₹99)** |
| **5,000 Queries / Mo** | ~26.6M Tokens | **$47.89 (₹4,142)** | **$5.75 (₹497)** |
| **20,000 Queries / Mo** | ~106.5M Tokens | **$191.57 (₹16,570)** | **$22.99 (₹1,988)** |
| **50,000 Queries / Mo** | ~266.3M Tokens | **$478.91 (₹41,426)** | **$57.48 (₹4,971)** |

---

## 6. Architectural Cost Optimization Strategies

1. **Vertex AI Context Caching**:
   - The ~2,050 tokens of system instructions and tool definitions do not change across queries.
   - Activating Context Caching reduces input costs for these static tokens by **75%** (from $1.25 down to $0.3125 per 1M tokens).
2. **Flash-First Routing**:
   - Simple single-city variant checks (Tier 1) can be resolved entirely using `gemini-2.5-flash`, reducing per-query costs from ₹0.42 to ₹0.05.
   - `gemini-2.5-pro` can be preserved exclusively for multi-brand strategic analysis and multi-city matrix reports.
3. **Local TTL Scraping Cache**:
   - The integrated in-memory 10-minute TTL cache eliminates redundant DOM fetches when multiple users in the same dealership search the same models.
