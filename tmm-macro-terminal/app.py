import os
import threading
import time
from datetime import datetime, timezone
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Import all fetchers
from fetchers.coingecko import get_prices, get_global, get_fear_and_greed
from fetchers.bybit import get_funding_rates
from fetchers.yahoo import get_indices, get_commodities, get_fx
from fetchers.fred import get_macro
from fetchers.finnhub import get_all_news, get_session_status
from fetchers.economic_calendar import get_calendar, get_next_high_impact
from cache.cache_manager import get_or_fetch, invalidate_cache, write_cache


# ============================================================
# HELPER - build combined crypto payload
# ============================================================

def fetch_crypto():
    prices = get_prices()
    global_data = get_global()
    fg = get_fear_and_greed()
    funding = get_funding_rates()

    if prices['status'] != 'ok':
        return prices

    # Merge funding rates into price data
    for symbol in prices['data']:
        prices['data'][symbol]['funding_rate'] = funding['data'].get(symbol, {}).get('rate', None)

    return {
        'status': 'ok',
        'data': {
            'prices': prices['data'],
            'global': global_data.get('data', {}),
            'fear_and_greed': fg.get('data', {}),
        }
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'service': 'TMM Macro Terminal',
        'version': '1.0.0',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'environment': os.getenv('FLASK_ENV', 'development')
    })


# ============================================================
# API ROUTES
# ============================================================

@app.route('/api/crypto')
def crypto():
    result = get_or_fetch('crypto', fetch_crypto)
    return jsonify({
        'status': 'ok',
        'stale': result['stale'],
        'source': result['source'],
        'data': result['data']
    })


@app.route('/api/indices')
def indices():
    result = get_or_fetch('indices', get_indices)
    return jsonify({
        'status': 'ok',
        'stale': result['stale'],
        'source': result['source'],
        'data': result['data']
    })


@app.route('/api/macro')
def macro():
    result = get_or_fetch('macro', get_macro)
    return jsonify({
        'status': 'ok',
        'stale': result['stale'],
        'source': result['source'],
        'data': result['data']
    })


@app.route('/api/commodities')
def commodities():
    result = get_or_fetch('commodities', get_commodities)
    return jsonify({
        'status': 'ok',
        'stale': result['stale'],
        'source': result['source'],
        'data': result['data']
    })


@app.route('/api/fx')
def fx():
    result = get_or_fetch('fx', get_fx)
    return jsonify({
        'status': 'ok',
        'stale': result['stale'],
        'source': result['source'],
        'data': result['data']
    })


@app.route('/api/news')
def news():
    result = get_or_fetch('news', get_all_news)
    return jsonify({
        'status': 'ok',
        'stale': result['stale'],
        'source': result['source'],
        'data': result['data']
    })


@app.route('/api/calendar')
def calendar():
    result = get_or_fetch('calendar', get_calendar)
    return jsonify({
        'status': 'ok',
        'stale': result['stale'],
        'source': result['source'],
        'data': result['data']
    })


@app.route('/api/sessions')
def sessions():
    # Sessions are calculated not fetched - no need to cache
    result = get_session_status()
    return jsonify({
        'status': 'ok',
        'data': result['data'],
        'current_utc': result['current_utc'],
        'is_weekend': result['is_weekend']
    })


@app.route('/api/all')
def all_data():
    """
    Single aggregated endpoint - this is what the frontend calls
    Returns everything in one hit
    """
    crypto = get_or_fetch('crypto', fetch_crypto)
    indices = get_or_fetch('indices', get_indices)
    macro = get_or_fetch('macro', get_macro)
    commodities = get_or_fetch('commodities', get_commodities)
    fx = get_or_fetch('fx', get_fx)
    news = get_or_fetch('news', get_all_news)
    calendar = get_or_fetch('calendar', get_calendar)
    sessions = get_session_status()
    alert = get_next_high_impact()

    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'data': {
            'crypto': crypto['data'],
            'indices': indices['data'],
            'macro': macro['data'],
            'commodities': commodities['data'],
            'fx': fx['data'],
            'news': news['data'],
            'calendar': calendar['data'],
            'sessions': sessions['data'],
            'alert': alert,
        }
    })


@app.route('/api/refresh')
def refresh():
    """
    Force-clear all cache files and re-fetch everything
    Use this if data looks stale or wrong
    """
    print('[API] Manual cache refresh triggered')
    invalidate_cache()
    return jsonify({
        'status': 'ok',
        'message': 'Cache cleared - next request will fetch fresh data'
    })


# ============================================================
# BACKGROUND CACHE PRE-WARMER
# Runs in a separate thread, keeps cache fresh automatically
# ============================================================

def prewarm_cache():
    """
    Pre-warm cache on startup and keep it refreshed in background
    Runs forever in a daemon thread
    """
    print('[PreWarm] Starting background cache warmer...')

    # Small delay to let Flask start up first
    time.sleep(3)

    while True:
        try:
            print('[PreWarm] Refreshing crypto cache...')
            result = fetch_crypto()
            if result['status'] == 'ok':
                write_cache('crypto', result['data'])

            print('[PreWarm] Refreshing indices cache...')
            result = get_indices()
            if result['status'] == 'ok':
                write_cache('indices', result['data'])

            print('[PreWarm] Refreshing commodities cache...')
            result = get_commodities()
            if result['status'] == 'ok':
                write_cache('commodities', result['data'])

            print('[PreWarm] Refreshing FX cache...')
            result = get_fx()
            if result['status'] == 'ok':
                write_cache('fx', result['data'])

            print('[PreWarm] Refreshing news cache...')
            result = get_all_news()
            if result['status'] == 'ok':
                write_cache('news', result['data'])

            print('[PreWarm] Refreshing macro cache...')
            result = get_macro()
            if result['status'] == 'ok':
                write_cache('macro', result['data'])

            print('[PreWarm] Refreshing calendar cache...')
            result = get_calendar()
            if result['status'] == 'ok':
                write_cache('calendar', result['data'])

            print('[PreWarm] Cache refresh complete. Sleeping 60s...')
            time.sleep(60)

        except Exception as e:
            print(f'[PreWarm] ERROR - {e}')
            time.sleep(30)


# ============================================================
# SERVER STARTUP
# ============================================================

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5001))

    # Start background cache warmer in daemon thread
    cache_thread = threading.Thread(target=prewarm_cache, daemon=True)
    cache_thread.start()

    print(f'')
    print(f'  TMM Macro Terminal - Backend Server')
    print(f'  ------------------------------------')
    print(f'  Running on:   http://localhost:{port}')
    print(f'  Health check: http://localhost:{port}/health')
    print(f'  All data:     http://localhost:{port}/api/all')
    print(f'  Environment:  {os.getenv("FLASK_ENV", "development")}')
    print(f'')

    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )