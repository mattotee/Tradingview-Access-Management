import requests
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

FRED_KEY = os.getenv('FRED_KEY')
BASE_URL = 'https://api.stlouisfed.org/fred/series/observations'

# 2026 FOMC meeting dates - hardcoded as they're published in advance
FOMC_DATES_2026 = [
    '2026-01-28',
    '2026-03-18',
    '2026-05-07',
    '2026-06-17',
    '2026-07-29',
    '2026-09-16',
    '2026-10-28',
    '2026-12-09',
]


def get_series(series_id, limit=2):
    """
    Fetch the latest observations for a FRED series
    Returns the most recent value/s
    """
    try:
        params = {
            'series_id': series_id,
            'api_key': FRED_KEY,
            'file_type': 'json',
            'sort_order': 'desc',
            'limit': limit
        }
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        observations = data.get('observations', [])
        return observations
    except Exception as e:
        print(f'[FRED] ERROR fetching {series_id}: {e}')
        return []


def get_next_fomc():
    """
    Calculate next FOMC meeting date and days away
    """
    today = datetime.now(timezone.utc).date()
    for date_str in FOMC_DATES_2026:
        meeting_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        if meeting_date >= today:
            days_away = (meeting_date - today).days
            return {
                'date': date_str,
                'date_formatted': meeting_date.strftime('%b %d, %Y'),
                'days_away': days_away
            }
    return {'date': None, 'date_formatted': 'TBC', 'days_away': None}


def get_macro():
    """
    Fetch all macro data from FRED
    Returns Fed rate, yields, CPI, M2, unemployment
    """
    try:
        print('[FRED] Fetching Fed Funds Rate...')
        fed_rate_obs = get_series('FEDFUNDS', 2)
        fed_rate = float(fed_rate_obs[0]['value']) if fed_rate_obs else None

        print('[FRED] Fetching 2Y Treasury yield...')
        yield_2y_obs = get_series('DGS2', 2)
        yield_2y = float(yield_2y_obs[0]['value']) if yield_2y_obs else None

        print('[FRED] Fetching 10Y Treasury yield...')
        yield_10y_obs = get_series('DGS10', 2)
        yield_10y = float(yield_10y_obs[0]['value']) if yield_10y_obs else None

        # Yield spread - negative = inverted curve = recession watch
        yield_spread = None
        if yield_2y is not None and yield_10y is not None:
            yield_spread = round(yield_10y - yield_2y, 2)

        print('[FRED] Fetching CPI...')
        cpi_obs = get_series('CPIAUCSL', 13)
        cpi_yoy = None
        if len(cpi_obs) >= 13:
            current_cpi = float(cpi_obs[0]['value'])
            year_ago_cpi = float(cpi_obs[12]['value'])
            cpi_yoy = round(((current_cpi - year_ago_cpi) / year_ago_cpi) * 100, 2)

        print('[FRED] Fetching M2 Money Supply...')
        m2_obs = get_series('M2SL', 2)
        m2 = float(m2_obs[0]['value']) if m2_obs else None

        print('[FRED] Fetching Unemployment Rate...')
        unemp_obs = get_series('UNRATE', 2)
        unemployment = float(unemp_obs[0]['value']) if unemp_obs else None

        print('[FRED] Calculating next FOMC date...')
        fomc = get_next_fomc()

        result = {
            'fed_rate': fed_rate,
            'yield_2y': yield_2y,
            'yield_10y': yield_10y,
            'yield_spread': yield_spread,
            'yield_inverted': yield_spread < 0 if yield_spread is not None else False,
            'cpi_yoy': cpi_yoy,
            'm2_billions': round(m2 * 1000, 0) if m2 else None,
            'unemployment': unemployment,
            'fomc': fomc,
        }

        print(f'[FRED] Fed Rate: {fed_rate}%')
        print(f'[FRED] 2Y Yield: {yield_2y}% | 10Y Yield: {yield_10y}%')
        print(f'[FRED] Yield Spread: {yield_spread}% ({"INVERTED" if result["yield_inverted"] else "normal"})')
        print(f'[FRED] CPI YoY: {cpi_yoy}%')
        print(f'[FRED] Unemployment: {unemployment}%')
        print(f'[FRED] Next FOMC: {fomc["date_formatted"]} ({fomc["days_away"]} days away)')

        return {
            'status': 'ok',
            'data': result,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        print(f'[FRED] ERROR - {e}')
        return {'status': 'error', 'error': str(e), 'data': {}}


# Quick test
if __name__ == '__main__':
    print('Testing FRED fetcher...')
    print()

    macro = get_macro()
    print(f'Status: {macro["status"]}')
    print()
    print('All done.')