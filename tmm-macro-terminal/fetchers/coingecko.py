import requests
from datetime import datetime, timezone

# CoinGecko free tier - no API key needed
# Rate limit: 30 calls/min - handled by our cache layer
BASE_URL = 'https://api.coingecko.com/api/v3'

# Maps our internal names to CoinGecko IDs
COIN_IDS = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'SOL': 'solana',
    'HYPE': 'hyperliquid'
}


def get_prices():
    """
    Fetch live prices + 24h change for BTC, ETH, SOL, HYPE
    Returns a clean dict ready for the frontend
    """
    try:
        ids = ','.join(COIN_IDS.values())
        url = f'{BASE_URL}/simple/price'
        params = {
            'ids': ids,
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true'
        }

        print(f'[CoinGecko] Fetching prices...')
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        prices = {}
        for symbol, cg_id in COIN_IDS.items():
            if cg_id in data:
                coin = data[cg_id]
                prices[symbol] = {
                    'price': coin.get('usd', 0),
                    'change_24h': round(coin.get('usd_24h_change', 0), 2),
                    'market_cap': coin.get('usd_market_cap', 0),
                    'volume_24h': coin.get('usd_24h_vol', 0),
                }
                print(f'[CoinGecko] {symbol}: ${prices[symbol]["price"]:,.2f} ({prices[symbol]["change_24h"]}%)')

        return {'status': 'ok', 'data': prices, 'timestamp': datetime.now(timezone.utc).isoformat()}

    except requests.exceptions.Timeout:
        print(f'[CoinGecko] ERROR - Request timed out')
        return {'status': 'error', 'error': 'timeout', 'data': {}}

    except requests.exceptions.RequestException as e:
        print(f'[CoinGecko] ERROR - {e}')
        return {'status': 'error', 'error': str(e), 'data': {}}


def get_global():
    """
    Fetch global crypto market data
    Returns BTC dominance, total market cap, 24h volume
    """
    try:
        url = f'{BASE_URL}/global'
        print(f'[CoinGecko] Fetching global market data...')
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json().get('data', {})

        result = {
            'btc_dominance': round(data.get('market_cap_percentage', {}).get('btc', 0), 1),
            'total_market_cap': data.get('total_market_cap', {}).get('usd', 0),
            'total_volume_24h': data.get('total_volume', {}).get('usd', 0),
            'market_cap_change_24h': round(data.get('market_cap_change_percentage_24h_usd', 0), 2)
        }

        print(f'[CoinGecko] BTC Dominance: {result["btc_dominance"]}%')
        print(f'[CoinGecko] Total Market Cap: ${result["total_market_cap"]:,.0f}')

        return {'status': 'ok', 'data': result, 'timestamp': datetime.now(timezone.utc).isoformat()}

    except requests.exceptions.RequestException as e:
        print(f'[CoinGecko] ERROR - {e}')
        return {'status': 'error', 'error': str(e), 'data': {}}


def get_fear_and_greed():
    """
    Fetch Fear & Greed Index from alternative.me
    Free, no key needed
    Returns current value, yesterday, 7d avg
    """
    try:
        url = 'https://api.alternative.me/fng/?limit=8'
        print(f'[F&G] Fetching Fear & Greed index...')
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json().get('data', [])

        if not data:
            return {'status': 'error', 'error': 'no data', 'data': {}}

        current = data[0]
        yesterday = data[1] if len(data) > 1 else current

        week_values = [int(d['value']) for d in data[:7]]
        avg_7d = round(sum(week_values) / len(week_values), 0)

        result = {
            'value': int(current['value']),
            'label': current['value_classification'],
            'yesterday': int(yesterday['value']),
            'avg_7d': int(avg_7d),
        }

        print(f'[F&G] Current: {result["value"]} ({result["label"]})')

        return {'status': 'ok', 'data': result, 'timestamp': datetime.now(timezone.utc).isoformat()}

    except requests.exceptions.RequestException as e:
        print(f'[F&G] ERROR - {e}')
        return {'status': 'error', 'error': str(e), 'data': {}}


# Quick test - run this file directly to check everything works
if __name__ == '__main__':
    print('Testing CoinGecko fetcher...')
    print()

    print('--- PRICES ---')
    prices = get_prices()
    print(f'Status: {prices["status"]}')
    print()

    print('--- GLOBAL ---')
    global_data = get_global()
    print(f'Status: {global_data["status"]}')
    print()

    print('--- FEAR & GREED ---')
    fg = get_fear_and_greed()
    print(f'Status: {fg["status"]}')
    print()

    print('All done.')