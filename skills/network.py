import logging
import httpx
from typing import Dict, Any, Optional

log = logging.getLogger("octopus.skill.network")

def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute network requests.
    Params:
        method: GET, POST, etc.
        url: target URL
        data: payload for POST (optional)
        headers: dict of headers (optional)
    """
    method = params.get("method", "GET").upper()
    url = params.get("url")
    data = params.get("data")
    headers = params.get("headers", {})

    if not url:
        return {"status": "error", "message": "URL is required"}

    try:
        with httpx.Client(timeout=10.0) as client:
            if method == "GET":
                response = client.get(url, headers=headers)
            elif method == "POST":
                response = client.post(url, json=data, headers=headers)
            else:
                return {"status": "error", "message": f"Unsupported method: {method}"}
            
            response.raise_for_status()
            
            # Try to parse JSON, else return raw text
            try:
                content = response.json()
            except:
                content = response.text[:1000] # Cap text length
                
            return {
                "status": "ok",
                "message": f"Request {method} {url} successful",
                "content": content,
                "code": response.status_code
            }
    except Exception as e:
        log.error(f"Network error: {e}")
        return {"status": "error", "message": str(e)}
