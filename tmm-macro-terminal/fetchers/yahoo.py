import yfinance as yf
from datetime import datetime, timezone


# ============================================================
# INDICES
# ============================================================

US_INDICES = {
    'S&P 500': '^GSPC',
    'NASDAQ': '^IXIC',
    'Dow Jones': '^DJI',
    'VIX': '^VIX',
}

ASIA_INDICES = {
    'ASX 200': '^AXJO',
    'Nikkei 225': '^N225',
    'Hang Seng': '^HSI',
    'CSI 300': '000300.SS',
}

EUROPE_INDICES = {
    'FTSE 100': '^FTSE',
    'DAX 40': '^GDAXI',
    'CAC 40': '^FCHI',
    'STOXX 50': '^STOXX50E',
}

# ============================================================
# COMMODITIES
# ============================================================

COMMODITIES = {
    'Gold': 'GC=F',
    'Silver': 'SI=F',
    'WTI Crude': 'CL=F',
    'Brent Crude': 'BZ=F',
    'Copper': 'HG=F',
    'Natural Gas': 'NG=F',
}

# ============================================================
# FX
# ============================================================

FX_PAIRS = {
    'AUD/USD': 'AUDUSD=X',
    'USD/JPY': 'JPY=X',
    'EUR/USD': 'EURUSD=X',
    'GBP/USD': 'GBPUSD=X',
    'DXY': 'DX-Y.NYB',
}


def fetch_quotes(symbols_dict, category=''):
    """
    Generic fetcher for any yfinance symbols dict
    Returns price + % change for each symbol
    """
    results = {}

    for name, ticker in symbols_dict.items():
        try:
            print(f'[Yahoo] Fetching {name} ({ticker})...')
            t = yf.Ticker(ticker)
            hist = t.history(period='2d')

            if hist.empty or len(hist) < 1:
                print(f'[Yahoo] WARNING - No data for {name}')
                results[name] = {'price': None, 'change_pct': None, 'error': 'no data'}
                continue

            current = hist['Close'].iloc[-1]

            # Calculate % change - use previous close if available
            if len(hist) >= 2:
                prev = hist['Close'].iloc[-2]
                change_pct = round(((current - prev) / prev) * 100, 2)
            else:
                change_pct = 0.0

            results[name] = {
                'price': round(float(current), 4),
                'change_pct': change_pct,
            }

            direction = '+' if change_pct >= 0 else ''
            print(f'[Yahoo] {name}: {current:.2f} ({direction}{change_pct}%)')

        except Exception as e:
            print(f'[Yahoo] ERROR for {name}: {e}')
            results[name] = {'price': None, 'change_pct': None, 'error': str(e)}

    return results


def get_indices():
    """
    Fetch all global indices - US, Asia, Europe
    """
    print('[Yahoo] --- US Indices ---')
    us = fetch_quotes(US_INDICES)

    print('[Yahoo] --- Asia Indices ---')
    asia = fetch_quotes(ASIA_INDICES)

    print('[Yahoo] --- Europe Indices ---')
    europe = fetch_quotes(EUROPE_INDICES)

    return {
        'status': 'ok',
        'data': {
            'us': us,
            'asia': asia,
            'europe': europe,
        },
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


def get_commodities():
    """
    Fetch commodity prices - Gold, Silver, Oil, Copper, Gas
    """
    print('[Yahoo] --- Commodities ---')
    data = fetch_quotes(COMMODITIES)

    return {
        'status': 'ok',
        'data': data,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


def get_fx():
    """
    Fetch FX crosses + DXY
    """
    print('[Yahoo] --- FX ---')
    data = fetch_quotes(FX_PAIRS)

    return {
        'status': 'ok',
        'data': data,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


# Quick test
if __name__ == '__main__':
    print('Testing Yahoo fetcher...')
    print()

    print('--- INDICES ---')
    indices = get_indices()
    print(f'Status: {indices["status"]}')
    print()

    print('--- COMMODITIES ---')
    commodities = get_commodities()
    print(f'Status: {commodities["status"]}')
    print()

    print('--- FX ---')
    fx = get_fx()
    print(f'Status: {fx["status"]}')
    print()

    print('All done.')