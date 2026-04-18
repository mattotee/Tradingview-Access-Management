import json
import logging
from functools import wraps
from flask import Flask, request, jsonify
from tradingview import TradingView
import config

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("tmm-tv-gateway")

app = Flask("tmm-tv-gateway")


# ─────────────────────────────────────────────
# API Key authentication decorator
# Make sends X-API-Key header on every request.
# Set TMM_API_KEY in your .env file.
# ─────────────────────────────────────────────
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key", "")
        if not config.API_KEY:
            logger.warning("TMM_API_KEY not set - running without auth (not safe for production)")
        elif key != config.API_KEY:
            logger.warning(f"Unauthorised request from {request.remote_addr}")
            return jsonify({"error": "Unauthorised"}), 401
        return f(*args, **kwargs)
    return decorated


def resolve_pine_id(identifier):
    """
    Accept either a shortname ("VCI", "CCO" etc) or a full pine ID ("PUB;xxx").
    Returns the full pine ID string, or raises ValueError if not found.
    """
    if identifier.upper() in config.PINE_IDS:
        return config.PINE_IDS[identifier.upper()]
    if identifier.startswith("PUB;"):
        return identifier
    raise ValueError(f"Unknown indicator identifier: {identifier}. Use a shortname (VCI, CCO, CCPRO, VPI, WCO) or a full PUB; ID.")


# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    """
    Health check - no auth required.
    Returns service status and whether the TV session is active.
    """
    try:
        tv = TradingView()
        return jsonify({
            "status": "ok",
            "service": "tmm-tv-gateway",
            "tv_session": "active",
            "indicators": list(config.PINE_IDS.keys()),
        }), 200
    except Exception as e:
        return jsonify({"status": "degraded", "error": str(e)}), 503


@app.route("/validate-user", methods=["GET"])
@require_api_key
def validate_user():
    """
    Validate a TradingView username before granting access.

    Query params:
        username (required)

    Returns:
        { valid: bool, username: str }

    Make automation should call this first and halt if valid=false,
    then email the customer to resubmit their correct TV username.
    """
    username = request.args.get("username", "").strip()
    if not username:
        return jsonify({"error": "username parameter is required"}), 400

    try:
        tv = TradingView()
        result = tv.validate_username(username)
        logger.info(f"validate-user: {username} -> valid={result['valid']}")
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"validate-user error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/add-access", methods=["POST"])
@require_api_key
def add_access():
    """
    Grant access to one or more indicators.

    Body (JSON):
        username   (required) - TradingView username
        indicators (required) - list of shortnames or pine IDs e.g. ["VCI"] or ["VCI","CCO"]
        duration   (required) - e.g. "1M" (1 month), "1Y", "7D", "L" (lifetime)

    Returns list of access results, one per indicator.

    Example Make call for an Edge Bundle purchase:
        { "username": "mattotee_trader", "indicators": ["VCI","CCO","CCPRO","VPI"], "duration": "1M" }
    """
    body = request.get_json()
    if not body:
        return jsonify({"error": "JSON body required"}), 400

    username = body.get("username", "").strip()
    indicators = body.get("indicators", [])
    duration = body.get("duration", "1M").strip()

    if not username:
        return jsonify({"error": "username is required"}), 400
    if not indicators:
        return jsonify({"error": "indicators list is required"}), 400

    # Parse duration string e.g. "1M" -> type="M", length=1
    try:
        d_length = int(duration[:-1])
        d_type = duration[-1:].upper()
    except (ValueError, IndexError):
        return jsonify({"error": f"Invalid duration format '{duration}'. Use e.g. '1M', '7D', '1Y', 'L'"}), 400

    try:
        tv = TradingView()
        results = []
        for indicator in indicators:
            try:
                pine_id = resolve_pine_id(indicator)
                access = tv.get_access_details(username, pine_id)
                result = tv.add_access(access, d_type, d_length)
                result["indicator"] = indicator.upper() if not indicator.startswith("PUB;") else indicator
                results.append(result)
            except ValueError as ve:
                results.append({"indicator": indicator, "status": "error", "error": str(ve)})

        logger.info(f"add-access: {username} | {indicators} | duration={duration} | results={[r['status'] for r in results]}")
        return jsonify(results), 200

    except Exception as e:
        logger.error(f"add-access error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/remove-access", methods=["POST"])
@require_api_key
def remove_access():
    """
    Revoke access to one or more indicators.

    Body (JSON):
        username   (required) - TradingView username
        indicators (required) - list of shortnames or pine IDs

    Called by Make on:
        - Stripe subscription cancelled/payment failed
        - NOWPayments IPN status: expired
        - Manual revocation

    Example:
        { "username": "mattotee_trader", "indicators": ["VCI"] }
    """
    body = request.get_json()
    if not body:
        return jsonify({"error": "JSON body required"}), 400

    username = body.get("username", "").strip()
    indicators = body.get("indicators", [])

    if not username:
        return jsonify({"error": "username is required"}), 400
    if not indicators:
        return jsonify({"error": "indicators list is required"}), 400

    try:
        tv = TradingView()
        results = []
        for indicator in indicators:
            try:
                pine_id = resolve_pine_id(indicator)
                access = tv.get_access_details(username, pine_id)
                result = tv.remove_access(access)
                result["indicator"] = indicator.upper() if not indicator.startswith("PUB;") else indicator
                results.append(result)
            except ValueError as ve:
                results.append({"indicator": indicator, "status": "error", "error": str(ve)})

        logger.info(f"remove-access: {username} | {indicators} | results={[r['status'] for r in results]}")
        return jsonify(results), 200

    except Exception as e:
        logger.error(f"remove-access error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/check-access", methods=["GET"])
@require_api_key
def check_access():
    """
    Check current access status for a user on one or more indicators.

    Query params:
        username   (required)
        indicators (required) - comma-separated e.g. "VCI,CCO"

    Returns list of current access details.
    """
    username = request.args.get("username", "").strip()
    indicators_param = request.args.get("indicators", "").strip()

    if not username:
        return jsonify({"error": "username parameter is required"}), 400
    if not indicators_param:
        return jsonify({"error": "indicators parameter is required"}), 400

    indicators = [i.strip() for i in indicators_param.split(",")]

    try:
        tv = TradingView()
        results = []
        for indicator in indicators:
            try:
                pine_id = resolve_pine_id(indicator)
                access = tv.get_access_details(username, pine_id)
                access["indicator"] = indicator.upper() if not indicator.startswith("PUB;") else indicator
                results.append(access)
            except ValueError as ve:
                results.append({"indicator": indicator, "error": str(ve)})

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"check-access error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/extend-access", methods=["POST"])
@require_api_key
def extend_access():
    """
    Extend access for an existing subscriber (monthly renewal).

    Body (JSON):
        username   (required) - TradingView username
        indicators (required) - list of shortnames or pine IDs
        duration   (required) - e.g. "1M"

    This is functionally identical to add-access but semantically
    clearer in Make automations - called on subscription renewal events.
    """
    # Extend is the same operation as add (it modifies the expiration)
    # so we just delegate to the add_access logic
    return add_access()


def start_server():
    port = int(__import__("os").environ.get("PORT", 5001))
    logger.info(f"TMM TradingView Gateway starting on port {port}")
    app.run(host="0.0.0.0", port=port)
