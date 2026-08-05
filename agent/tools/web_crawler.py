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
        async with session.get(url, ssl=False, timeout=aiohttp.ClientTimeout(total=15)) as response:
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

async def crawl_website(start_url: str = "https://www.vidaworld.com", max_pages: int = 3) -> str:
    """
    Crawls the specified website and converts pages into clean Markdown context for LLM agents.
    """
    domain = urlparse(start_url).netloc
    visited = set()
    queue = [start_url]
    extracted_docs = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

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

                # Find internal links
                soup = BeautifulSoup(html, 'html.parser')
                for a in soup.find_all('a', href=True):
                    full = urljoin(current_url, a['href']).split('#')[0]
                    if urlparse(full).netloc == domain and full not in visited and full not in queue:
                        # Prioritize vehicle / product / pricing pages
                        if any(k in full.lower() for k in ['scooter', 'vx2', 'v2', 'price', 'product', 'dealers']):
                            queue.insert(0, full)
                        else:
                            queue.append(full)

    if not extracted_docs:
        return f"Could not extract live content from {start_url}. Using cached specification data."

    return "\n\n---\n\n".join(extracted_docs)

def run_crawler_tool(url: str = "https://www.vidaworld.com") -> str:
    """Synchronous entrypoint for Google ADK Agent tool calling."""
    return asyncio.run(crawl_website(start_url=url, max_pages=3))
