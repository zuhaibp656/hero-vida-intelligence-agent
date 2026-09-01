import os
import json
import time
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

SANDBOX_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sandbox_data")

def get_sandbox_dir() -> str:
    """Ensures sandbox directory exists and returns its absolute path."""
    os.makedirs(SANDBOX_BASE_DIR, exist_ok=True)
    return SANDBOX_BASE_DIR

def save_to_sandbox(oem_name: str, payload: Dict[str, Any], raw_dom: Optional[str] = None) -> str:
    """
    Saves scraped and verified OEM data into local sandbox file store.
    """
    sandbox_dir = get_sandbox_dir()
    slug = oem_name.lower().replace(" ", "_").replace(".", "_")
    timestamp = int(time.time())
    
    # Save structured JSON
    filename = f"{slug}_latest.json"
    filepath = os.path.join(sandbox_dir, filename)
    
    data_to_store = {
        "oem": oem_name,
        "timestamp": timestamp,
        "timestamp_str": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)),
        "data": payload
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data_to_store, f, indent=2, ensure_ascii=False)
        
    # Also save raw DOM / markdown context if provided
    if raw_dom:
        dom_file = os.path.join(sandbox_dir, f"{slug}_dom.md")
        with open(dom_file, "w", encoding="utf-8") as f:
            f.write(raw_dom)
            
    logger.info(f"Successfully stored {oem_name} data in sandbox at {filepath}")
    return filepath

def load_from_sandbox(oem_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves stored OEM data from sandbox.
    """
    sandbox_dir = get_sandbox_dir()
    slug = oem_name.lower().replace(" ", "_").replace(".", "_")
    filepath = os.path.join(sandbox_dir, f"{slug}_latest.json")
    
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading {filepath} from sandbox: {e}")
            return None
    return None

def list_sandbox_contents() -> List[Dict[str, Any]]:
    """
    Lists all available OEM datasets currently saved in the sandbox.
    """
    sandbox_dir = get_sandbox_dir()
    results = []
    if not os.path.exists(sandbox_dir):
        return results
        
    for fname in os.listdir(sandbox_dir):
        if fname.endswith("_latest.json"):
            fpath = os.path.join(sandbox_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    results.append({
                        "file": fname,
                        "oem": data.get("oem", "Unknown"),
                        "timestamp": data.get("timestamp_str", ""),
                        "models_count": len(data.get("data", {}).get("models", []))
                    })
            except Exception:
                continue
    return results

def query_sandbox_models(oem_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns a unified list of all structured models across all OEMs in the sandbox.
    """
    sandbox_dir = get_sandbox_dir()
    all_models = []
    if not os.path.exists(sandbox_dir):
        return all_models
        
    for fname in os.listdir(sandbox_dir):
        if fname.endswith("_latest.json"):
            fpath = os.path.join(sandbox_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    oem = content.get("oem", "")
                    if oem_filter and oem_filter.lower() not in oem.lower() and oem.lower() not in oem_filter.lower():
                        continue
                    models = content.get("data", {}).get("models", [])
                    all_models.extend(models)
            except Exception:
                continue
    return all_models
