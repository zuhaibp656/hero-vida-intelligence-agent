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
    description="Crawls official OEM websites ONLY and extracts clean real-time markdown dataset, pricing, specs, electronics, and active offers.",
    instruction="""
    You are the Web Crawling Sub-Agent.
    STRICT GROUNDING MANDATE:
    You MUST ONLY crawl official OEM web portals:
    - For Hero VIDA: Crawl https://www.vidaworld.com
    - For Competitors: Crawl the official website of whichever competitor is mentioned in the chat by the user (e.g. Ather, TVS, Chetak, Ola).
    NEVER crawl third-party blogs, BikeWale, ZigWheels, or aggregators.
    
    Call `run_crawler_tool(target_query_or_url, city_name)` passing the brand name/URL and the user's target city (e.g. 'pune', 'bengaluru', 'delhi').
    Return the live scraped model names, ex-showroom and effective prices, battery kWh, certified range, top speed, riding modes, and active promotional offers to the main orchestrator agent.
    """,
    tools=[run_crawler_tool]
)



