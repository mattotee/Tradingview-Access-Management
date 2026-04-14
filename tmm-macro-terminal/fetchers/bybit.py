import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

BASE_URL = 'https://api.bybit.com'
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']


def get_funding_rates():
    """
    Fetch current funding rates for BTC, ETH, SOL perps
    Positive = longs paying shorts (bearish sentiment)
    Negative = shorts paying longs (bullish sentiment)
    """
    try:
        funding = {}
        for symbol in SYMBOLS:
            url = f'{BASE_URL}/v5/market/tickers'
            params = {'category': 'linear', 'symbol': symbol}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('retCode') == 0:
                items = data.get('result', {}).get('list', [])
                if items:
                    ticker = items[0]
                    funding_rate = float(ticker.get('fundingRate', 0))
                    clean_symbol = symbol.replace('USDT', '')
                    funding[clean_symbol] = {
                        'rate': round(funding_rate * 100, 4),
                        'rate_annualised': round(funding_rate * 100 * 3 * 365, 2),
                    }
                    print(f'[Bybit] {clean_symbol} funding: {funding[clean_symbol]["rate"]}%')
        return {'status': 'ok', 'data': funding, 'timestamp': datetime.now(timezone.utc).isoformat()}
    except requests.exceptions.RequestException as e:
        print(f'[Bybit] ERROR - {e}')
        return {'status': 'error', 'error': str(e), 'data': {}}


def get_long_short_ratio():
    """
    Fetch long/short ratio for BTC, ETH, SOL
    > 50% long = traders are bullish
    < 50% long = traders are bearish
    """
    try:
        ratios = {}
        for symbol in SYMBOLS:
            url = f'{BASE_URL}/v5/market/account-ratio'
            params = {
                'category': 'linear',
                'symbol': symbol,
                'period': '1h',
                'limit': 1
            }
            print(f'[Bybit] Fetching L/S ratio for {symbol}...')
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('retCode') == 0:
                items = data.get('result', {}).get('list', [])
                if items:
                    clean_symbol = symbol.replace('USDT', '')
                    buy_ratio = float(items[0].get('buyRatio', 0.5))
                    sell_ratio = float(items[0].get('sellRatio', 0.5))
                    ratios[clean_symbol] = {
                        'long_pct': round(buy_ratio * 100, 1),
                        'short_pct': round(sell_ratio * 100, 1),
                        'bias': 'LONG' if buy_ratio > sell_ratio else 'SHORT'
                    }
                    print(f'[Bybit] {clean_symbol} L/S: {ratios[clean_symbol]["long_pct"]}% / {ratios[clean_symbol]["short_pct"]}%')
        return {'status': 'ok', 'data': ratios, 'timestamp': datetime.now(timezone.utc).isoformat()}
    except requests.exceptions.RequestException as e:
        print(f'[Bybit] L/S ERROR - {e}')
        return {'status': 'error', 'error': str(e), 'data': {}}


def get_market_structure():
    """
    Combined call - funding rates + long/short ratios
    Returns everything needed for the Market Structure panel
    """
    funding = get_funding_rates()
    ls = get_long_short_ratio()

    combined = {}
    for sym in ['BTC', 'ETH', 'SOL']:
        combined[sym] = {
            'funding_rate': funding['data'].get(sym, {}).get('rate'),
            'funding_annualised': funding['data'].get(sym, {}).get('rate_annualised'),
            'long_pct': ls['data'].get(sym, {}).get('long_pct'),
            'short_pct': ls['data'].get(sym, {}).get('short_pct'),
            'bias': ls['data'].get(sym, {}).get('bias'),
        }

    return {
        'status': 'ok',
        'data': combined,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


# Quick test
if __name__ == '__main__':
    print('Testing Bybit fetcher...')
    print()

    print('--- MARKET STRUCTURE ---')
    ms = get_market_structure()
    print(f'Status: {ms["status"]}')
    for sym, d in ms['data'].items():
        print(f'  {sym}: {d["long_pct"]}% Long / {d["short_pct"]}% Short | Bias: {d["bias"]} | Funding: {d["funding_rate"]}%')

    print()
    print('All done.')