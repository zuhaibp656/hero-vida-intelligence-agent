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
    description="Crawls official OEM websites ONLY and extracts clean markdown context, specs, electronics, and active offers.",
    instruction="""
    You are the Web Crawling Sub-Agent.
    STRICT GROUNDING MANDATE:
    You MUST ONLY crawl official OEM web portals (Hero VIDA official ground truth: https://www.vidaworld.com, or the official website of whichever competitor is mentioned in the chat by the user).
    NEVER crawl or rely on third-party blogs, BikeWale, ZigWheels, or Google search aggregators.
    
    Call `run_crawler_tool` passing the target competitor brand name or official URL. Extract vehicle models, battery capacities (kWh), IDC range, promotional offers, touchscreen console specs, and complimentary perks.
    Return clean structured markdown context to the main agent.
    """,
    tools=[run_crawler_tool]
)


