"""
Utilities: client factory, validation, structured logging.
"""

import os
import time
import hmac
import hashlib
import logging
import json
from logging.handlers import RotatingFileHandler

# Try importing official connector; else we'll operate in dry-run.
try:
    from binance.client import Client as BinanceClient  # python-binance older name
    from binance import ThreadedWebsocketManager
    BINANCE_AVAILABLE = True
except Exception:
    BINANCE_AVAILABLE = False

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bot.log")


def setup_logger(name="bot", level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


logger = setup_logger()


def log_action(action: str, details: dict):
    """
    Structured JSON log entry.
    """
    entry = {
        "ts": int(time.time() * 1000),
        "action": action,
        "details": details
    }
    logger.info(json.dumps(entry))


# Basic input validators
def valid_symbol(sym: str) -> bool:
    return isinstance(sym, str) and sym.isalnum()


def valid_side(side: str) -> bool:
    return side.upper() in {"BUY", "SELL"}


def valid_decimal(x) -> bool:
    try:
        float(x)
        return True
    except Exception:
        return False


def get_client(api_key: str = None, api_secret: str = None, testnet=False, dry_run=True):
    """
    Returns a Binance client wrapper if library present and keys supplied.
    If dry_run is True or keys missing, returns None (caller should simulate).
    """
    api_key = api_key or os.environ.get("BINANCE_API_KEY")
    api_secret = api_secret or os.environ.get("BINANCE_API_SECRET")
    if dry_run:
        log_action("client.init", {"mode": "dry-run"})
        return None
    if not api_key or not api_secret:
        log_action("client.init", {"mode": "missing-keys"})
        return None

    if BINANCE_AVAILABLE:
        client = BinanceClient(api_key, api_secret)
        # Optionally configure testnet endpoints if user wants.
        if testnet:
            client.API_URL = 'https://testnet.binancefuture.com'
        log_action("client.init", {"mode": "live", "testnet": testnet})
        return client
    else:
        log_action("client.init", {"mode": "lib-not-installed"})
        return None


# Helper to format responses uniformly
def make_result(ok: bool, msg: str, meta: dict = None):
    return {"ok": ok, "message": msg, "meta": meta or {}}
