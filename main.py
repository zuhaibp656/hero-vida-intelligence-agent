import asyncio
import json
import re
import uuid
import os
import requests
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from agent.agent import root_agent
from agent.tools.web_crawler import crawl_website, run_crawler_tool
from agent.sub_agents.pricing_agent import compare_competitor_with_vida
from agent.tools.price_engine import CITY_TAX_RULES
from agent.tools.sandbox_manager import list_sandbox_contents

console = Console()

def render_table(data_json: str):
    try:
        rows = json.loads(data_json)
    except Exception as e:
        console.print(f"[red]Failed to parse pricing records: {e}[/red]")
        return

    if not rows:
        console.print("[red]No pricing records found.[/red]")
        return

    city_name = rows[0].get("city", "Target City")
    table = Table(
        title=f"Competitive Pricing Benchmark against HERO VIDA — {city_name}",
        header_style="bold magenta",
        show_lines=True
    )
    table.add_column("OEM / Brand", style="cyan")
    table.add_column("Model Name", style="bold white")
    table.add_column("Segment", style="dim")
    table.add_column("Battery", style="yellow")
    table.add_column("Range (IDC)", style="green")
    table.add_column("Net Ex-Showroom", style="white")
    table.add_column("On-Road Price", style="bold green")
    table.add_column("Delta vs HERO VIDA", style="magenta")
    table.add_column("Value Score (km/₹L)", style="blue")

    for r in rows:
        oem_display = f"[bold green]{r['oem']}[/bold green]" if "HERO" in r['model'] else r['oem']
        table.add_row(
            oem_display,
            r["model"],
            r.get("segment", "-"),
            f"{r['battery_kwh']} kWh" if isinstance(r['battery_kwh'], (int, float)) else str(r['battery_kwh']),
            f"{r['range_km']} km" if isinstance(r['range_km'], (int, float)) else str(r['range_km']),
            r["net_ex_showroom"],
            r["effective_on_road_price"],
            r["price_delta_vs_vida"],
            str(r.get("value_score", "-"))
        )
    console.print(table)

def get_auth_headers():
    try:
        from google.auth.transport.requests import Request
        from google.auth import default
        creds, _ = default()
        creds.refresh(Request())
        return {
            "Authorization": f"Bearer {creds.token}",
            "Content-Type": "application/json"
        }
    except Exception as e:
        return None

async def interactive_chat():
    session_id = str(uuid.uuid4())
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    ENGINE_ID = os.environ.get("AGENT_ENGINE_ID", "")
    user_identity = os.environ.get("USER", "hero_user")
    
    can_stream_remote = bool(PROJECT_ID and ENGINE_ID)
    URL = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{ENGINE_ID}:streamQuery" if can_stream_remote else ""
    
    console.print(Panel(
        "[bold green]Entering Interactive Agent Mode.[/bold green]\n"
        "Ask about any competitor or city (e.g. 'Compare Ather in Bengaluru with VIDA').\n"
        "The agent will dynamically crawl official sites, dismiss popups/tabs, save to sandbox, and compute city subsidies.\n"
        "Type [bold red]'exit'[/bold red] to return to the main menu.",
        border_style="green"
    ))

    last_context = ""
    while True:
        user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
        if user_input.strip().lower() in ['exit', 'quit', '0']:
            break
        if not user_input.strip():
            continue

        # Check if user query is a follow-up continuing the previous context
        is_followup = any(user_input.lower().startswith(prefix) for prefix in ["now", "also", "and", "what about", "add", "compare with", "how about", "in ", "which"])
        effective_query = f"{last_context} and {user_input}" if (is_followup and last_context) else user_input
        last_context = effective_query

        headers = get_auth_headers() if can_stream_remote else None
        if headers and can_stream_remote:
            payload = {
                "class_method": "async_stream_query",
                "input": {
                    "message": user_input,
                    "user_id": user_identity,
                    "session_id": session_id
                }
            }
            console.print("\n[bold purple]VIDA Agent (Agent Platform):[/bold purple]")
            try:
                with requests.post(URL, headers=headers, json=payload, stream=True, timeout=60) as r:
                    if r.status_code == 200:
                        for line in r.iter_lines():
                            if line:
                                try:
                                    chunk = json.loads(line.decode('utf-8'))
                                    if "content" in chunk and isinstance(chunk["content"], dict) and "parts" in chunk["content"]:
                                        for part in chunk["content"]["parts"]:
                                            if "text" in part:
                                                print(part["text"], end="", flush=True)
                                except json.JSONDecodeError:
                                    continue
                        print("\n")
                        continue
                    else:
                        console.print(f"[dim yellow]Remote agent returned status {r.status_code}, executing via Local ADK Runner...[/dim yellow]")
            except Exception as e:
                console.print(f"[dim yellow]Remote endpoint unreachable ({e}), running via Local Agent Engine...[/dim yellow]")

        # Local execution fallback
        console.print("\n[bold purple]VIDA Agent (Local Multi-Agent Runtime):[/bold purple]")
        from agent.tools.web_crawler import parse_cities
        cities = parse_cities(effective_query)
        city_str = ", ".join(cities)
        
        result_md = run_crawler_tool(target_query_or_url=effective_query, city_name=city_str)
        console.print(result_md)


async def main():
    console.print(Panel(
        "[bold cyan]HERO MOTOCORP VIDA[/bold cyan] — [bold green]Dynamic Competitor Intelligence Multi-Agent[/bold green]\n"
        "[dim]High-Code Agent built with Google ADK (Main Agent + 3 Sub-Agents)[/dim]\n"
        "[italic yellow]Target Portal: https://www.vidaworld.com | Dynamic DOM & Sandbox Pipeline[/italic yellow]",
        border_style="cyan"
    ))

    while True:
        console.print("\n[bold]Select an Option:[/bold]")
        console.print("  [1] [bold white]Ask / Chat in Natural Language[/bold white] (e.g., 'Compare Ather in Bengaluru with VIDA')")
        console.print("  [2] [bold white]Quick Benchmark Form[/bold white] (Enter any Competitor Name & City as variables)")
        console.print("  [3] [bold white]Run Dynamic Web Crawler (Playwright DOM + Tabs/Popups Engine)[/bold white]")
        console.print("  [4] [bold white]List Major Indian EV Cities & Subsidies[/bold white]")
        console.print("  [5] [bold white]Inspect Sandbox Datasets[/bold white]")
        console.print("  [0] [bold red]Exit[/bold red]")

        choice = Prompt.ask("\nEnter choice", choices=["0", "1", "2", "3", "4", "5"], default="1")

        if choice == "0":
            console.print("[green]Exiting Hero Intelligence Agent. Goodbye![/green]")
            break

        elif choice == "5":
            items = list_sandbox_contents()
            table = Table(title="Local Sandbox Data Store Contents", header_style="bold green")
            table.add_column("File Name", style="cyan")
            table.add_column("OEM Brand", style="bold white")
            table.add_column("Last Crawled", style="yellow")
            table.add_column("Models Cached", style="green")
            for item in items:
                table.add_row(item["file"], item["oem"], item["timestamp"], str(item["models_count"]))
            console.print(table if items else "[yellow]Sandbox is currently empty. Run a crawl first![/yellow]")

        elif choice == "4":
            cluster_table = Table(title="Major Indian EV Cities & State Policy Subsidies", header_style="bold cyan")
            cluster_table.add_column("City / Hub", style="bold green")
            cluster_table.add_column("State", style="white")
            cluster_table.add_column("Region", style="magenta")
            cluster_table.add_column("State EV Subsidy", style="yellow")
            cluster_table.add_column("RTO Exemption", style="blue")
            
            seen = set()
            for cid, cdata in CITY_TAX_RULES.items():
                if cdata["name"] not in seen:
                    seen.add(cdata["name"])
                    sub_str = f"₹{cdata['subsidy_kwh']}/kWh (Max ₹{cdata['max_subsidy']})" if cdata['subsidy_kwh'] > 0 else "0% (PM E-DRIVE Only)"
                    rto_str = f"{cdata['rto_pct']}% Tax" if cdata['rto_pct'] > 0 else "100% Waived"
                    cluster_table.add_row(cdata["name"], cdata["state"], cdata["region"], sub_str, rto_str)
            console.print(cluster_table)

        elif choice == "3":
            url_in = Prompt.ask("Enter Target OEM Website or Brand Name", default="https://www.vidaworld.com")
            city_in = Prompt.ask("Enter City Name", default="Pune")
            console.print(f"\n[yellow]Executing Dynamic Playwright Crawler on {url_in} for {city_in}...[/yellow]")
            context_md = run_crawler_tool(url_in, city_in, "")
            console.print(Panel(context_md, title="Dynamic Web Crawl Output & Grounding", border_style="yellow"))

        elif choice == "2":
            console.print("\n[bold cyan]Dynamic Variable Inputs:[/bold cyan]")
            comp_input = Prompt.ask("Enter Competitor Name (e.g. 'Ather', 'Chetak', 'TVS', 'Ola', or 'ALL')", default="Ather")
            city_input = Prompt.ask("Enter City Name (e.g. 'Bengaluru', 'Delhi', 'Mumbai', 'Pune', 'Ahmedabad', 'Jaipur')", default="Bengaluru")

            console.print(f"\n[cyan]Benchmarking [bold]{comp_input}[/bold] against [bold]HERO VIDA[/bold] in [bold]{city_input}[/bold]...[/cyan]\n")
            result_json = compare_competitor_with_vida(competitor_name=comp_input, city_name=city_input)
            render_table(result_json)

        elif choice == "1":
            await interactive_chat()

if __name__ == "__main__":
    asyncio.run(main())
