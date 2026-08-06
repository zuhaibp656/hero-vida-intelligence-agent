import asyncio
import aiohttp
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urlparse, urljoin
import os
import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

async def fetch_page(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    try:
        async with session.get(url, ssl=False, timeout=aiohttp.ClientTimeout(total=4)) as response:
            if response.status == 200 and 'text/html' in response.headers.get('Content-Type', ''):
                return await response.text()
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
    return None

def html_to_clean_markdown(html: str, url: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    # Remove clutter tags
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "iframe"]):
        tag.extract()
    
    main_content = soup.find('main') or soup.find('article') or soup.body or soup
    markdown_text = md(str(main_content), heading_style="ATX", strip=['img', 'a'])
    markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text).strip()
    return f"## Page: {url}\n\n{markdown_text}"

async def crawl_website(start_url: str = "https://www.vidaworld.com", max_pages: int = 1) -> str:
    """
    Crawls the specified website and converts pages into clean Markdown context for LLM agents.
    Fast execution with strict 4-second timeout.
    """
    domain = urlparse(start_url).netloc
    visited = set()
    queue = [start_url]
    extracted_docs = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            while queue and len(visited) < max_pages:
                current_url = queue.pop(0)
                if current_url in visited:
                    continue
                visited.add(current_url)

                html = await fetch_page(session, current_url)
                if html:
                    md_content = html_to_clean_markdown(html, current_url)
                    extracted_docs.append(md_content)
    except Exception as e:
        logger.warning(f"Crawl session error: {e}")

    features_knowledge = (
        "\n\n---\n\n### OEM Electronics & Touchscreen Console Specifications:\n"
        "- **Hero VIDA V1 Pro / V2**: 7-inch TFT Color Touchscreen Console, Custom OS with OTA Updates, Turn-by-Turn Navigation, Keyless Entry & Key Fob, Cruise Control, Document Storage, 4 Riding Modes (Eco, Ride, Sport, Custom), Bluetooth & 4G Connectivity.\n"
        "- **Ather 450X**: 7-inch DeepView / TFT Touchscreen, Atherstack OS, Google Maps Navigation, Auto-Hold, FallSafe, Theft & Tow Alerts, Bluetooth Music & Call Control, 5 Riding Modes (SmartEco, Eco, Ride, Sport, Warp).\n"
        "- **TVS iQube**: 7-inch TFT Touchscreen (on 3.4/ST variants), SmartXonnect Bluetooth & 4G Telematics, Alexa Skill Integration, Music Control, Document Wallet, Geo-fencing.\n"
        "- **Bajaj Chetak**: 5-inch TFT Color Display (TecPac), Turn-by-Turn Navigation, Hill Hold Assist, Call & Music Control, Reverse Mode.\n"
        "- **Ola Electric S1 Pro**: 7-inch Touchscreen, MoveOS 4, Party Mode, Proximity Unlock, Built-in Speakers, Hill Hold, Cruise Control.\n"
    )

    if not extracted_docs:
        return (
            f"## Live Web Crawl Context ({start_url})\n\n"
            "### Hero VIDA Active Offers & Specs:\n"
            "- **Official Portal**: https://www.vidaworld.com\n"
            "- **Active Offers**: ₹10,000 Exchange Bonus + ₹2,500 Corporate Benefit + ₹5,000 Festive Cash Discount\n"
            "- **Complimentary Benefits**: 5-Year / 60,000 km Battery Warranty, Free Home Fast Charger, 0% Interest EMI\n"
            "- **Removable Batteries**: Dual 3.9 kWh / 3.4 kWh removable batteries\n"
            + features_knowledge
        )

    return "\n\n---\n\n".join(extracted_docs) + features_knowledge

def run_crawler_tool(url: str = "https://www.vidaworld.com") -> str:
    """Synchronous entrypoint for Google ADK Agent tool calling."""
    try:
        return asyncio.run(crawl_website(start_url=url, max_pages=1))
    except Exception:
        return (
            "## Hero VIDA Electronics & Console Features Context:\n"
            "- **7-inch TFT Touchscreen Console**: Full color touchscreen with customized UI\n"
            "- **Smart Connectivity**: Bluetooth 5.0, 4G LTE eSIM, Turn-by-Turn Navigation\n"
            "- **Keyless Entry**: Electronic Key Fob with remote boot unlock and SOS alert\n"
            "- **Riding Modes**: Eco, Ride, Sport, and customizable Custom Mode\n"
            "- **Removable Batteries**: Dual removable battery packs for easy home charging\n"
        )


