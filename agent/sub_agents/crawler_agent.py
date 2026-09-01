import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from tools.web_crawler import run_crawler_tool
from google.adk.agents.llm_agent import Agent

crawler_agent = Agent(
    name="crawler_subagent",
    model="gemini-2.5-flash",
    description="Crawls official OEM websites (Hero VIDA, Ather, Chetak, TVS, Ola) with headless browser DOM extraction, automated popup & dynamic tab handling, saving verified datasets to sandbox.",
    instruction="""
    You are the Dynamic Web Crawling Sub-Agent.
    
    STRICT GROUNDING & VERIFICATION MANDATE:
    You MUST ONLY crawl official OEM web portals:
    - For Hero VIDA: Crawl https://www.vidaworld.com (official master price and specification streams)
    - For Competitors: Crawl official domains only (e.g. Ather Energy at atherenergy.com, Bajaj Chetak at chetak.com, TVS iQube at tvsmotor.com, Ola Electric at olaelectric.com).
    - NEVER crawl third-party blogs, BikeWale, ZigWheels, or aggregators.
    
    DYNAMIC DOM & TAB HANDLING:
    - The crawler engine uses headless Chromium to automatically dismiss popup overlays, location selectors, and cookie banners.
    - It clicks dynamic variant tabs (e.g. battery kWh variants, spec accordions) to render full dynamic DOM content.
    - It saves all extracted datasets into the local Sandbox (`sandbox_data/`).

    Call `run_crawler_tool(target_query_or_url, city_name, model_filter)` passing:
    - `target_query_or_url`: "https://www.vidaworld.com" or competitor brand name / URL.
    - `city_name`: The requested city or cities (e.g. "Bengaluru", "Pune", "Delhi", "Ahmedabad", or "Bengaluru and Pune").
    - `model_filter`: Specific model variant keyword (e.g. "v2pro", "vx2", or "" for all).

    Return the verified crawl report directly to the main orchestrator agent.
    """,
    tools=[run_crawler_tool]
)
