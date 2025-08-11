import datetime as _dt
import mimetypes
import os
import pathlib
import time as _time
from typing import Dict, Tuple

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Environment variables inside the kernel VM
# ---------------------------------------------------------------------------

TOKEN_ENV = "LUMERA_TOKEN"
BASE_URL_ENV = "LUMERA_BASE_URL"
ENV_PATH = "/root/.env"

# Load variables from /root/.env if it exists (and also current dir .env)
load_dotenv(override=False)  # Local .env (no-op in prod)
load_dotenv(ENV_PATH, override=False)


# Determine API base URL ------------------------------------------------------

_default_api_base = "https://app.lumerahq.com/api"
API_BASE = os.getenv(BASE_URL_ENV, _default_api_base).rstrip("/")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _ensure_token() -> str:
    """Return the personal Lumera token, loading /root/.env if necessary."""

    token = os.getenv(TOKEN_ENV)
    if token:
        return token

    raise RuntimeError(
        f"{TOKEN_ENV} environment variable not set (checked environment and {ENV_PATH})"
    )


# ---------------------------------------------------------------------------
# Provider-agnostic access-token retrieval
# ---------------------------------------------------------------------------


# _token_cache maps provider
# without an explicit expiry (e.g. API keys) we store `float('+inf')` so that
# they are never considered stale.
# Map provider -> (token, expiry)
_token_cache: dict[str, Tuple[str, float]] = {}

# ``expires_at`` originates from the Lumera API and may be one of several
# formats: epoch seconds (``int``/``float``), an RFC 3339 / ISO-8601 string, or
# even ``None``. We therefore accept ``Any`` and normalise it internally.


# Accept multiple formats returned by the API (epoch seconds or ISO-8601), or
# ``None`` when the token never expires.


def _parse_expiry(expires_at: int | float | str | None) -> float:
    """Convert `expires_at` from the API (may be ISO8601 or epoch) to epoch seconds.

    Returns +inf if `expires_at` is falsy/None.
    """

    if not expires_at:
        return float("inf")

    if isinstance(expires_at, (int, float)):
        return float(expires_at)

    # Assume RFC 3339 / ISO 8601 string.
    if isinstance(expires_at, str):
        if expires_at.endswith("Z"):
            expires_at = expires_at[:-1] + "+00:00"
        return _dt.datetime.fromisoformat(expires_at).timestamp()

    raise TypeError(f"Unsupported expires_at format: {type(expires_at)!r}")


def _fetch_access_token(provider: str) -> Tuple[str, float]:
    """Call the Lumera API to obtain a valid access token for *provider*."""

    provider = provider.lower().strip()
    if not provider:
        raise ValueError("provider is required")

    token = _ensure_token()

    url = f"{API_BASE}/connections/{provider}/access-token"
    headers = {"Authorization": f"token {token}"}

    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()

    data = resp.json()
    access_token = data.get("access_token")
    expires_at = data.get("expires_at")

    if not access_token:
        raise RuntimeError(f"Malformed response from Lumera when fetching {provider} access token")

    expiry_ts = _parse_expiry(expires_at)
    return access_token, expiry_ts


def get_access_token(provider: str, min_valid_seconds: int = 900) -> str:
    """Return a cached access token for *provider* valid
    *min_valid_seconds*.

       Automatically refreshes tokens via the Lumera API when they are missing or
       close to expiry.  For tokens without an expiry (API keys) the first value
       is cached indefinitely.
    """

    global _token_cache

    provider = provider.lower().strip()
    if not provider:
        raise ValueError("provider is required")

    now = _time.time()

    cached = _token_cache.get(provider)
    if cached is not None:
        access_token, expiry_ts = cached
        if (expiry_ts - now) >= min_valid_seconds:
            return access_token

    # (Re)fetch from server
    access_token, expiry_ts = _fetch_access_token(provider)
    _token_cache[provider] = (access_token, expiry_ts)
    return access_token


# Backwards-compatibility wrapper ------------------------------------------------


def get_google_access_token(min_valid_seconds: int = 900) -> str:
    """Legacy helper kept for old notebooks
    delegates to get_access_token."""

    return get_access_token("google", min_valid_seconds=min_valid_seconds)


# ---------------------------------------------------------------------------
# Document upload helper (unchanged apart from minor refactoring)
# ---------------------------------------------------------------------------


def _pretty_size(size: int) -> str:
    """Return *size* in bytes as a human-readable string (e.g. "1.2 MB").

    Iteratively divides by 1024 and appends the appropriate unit all the way up
    to terabytes.
    """

    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def _upload_session_file(file_path: str, session_id: str) -> Dict:
    """Upload file into the current Playground session's file space."""

    token = _ensure_token()
    path = pathlib.Path(file_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path)

    filename = path.name
    size = path.stat().st_size
    mimetype = mimetypes.guess_type(filename)[0] or "application/octet-stream"

    headers = {"Authorization": f"token {token}", "Content-Type": "application/json"}

    # 1) Get signed upload URL
    resp = requests.post(
        f"{API_BASE}/sessions/{session_id}/files/upload-url",
        json={"filename": filename, "content_type": mimetype, "size": size},
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    upload_url: str = data["upload_url"]
    notebook_path: str = data.get("notebook_path", "")

    # 2) Upload bytes
    with open(path, "rb") as fp:
        put = requests.put(upload_url, data=fp, headers={"Content-Type": mimetype}, timeout=300)
        put.raise_for_status()

    # 3) Optionally enable docs (idempotent; ignore errors)
    try:
        requests.post(
            f"{API_BASE}/sessions/{session_id}/enable-docs",
            headers=headers,
            timeout=15,
        )
    except Exception:
        pass

    return {"name": filename, "notebook_path": notebook_path}


def _upload_document(file_path: str) -> Dict:
    """Fallback: Upload file into global Documents collection."""

    token = _ensure_token()
    path = pathlib.Path(file_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path)

    filename = path.name
    size = path.stat().st_size
    mimetype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    pretty = _pretty_size(size)

    headers = {"Authorization": f"token {token}", "Content-Type": "application/json"}
    documents_base = f"{API_BASE}/documents"

    # 1) Create
    resp = requests.post(
        documents_base,
        json={
            "title": filename,
            "content": f"File to be uploaded: {filename} ({pretty})",
            "type": mimetype.split("/")[-1],
            "status": "uploading",
        },
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    doc = resp.json()
    doc_id = doc["id"]

    # 2) Signed URL
    resp = requests.post(
        f"{documents_base}/{doc_id}/upload-url",
        json={"filename": filename, "content_type": mimetype, "size": size},
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    upload_url: str = resp.json()["upload_url"]

    # 3) PUT bytes
    with open(path, "rb") as fp:
        put = requests.put(upload_url, data=fp, headers={"Content-Type": mimetype}, timeout=300)
        put.raise_for_status()

    # 4) Finalize
    resp = requests.put(
        f"{documents_base}/{doc_id}",
        json={
            "status": "uploaded",
            "content": f"Uploaded file: {filename} ({pretty})",
        },
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def save_to_lumera(file_path: str) -> Dict:
    """Upload *file_path* to the active Playground session if available,
    otherwise fall back to the global Documents collection."""

    session_id = os.getenv("LUMERA_SESSION_ID", "").strip()
    if session_id:
        return _upload_session_file(file_path, session_id)
    return _upload_document(file_path)
