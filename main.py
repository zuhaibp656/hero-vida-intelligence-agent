import asyncio
import json
import re
import uuid
import requests
from google.auth.transport.requests import Request
from google.auth import default
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from agent.agent import root_agent
from agent.tools.web_crawler import crawl_website
from agent.sub_agents.pricing_agent import compare_competitor_with_vida
from agent.tools.price_engine import CITY_TAX_RULES

console = Console()

def render_table(data_json: str):
    rows = json.loads(data_json)
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
            r["segment"],
            r["battery_kwh"],
            r["range_km"],
            r["net_ex_showroom"],
            r["effective_on_road_price"],
            r["price_delta_vs_vida"],
            str(r["value_score"])
        )
    console.print(table)

def get_auth_headers():
    creds, _ = default()
    creds.refresh(Request())
    return {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json"
    }

async def interactive_chat():
    session_id = str(uuid.uuid4())
    PROJECT_ID = "zuhaibp-ai"
    LOCATION = "us-central1"
    ENGINE_ID = "8827320801704280064"
    URL = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{ENGINE_ID}:streamQuery"
    
    console.print(Panel(
        "[bold green]Entering Interactive Agent Mode.[/bold green]\n"
        "Ask about any competitor or city. The agent will remember the context.\n"
        "Type [bold red]'exit'[/bold red] to return to the menu.",
        border_style="green"
    ))

    while True:
        user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
        if user_input.strip().lower() in ['exit', 'quit', '0']:
            break
        if not user_input.strip():
            continue

        payload = {
            "class_method": "async_stream_query",
            "input": {
                "message": user_input,
                "session_id": session_id
            }
        }
        console.print("\n[bold purple]VIDA Agent:[/bold purple]")
        
        try:
            with requests.post(URL, headers=get_auth_headers(), json=payload, stream=True) as r:
                r.raise_for_status()
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
        except Exception as e:
            console.print(f"[bold red]Error communicating with Agent Platform:[/bold red] {e}")

async def main():
    console.print(Panel(
        "[bold cyan]HERO MOTOCORP VIDA[/bold cyan] — [bold green]Dynamic Competitor Intelligence Agent[/bold green]\n"
        "[dim]High-Code Agent built with Google ADK (Main Agent + 3 Sub-Agents)[/dim]\n"
        "[italic yellow]Target Portal: https://www.vidaworld.com | Baseline: Always Benchmark vs Hero VIDA[/italic yellow]",
        border_style="cyan"
    ))

    while True:
        console.print("\n[bold]Select an Option:[/bold]")
        console.print("  [1] [bold white]Ask / Chat in Natural Language[/bold white] (e.g., 'Compare Chetak in Pune with VIDA')")
        console.print("  [2] [bold white]Quick Benchmark Form[/bold white] (Enter any Competitor Name & City as variables)")
        console.print("  [3] [bold white]Run Live Web Crawler on vidaworld.com[/bold white] (Pulls live markdown specs)")
        console.print("  [4] [bold white]List Major Indian EV Cities & Subsidies[/bold white]")
        console.print("  [0] [bold red]Exit[/bold red]")

        choice = Prompt.ask("\nEnter choice", choices=["0", "1", "2", "3", "4"], default="1")

        if choice == "0":
            console.print("[green]Exiting Hero Intelligence Agent. Goodbye![/green]")
            break

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
            console.print("\n[yellow]Executing Web Crawler Sub-Agent on https://www.vidaworld.com...[/yellow]")
            context_md = await crawl_website("https://www.vidaworld.com", max_pages=2)
            console.print(Panel(context_md[:1500] + "\n\n...[Truncated for display]...", title="Extracted Live Knowledge Context", border_style="yellow"))

        elif choice == "2":
            console.print("\n[bold cyan]Dynamic Variable Inputs:[/bold cyan]")
            comp_input = Prompt.ask("Enter Competitor Name (e.g. 'Ather', 'Chetak', 'TVS', 'Ola', 'River Indie', or 'ALL')", default="ALL")
            city_input = Prompt.ask("Enter City Name (e.g. 'Bengaluru', 'Delhi', 'Mumbai', 'Pune', 'Ahmedabad', 'Jaipur')", default="delhi_ncr")

            console.print(f"\n[cyan]Benchmarking [bold]{comp_input}[/bold] against [bold]HERO VIDA[/bold] in [bold]{city_input}[/bold]...[/cyan]\n")
            result_json = compare_competitor_with_vida(competitor_name=comp_input, city_name=city_input)
            render_table(result_json)

        elif choice == "1":
            await interactive_chat()

if __name__ == "__main__":
    asyncio.run(main())
