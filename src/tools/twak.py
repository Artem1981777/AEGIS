# src/tools/twak.py
# Thin wrapper around the official Trust Wallet Agent Kit (TWAK) CLI: @trustwallet/cli.
# Auth: Access ID + HMAC-SHA256 secret (twak init, or TWAK_ACCESS_ID / TWAK_HMAC_SECRET env).
import os, shutil, subprocess, sys
from dotenv import load_dotenv

load_dotenv()


def _base():
    if shutil.which("twak"):
        return ["twak"]
    return ["npx", "--yes", "@trustwallet/cli"]


def _env():
    env = dict(os.environ)
    aid = os.getenv("TWAK_ACCESS_ID")
    sec = os.getenv("TWAK_HMAC_SECRET")
    if aid:
        env["TWAK_ACCESS_ID"] = aid
    if sec:
        env["TWAK_HMAC_SECRET"] = sec
    return env


def cli(*args, timeout=120):
    cmd = _base() + list(args)
    print("[twak] $", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True, env=_env(), timeout=timeout)
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out.strip()


def auth_status():
    return cli("auth", "status")


def price(symbol="BNB"):
    return cli("price", symbol, "--json")


def compete_register(extra=None):
    args = ["compete", "register"]
    if extra:
        args += list(extra)
    return cli(*args)


def have_creds():
    return bool(os.getenv("TWAK_ACCESS_ID") and os.getenv("TWAK_HMAC_SECRET"))


def main():
    dry = "--dry" in sys.argv
    if dry:
        print("base cmd:", " ".join(_base()))
        print("creds present:", have_creds())
        print("would run: auth status -> price BNB --json -> compete register")
        print("dry run - no CLI call.")
        return
    if not have_creds():
        print("Missing TWAK_ACCESS_ID / TWAK_HMAC_SECRET. Get them at portal.trustwallet.com and add to .env.")
        sys.exit(1)
    if "--register" in sys.argv:
        code, out = compete_register()
    else:
        code, out = price("BNB")
    print(out)
    sys.exit(code)


if __name__ == "__main__":
    main()
