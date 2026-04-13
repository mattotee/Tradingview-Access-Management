import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# Bybit API v5 - read-only, no trading permissions needed
BASE_URL = 'https://api.bybit.com'

# The perps we track
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']


def get_funding_rates():
    """
    Fetch current funding rates for BTC, ETH, SOL perps
    Positive = longs paying shorts (bearish signal)
    Negative = shorts paying longs (bullish signal)
    """
    try:
        funding = {}

        for symbol in SYMBOLS:
            url = f'{BASE_URL}/v5/market/tickers'
            params = {
                'category': 'linear',
                'symbol': symbol
            }

            print(f'[Bybit] Fetching funding rate for {symbol}...')
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
                        'rate_8h': round(funding_rate * 100, 4),
                        'rate_annualised': round(funding_rate * 100 * 3 * 365, 2),
                    }
                    print(f'[Bybit] {clean_symbol} funding: {funding[clean_symbol]["rate"]}%')
            else:
                print(f'[Bybit] ERROR for {symbol}: {data.get("retMsg")}')

        return {'status': 'ok', 'data': funding, 'timestamp': datetime.now(timezone.utc).isoformat()}

    except requests.exceptions.RequestException as e:
        print(f'[Bybit] ERROR - {e}')
        return {'status': 'error', 'error': str(e), 'data': {}}


# Quick test
if __name__ == '__main__':
    print('Testing Bybit fetcher...')
    print()

    print('--- FUNDING RATES ---')
    rates = get_funding_rates()
    print(f'Status: {rates["status"]}')
    if rates['status'] == 'ok':
        for symbol, data in rates['data'].items():
            print(f'{symbol}: {data["rate"]}% per 8h')
    print()
    print('All done.')