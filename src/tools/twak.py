# src/tools/twak.py
# Direct HMAC-SHA256 HTTP client for the Trust Wallet API (TWAK).
# Termux-friendly: pure Python, no Node or keyring needed.
# Sign: METHOD + PATH + QUERY + ACCESS_ID + NONCE + DATE -> HMAC-SHA256 -> base64.
import os, sys, hmac, hashlib, base64, uuid
from datetime import datetime, timezone
from urllib.parse import quote
import requests
from dotenv import load_dotenv

load_dotenv()


BASE = os.getenv("TWAK_BASE_URL", "https://tws.trustwallet.com")
ACCESS_ID = os.getenv("TWAK_ACCESS_ID", "")
SECRET = os.getenv("TWAK_HMAC_SECRET", "")


def _qs(params):
    if not params:
        return ""
    parts = []
    for k, v in params.items():
        parts.append(str(k) + "=" + quote(str(v), safe=""))
    return "&".join(parts)


def _sign(method, path, query, nonce, date):
    msg = method + path + query + ACCESS_ID + nonce + date
    digest = hmac.new(SECRET.encode(), msg.encode(), hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


def request(method, path, params=None, timeout=30):
    method = method.upper()
    query = _qs(params)
    nonce = uuid.uuid4().hex
    date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sig = _sign(method, path, query, nonce, date)
    url = BASE + path + (("?" + query) if query else "")
    headers = {"X-TW-Credential": ACCESS_ID, "X-TW-Nonce": nonce, "X-TW-Date": date, "Authorization": sig}
    r = requests.request(method, url, headers=headers, timeout=timeout)
    return r.status_code, r.text


def search_assets(query="BNB", limit=5):
    return request("GET", "/v1/search/assets", {"query": query, "limit": limit})


def have_creds():
    return bool(ACCESS_ID and SECRET)


def main():
    if "--dry" in sys.argv:
        print("base:", BASE)
        print("creds present:", have_creds())
        print("dry run - no HTTP call.")
        return
    if not have_creds():
        print("Missing TWAK_ACCESS_ID / TWAK_HMAC_SECRET in .env.")
        sys.exit(1)
    q = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "BNB"
    code, body = search_assets(q, 5)
    print("HTTP", code)
    print(body[:1500])
    sys.exit(0 if code == 200 else 1)


if __name__ == "__main__":
    main()
