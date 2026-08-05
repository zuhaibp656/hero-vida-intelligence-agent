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
    description="Crawls official OEM websites and extracts clean markdown context and vehicle specifications.",
    instruction="""
    You are the Web Crawling Sub-Agent.
    Your job is to call the `run_crawler_tool` on the official Hero VIDA portal (https://www.vidaworld.com) 
    or authorized OEM URLs. Extract vehicle models, battery sizes (kWh), IDC range (km), and promotional pricing.
    Return clean structured markdown context to the main agent.
    """,
    tools=[run_crawler_tool]
)
