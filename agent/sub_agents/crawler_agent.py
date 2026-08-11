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
    
    Call `run_crawler_tool(target_query_or_url, city_name, model_filter)` passing:
    - `target_query_or_url`: "https://www.vidaworld.com" (or competitor URL)
    - `city_name`: The city or cities requested (e.g. "Bengaluru and Pune and Chandigarh")
    - `model_filter`: Specific model keyword if specified by the user (e.g. "v2pro", "vx2", or "" for all models)

    Return the complete Markdown Table dataset directly to the main orchestrator agent.
    """,
    tools=[run_crawler_tool]
)




