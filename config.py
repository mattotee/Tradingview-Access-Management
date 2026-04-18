import os

# ─────────────────────────────────────────────
# TradingView API endpoints (internal API)
# ─────────────────────────────────────────────
TV_URLS = dict(
    tvcoins="https://www.tradingview.com/tvcoins/details/",
    username_hint="https://www.tradingview.com/username_hint/",
    list_users="https://www.tradingview.com/pine_perms/list_users/",
    modify_access="https://www.tradingview.com/pine_perms/modify_user_expiration/",
    add_access="https://www.tradingview.com/pine_perms/add/",
    remove_access="https://www.tradingview.com/pine_perms/remove/",
    signin="https://www.tradingview.com/accounts/signin/",
)

# ─────────────────────────────────────────────
# TMM Indicator Pine IDs
# Loaded from environment variables.
# Use the shortname (e.g. "VCI") in Make automation
# requests for readability.
# ─────────────────────────────────────────────
PINE_IDS = {
    "VCI":   os.environ.get("TV_VCI_ID",   "PUB;51ca8acd0b0d4ac00bd9684a3d989a427"),
    "CCO":   os.environ.get("TV_CCO_ID",   "PUB;ffa472cc81d34f908514dc05946cf84a"),
    "CCPRO": os.environ.get("TV_CCPRO_ID", "PUB;c37df8f0c33c41b1afccf49df071009a"),
    "VPI":   os.environ.get("TV_VPI_ID",   "PUB;y7e62ed783a64aa99b6a302f1b2d97a3"),
    "WCO":   os.environ.get("TV_WCO_ID",   "PUB;5477dfc3518642228abbe2d6c5b55579"),
}

# ─────────────────────────────────────────────
# Service credentials (set in .env / systemd)
# ─────────────────────────────────────────────
TV_USERNAME = os.environ.get("TV_SERVICE_USERNAME", "TMMEdge")
TV_PASSWORD = os.environ.get("TV_SERVICE_PASSWORD", "")

# API key - Make must send this in X-API-Key header
API_KEY = os.environ.get("TMM_API_KEY", "")

# Path for caching the TradingView session cookie
SESSION_FILE = os.environ.get("SESSION_FILE", "/home/tmm/tv_session.json")
