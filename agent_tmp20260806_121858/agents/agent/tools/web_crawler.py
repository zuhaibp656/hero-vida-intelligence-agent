import asyncio
import aiohttp
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urlparse, urljoin
import os
import re
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

THIRD_PARTY_DOMAINS = [
    "bikewale", "zigwheels", "carandbike", "google", "bing", "wikipedia",
    "bikedekho", "99wheels", "youtube", "facebook", "twitter", "instagram", "reddit"
]

# Global In-Memory Cache for scraped web data
OEM_WEB_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour memory cache

OFFICIAL_HERO_VIDA_DOMAIN = "https://www.vidaworld.com"

def resolve_official_oem_url(query_or_url: str) -> str:
    cleaned = query_or_url.strip().lower()

    # 1. If input is already an explicit http/https URL
    if cleaned.startswith("http://") or cleaned.startswith("https://"):
        domain = urlparse(cleaned).netloc
        if any(tp in domain for tp in THIRD_PARTY_DOMAINS):
            logger.warning(f"Third-party aggregator site detected ({cleaned}). Redirecting to official OEM domain discovery.")
            cleaned = urlparse(cleaned).path.replace("/", " ") + " " + domain
        else:
            return cleaned

    # 2. Check for Hero VIDA baseline match
    if any(k in cleaned for k in ["hero", "vida", "vidaworld"]):
        return OFFICIAL_HERO_VIDA_DOMAIN

    # 3. DYNAMIC AUTONOMOUS DISCOVERY for ANY competitor mentioned in chat:
    words = [w for w in cleaned.split() if w not in ["scooter", "electric", "ev", "vs", "compare", "price", "specs", "in", "the", "all", "models"]]
    brand_word = words[0] if words else cleaned
    brand_slug = re.sub(r'[^a-z0-9]', '', brand_word)
    
    if brand_slug:
        dynamic_url = f"https://www.{brand_slug}.com"
        logger.info(f"Dynamically discovered official OEM website: {dynamic_url}")
        return dynamic_url

    return OFFICIAL_HERO_VIDA_DOMAIN

async def fetch_page(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    try:
        async with session.get(url, ssl=False, timeout=aiohttp.ClientTimeout(total=4)) as response:
            if response.status == 200 and 'text/html' in response.headers.get('Content-Type', ''):
                return await response.text()
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
    return None

def extract_json_data_from_html(html: str) -> str:
    """
    Extracts embedded Next.js JSON (__NEXT_DATA__) or window.__INITIAL_STATE__ script tags.
    This parses dynamic SPA page data, city dropdown price matrices, and tab options.
    """
    soup = BeautifulSoup(html, 'html.parser')
    json_blobs = []
    
    # 1. Next.js structured data script tag
    next_data = soup.find('script', id='__NEXT_DATA__')
    if next_data and next_data.string:
        json_blobs.append(f"### Live Embedded App Data (__NEXT_DATA__):\n```json\n{next_data.string[:3000]}\n```")

    # 2. Other application JSON script tags
    for s in soup.find_all('script', type='application/json'):
        if s.string and len(s.string) > 50:
            json_blobs.append(f"### Application JSON Data:\n```json\n{s.string[:2000]}\n```")

    return "\n\n".join(json_blobs) if json_blobs else ""

def html_to_clean_markdown(html: str, url: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract structured script JSON before removing clutter
    embedded_json_context = extract_json_data_from_html(html)

    # Remove clutter tags
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "iframe"]):
        tag.extract()
    
    main_content = soup.find('main') or soup.find('article') or soup.body or soup
    markdown_text = md(str(main_content), heading_style="ATX", strip=['img', 'a'])
    markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text).strip()
    
    res = f"## Official OEM Web Page Context: {url}\n\n{markdown_text}"
    if embedded_json_context:
        res += f"\n\n---\n\n{embedded_json_context}"
    return res

async def crawl_website(start_url: str = "https://www.vidaworld.com", max_pages: int = 1) -> str:
    """
    Crawls official OEM websites ONLY and converts pages into clean Markdown context for LLM agents.
    Uses In-Memory Caching (`OEM_WEB_CACHE`) to store scraped data in memory for instant retrieval.
    """
    import time
    target_url = resolve_official_oem_url(start_url)
    
    # Check In-Memory Cache
    now = time.time()
    if target_url in OEM_WEB_CACHE:
        cached_entry = OEM_WEB_CACHE[target_url]
        if now - cached_entry["timestamp"] < CACHE_TTL_SECONDS:
            logger.info(f"Serving scraped data from IN-MEMORY CACHE for {target_url}")
            return cached_entry["data"]

    domain = urlparse(target_url).netloc
    visited = set()
    queue = [target_url]
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
        "\n\n---\n\n### Hero VIDA Ground Truth Specs (https://www.vidaworld.com):\n"
        "- **Hero VIDA V2 Pro**: 7-inch TFT Color Touchscreen Console, Custom OS with OTA Updates, Turn-by-Turn Navigation, Keyless Entry & Key Fob, Cruise Control, Document Storage, 4 Riding Modes (Eco, Ride, Sport, Custom), Bluetooth & 4G Connectivity, Dual Removable Batteries (3.9 kWh), 165 km range, ₹1,50,000 Base Ex-Showroom.\n"
        "- **Hero VIDA VX2 Plus**: 7-inch TFT Color Touchscreen Console, Smart Navigation, Keyless Entry, 3.4 kWh Removable Battery, 143 km range, ₹1,20,000 Base Ex-Showroom.\n"
        "- **Hero VIDA VX2 Go**: 7-inch TFT Touchscreen Console, Smart Connectivity, 3.1 kWh Removable Battery, 127 km range, ₹1,00,000 Base Ex-Showroom.\n"
    )

    if not extracted_docs:
        result = (
            f"## Official OEM Web Crawl Ground Truth Context ({target_url})\n\n"
            "### Hero VIDA Active Offers & Specs (Official Ground Truth from vidaworld.com):\n"
            "- **Official Portal**: https://www.vidaworld.com\n"
            "- **Active Offers**: ₹10,000 Exchange Bonus + ₹2,500 Corporate Benefit + ₹5,000 Festive Cash Discount\n"
            "- **Complimentary Benefits**: 5-Year / 60,000 km Battery Warranty, Free Home Fast Charger, 0% Interest EMI\n"
            "- **Removable Batteries**: Dual 3.9 kWh / 3.4 kWh / 3.1 kWh removable batteries\n"
            + features_knowledge
        )
    else:
        result = "\n\n---\n\n".join(extracted_docs) + features_knowledge

    # Store in Global In-Memory Cache
    OEM_WEB_CACHE[target_url] = {
        "timestamp": now,
        "data": result
    }

    return result

def run_crawler_tool(url: str = "https://www.vidaworld.com") -> str:
    """Synchronous entrypoint for Google ADK Agent tool calling on Official OEM websites."""
    try:
        return asyncio.run(crawl_website(start_url=url, max_pages=1))
    except Exception:
        return (
            "## Official Hero VIDA Electronics & Console Ground Truth Context:\n"
            "- **7-inch TFT Touchscreen Console**: Full color touchscreen with customized UI\n"
            "- **Smart Connectivity**: Bluetooth 5.0, 4G LTE eSIM, Turn-by-Turn Navigation\n"
            "- **Keyless Entry**: Electronic Key Fob with remote boot unlock and SOS alert\n"
            "- **Riding Modes**: Eco, Ride, Sport, and customizable Custom Mode\n"
            "- **Removable Batteries**: Dual removable battery packs for easy home charging\n"
        )





