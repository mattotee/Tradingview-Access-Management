import requests
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

FINNHUB_KEY = os.getenv('FINNHUB_KEY')
BASE_URL = 'https://finnhub.io/api/v1'


def get_news(category='general', limit=20):
    """
    Fetch financial news from Finnhub
    Categories: general, crypto, forex, merger
    Timestamps converted to AWST (UTC+8)
    """
    try:
        print(f'[Finnhub] Fetching {category} news...')
        url = f'{BASE_URL}/news'
        params = {
            'category': category,
            'token': FINNHUB_KEY
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data:
            return {'status': 'error', 'error': 'no data', 'data': []}

        # Format and clean up each news item
        news_items = []
        seen_headlines = set()

        for item in data[:limit]:
            headline = item.get('headline', '').strip()

            # Skip duplicates
            if headline in seen_headlines:
                continue
            seen_headlines.add(headline)

            # Convert Unix timestamp to AWST
            ts = item.get('datetime', 0)
            utc_time = datetime.fromtimestamp(ts, tz=timezone.utc)
            awst_time = utc_time + timedelta(hours=8)

            news_items.append({
                'headline': headline,
                'source': item.get('source', 'Unknown'),
                'url': item.get('url', ''),
                'time_awst': awst_time.strftime('%H:%M'),
                'date_awst': awst_time.strftime('%d %b'),
                'category': category,
                'summary': item.get('summary', '')[:200] if item.get('summary') else '',
            })

        print(f'[Finnhub] Got {len(news_items)} {category} news items')
        return {
            'status': 'ok',
            'data': news_items,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    except requests.exceptions.RequestException as e:
        print(f'[Finnhub] ERROR - {e}')
        return {'status': 'error', 'error': str(e), 'data': []}


def get_all_news():
    """
    Fetch and merge general + crypto news into a single feed
    Sorted by time, deduplicated
    """
    general = get_news('general', 20)
    crypto = get_news('crypto', 20)

    all_items = []

    if general['status'] == 'ok':
        for item in general['data']:
            item['category'] = 'macro'
            all_items.append(item)

    if crypto['status'] == 'ok':
        for item in crypto['data']:
            item['category'] = 'crypto'
            all_items.append(item)

    # Deduplicate by headline across categories
    seen = set()
    unique_items = []
    for item in all_items:
        if item['headline'] not in seen:
            seen.add(item['headline'])
            unique_items.append(item)

    print(f'[Finnhub] Combined feed: {len(unique_items)} unique items')

    return {
        'status': 'ok',
        'data': unique_items,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


def get_session_status():
    """
    Calculate which trading sessions are currently open
    Based on current UTC time - accounts for standard hours
    Note: does not account for DST changes - update offsets seasonally
    """
    now_utc = datetime.now(timezone.utc)
    current_hour = now_utc.hour
    current_minute = now_utc.minute
    current_time = current_hour * 60 + current_minute  # minutes since midnight UTC
    day_of_week = now_utc.weekday()  # 0=Monday, 6=Sunday

    # Weekend check - all markets closed
    is_weekend = day_of_week >= 5

    def is_open(open_utc_minutes, close_utc_minutes):
        if is_weekend:
            return False
        return open_utc_minutes <= current_time < close_utc_minutes

    # Session hours in UTC minutes
    # Tokyo: 9am-3pm JST = 1am-7am UTC (60-420)
    tokyo_open = is_open(60, 420)

    # Sydney: 10am-4pm AEDT = midnight-6am UTC (0-360)
    sydney_open = is_open(0, 360)

    # London: 8am-4:30pm GMT = 8am-4:30pm UTC (480-990)
    london_open = is_open(480, 990)

    # New York: 9:30am-4pm EST = 2:30pm-9pm UTC (870-1260)
    ny_open = is_open(870, 1260)

    sessions = {
        'tokyo': {
            'open': tokyo_open,
            'label': 'ASIA / TOKYO',
            'status': 'OPEN' if tokyo_open else 'CLOSED',
            'hours_utc': '01:00 - 07:00 UTC',
        },
        'sydney': {
            'open': sydney_open,
            'label': 'SYDNEY',
            'status': 'OPEN' if sydney_open else 'CLOSED',
            'hours_utc': '00:00 - 06:00 UTC',
        },
        'london': {
            'open': london_open,
            'label': 'LONDON',
            'status': 'OPEN' if london_open else 'CLOSED',
            'hours_utc': '08:00 - 16:30 UTC',
        },
        'new_york': {
            'open': ny_open,
            'label': 'NEW YORK',
            'status': 'OPEN' if ny_open else 'CLOSED',
            'hours_utc': '14:30 - 21:00 UTC',
        },
    }

    open_sessions = [s['label'] for s in sessions.values() if s['open']]
    print(f'[Sessions] Current UTC: {now_utc.strftime("%H:%M")} | Open: {open_sessions if open_sessions else ["None - weekend or off hours"]}')

    return {
        'status': 'ok',
        'data': sessions,
        'current_utc': now_utc.strftime('%H:%M'),
        'is_weekend': is_weekend,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


# Quick test
if __name__ == '__main__':
    print('Testing Finnhub fetcher...')
    print()

    print('--- GENERAL NEWS ---')
    news = get_news('general', 5)
    print(f'Status: {news["status"]}')
    if news['status'] == 'ok':
        for item in news['data'][:3]:
            print(f'  [{item["time_awst"]} AWST] {item["source"]}: {item["headline"][:80]}...')
    print()

    print('--- CRYPTO NEWS ---')
    crypto = get_news('crypto', 5)
    print(f'Status: {crypto["status"]}')
    if crypto['status'] == 'ok':
        for item in crypto['data'][:3]:
            print(f'  [{item["time_awst"]} AWST] {item["source"]}: {item["headline"][:80]}...')
    print()

    print('--- SESSION STATUS ---')
    sessions = get_session_status()
    print(f'Status: {sessions["status"]}')
    for key, s in sessions['data'].items():
        print(f'  {s["label"]}: {s["status"]}')
    print()

    print('All done.')