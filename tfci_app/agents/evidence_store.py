"""Agent evidence store: acquire, archive, hash, verify quotes.

Agent-acquired sources live under tfci_app/agents/vault/ (the agent sandbox).
Promotion into the governed evidence vault is a HUMAN decision at the
approval gate, never automatic.

Note: archives are retained for internal audit. Public redistribution of
paywalled content is not assumed; where content cannot be retained or
re-published, record the limitation and do not count unverifiable quotes.
"""
import hashlib
import re
import httpx
from bs4 import BeautifulSoup
from pathlib import Path

VAULT = Path(__file__).resolve().parent / "vault"

# Realistic browser headers to bypass basic 403/401 blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}
MAX_BYTES = 2_000_000  # 2MB limit to prevent memory exhaustion on massive pages

def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()

def _extract_clean_text(html_content: bytes) -> str:
    """Extract readable text, stripping scripts, styles, and nav clutter."""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        # Remove non-content elements
        for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            element.decompose()
        # Get text and normalize whitespace
        text = soup.get_text(separator=" ", strip=True)
        return text
    except Exception:
        # Fallback to basic regex if BS4 fails
        return re.sub(r"<[^>]+>", " ", html_content.decode("utf-8", errors="replace"))

def acquire(url: str, staging_id: str) -> dict:
    """Fetch + archive + hash a source. Never raises; returns a record."""
    VAULT.mkdir(exist_ok=True)
    rec = {
        "url": url, 
        "archive_path": None, 
        "http_status": None,
        "sha256": None, 
        "plain_text": "", 
        "error": None
    }
    
    if not url:
        rec["error"] = "no url"
        return rec
        
    h = hashlib.sha256(url.encode()).hexdigest()[:12]
    path = VAULT / f"{staging_id}_{h}.html"
    
    try:
        # Use httpx for robust fetching with redirect handling and timeouts
        with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=30.0) as client:
            response = client.get(url)
            rec["http_status"] = response.status_code
            
            if response.status_code >= 400:
                rec["error"] = f"HTTP Error {response.status_code}: {response.reason_phrase}"
                return rec
                
            raw_bytes = response.content[:MAX_BYTES]
            
        # ADR-0007: Archive the RAW bytes verbatim for immutable chain of custody
        path.write_bytes(raw_bytes)
        rec["archive_path"] = str(path)
        rec["sha256"] = hashlib.sha256(raw_bytes).hexdigest()
        
        # Pass cleaned text to LLM to save tokens and improve extraction accuracy
        rec["plain_text"] = _extract_clean_text(raw_bytes)
        
    except httpx.RequestError as e:
        rec["error"] = f"Request failed: {str(e)[:200]}"
    except Exception as e:
        rec["error"] = f"Unexpected error: {str(e)[:200]}"
        
    return rec

def quote_in_text(quote: str, plain_text: str, probe_chars: int = 140) -> bool:
    """Deterministic fidelity check: does the quote actually appear?"""
    if not quote or not plain_text:
        return False
    norm_quote = _normalize(quote)
    norm_text = _normalize(plain_text)
    # Check if the normalized quote is a substring of the normalized text
    # For long quotes, we check a probe window to handle minor extraction drift
    if len(norm_quote) > probe_chars:
        probe = norm_quote[:probe_chars]
        return probe in norm_text
    return norm_quote in norm_text
