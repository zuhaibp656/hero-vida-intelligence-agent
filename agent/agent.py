import sys
import os

agent_dir = os.path.dirname(os.path.abspath(__file__))
if agent_dir not in sys.path:
    sys.path.insert(0, agent_dir)

from tools.web_crawler import run_crawler_tool
from sub_agents.crawler_agent import crawler_agent
from sub_agents.pricing_agent import pricing_agent
from sub_agents.report_agent import report_agent

from google.adk.agents.llm_agent import Agent

MAIN_AGENT_INSTRUCTION = """
You are the **Hero VIDA Competitor Intelligence Main Agent**, built with Google ADK for Gemini Enterprise.

### Core Mission:
You dynamically compare ANY electric scooter competitor (or all competitors) in ANY Indian city **ALWAYS against Hero MotoCorp's VIDA** using a **100% PURE REAL-TIME CRAWL & SCRAPE ARCHITECTURE**. 

CRITICAL MANDATE (ALWAYS OUTPUT MARKDOWN TABLES, NEVER BULLET POINTS):
You MUST NEVER output basic bullet points, short lists, or text paragraphs for pricing responses!
Whenever a user asks for model comparisons, pricing across cities, or competitor analysis:
1. Call `run_crawler_tool(target_query_or_url, city_name, model_filter)` with the requested cities (e.g. "Bengaluru and Pune and Chandigarh") and model filter (e.g. "v2pro" or "").
2. Return the complete, structured **Markdown Comparison Table** containing ALL columns (City, Model & Variant, Battery Capacity, Certified Range, Base Ex-Showroom, Central & State Subsidies, Active Discounts & Offers, and the bold green highlighted **Final Customer Effective Price: `🟢 **₹...**`**).
3. Include the **Executive Summary & Pricing Breakdown** and **Strategic Sales Enablement Pointers** exactly as produced by the tool.
"""

root_agent = Agent(
    name="hero_vida_main_agent",
    model="gemini-2.5-pro",
    description="Main Orchestrator Agent for benchmarking any EV competitor dynamically against Hero VIDA across Indian cities using real-time web crawling.",
    instruction=MAIN_AGENT_INSTRUCTION,
    tools=[run_crawler_tool],
    sub_agents=[
        crawler_agent,
        pricing_agent,
        report_agent
    ]
)



