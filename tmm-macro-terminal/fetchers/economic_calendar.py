import requests
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

FINNHUB_KEY = os.getenv('FINNHUB_KEY')
BASE_URL = 'https://finnhub.io/api/v1/calendar/economic'


def get_calendar(days_ahead=7):
    """
    Fetch economic calendar from Finnhub API
    Filters for US high and medium impact events
    Converts times to AWST (UTC+8)
    """
    try:
        now_utc = datetime.now(timezone.utc)
        start = now_utc.strftime('%Y-%m-%d')
        end = (now_utc + timedelta(days=days_ahead)).strftime('%Y-%m-%d')

        print(f'[Calendar] Fetching from Finnhub ({start} to {end})...')

        params = {
            'token': FINNHUB_KEY,
            'from': start,
            'to': end,
        }

        response = requests.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        events = data.get('economicCalendar', [])

        if not events:
            print(f'[Calendar] No events returned from Finnhub')
            return {'status': 'ok', 'data': [], 'timestamp': datetime.now(timezone.utc).isoformat()}

        # High impact keywords - things that move crypto and risk assets
        HIGH_IMPACT_KEYWORDS = [
            'Non-Farm', 'NFP', 'CPI', 'Federal Funds', 'FOMC', 'Fed Chair',
            'Powell', 'GDP', 'PCE', 'PPI', 'Unemployment Rate', 'Retail Sales',
            'ISM Manufacturing', 'ISM Services', 'Consumer Price',
            'Producer Price', 'Payroll', 'Interest Rate'
        ]

        MEDIUM_IMPACT_KEYWORDS = [
            'Jobless Claims', 'Consumer Confidence', 'Industrial Production',
            'Philadelphia Fed', 'PMI', 'Building Permits', 'Housing Starts',
            'Durable Goods', 'Trade Balance', 'Consumer Sentiment',
            'ADP Employment', 'Retail', 'Michigan'
        ]

        upcoming = []

        for event in events:
            # Only US events
            country = event.get('country', '')
            if country != 'US':
                continue

            event_name = event.get('event', '')
            impact = 'low'

            # Determine impact by keyword matching
            if any(kw.lower() in event_name.lower() for kw in HIGH_IMPACT_KEYWORDS):
                impact = 'high'
            elif any(kw.lower() in event_name.lower() for kw in MEDIUM_IMPACT_KEYWORDS):
                impact = 'medium'
            else:
                continue  # Skip low impact events

            # Parse datetime
            event_date = event.get('time', '')
            if not event_date:
                continue

            try:
                # Finnhub returns time as full datetime string
                event_dt_utc = datetime.strptime(event_date, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
            except Exception:
                try:
                    event_dt_utc = datetime.strptime(event_date[:10], '%Y-%m-%d').replace(tzinfo=timezone.utc)
                except Exception:
                    continue

            # Skip past events
            if event_dt_utc < now_utc:
                continue

            # Convert to AWST
            event_dt_awst = event_dt_utc + timedelta(hours=8)

            # Countdown
            delta = event_dt_utc - now_utc
            hours_away = int(delta.total_seconds() // 3600)
            minutes_away = int((delta.total_seconds() % 3600) // 60)
            countdown = f'{hours_away}h {minutes_away}m' if hours_away < 48 else f'{int(hours_away/24)}d'

            upcoming.append({
                'event': event_name,
                'country': 'US',
                'impact': impact,
                'date_utc': event_dt_utc.strftime('%Y-%m-%d'),
                'time_utc': event_dt_utc.strftime('%H:%M'),
                'time_awst': event_dt_awst.strftime('%H:%M'),
                'date_awst': event_dt_awst.strftime('%d %b'),
                'hours_away': hours_away,
                'minutes_away': minutes_away,
                'countdown': countdown,
                'actual': event.get('actual', ''),
                'forecast': event.get('estimate', ''),
                'previous': event.get('prev', ''),
            })

        # Sort by datetime
        upcoming.sort(key=lambda x: x['date_utc'] + ' ' + x['time_utc'])

        print(f'[Calendar] Found {len(upcoming)} US events in next {days_ahead} days')
        return {
            'status': 'ok',
            'data': upcoming,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        print(f'[Calendar] ERROR - {e}')
        return {'status': 'error', 'error': str(e), 'data': []}


def get_next_high_impact():
    """
    Find the next high impact event within 24 hours for the alert banner
    """
    try:
        result = get_calendar(days_ahead=2)
        if result['status'] != 'ok':
            return {'found': False}

        for event in result['data']:
            if event['impact'] == 'high':
                return {
                    'found': True,
                    'event': event['event'],
                    'country': 'US',
                    'time_awst': event['time_awst'] + ' AWST',
                    'countdown': event['countdown'],
                }

        return {'found': False}

    except Exception as e:
        print(f'[Calendar] get_next_high_impact ERROR - {e}')
        return {'found': False}


# Quick test
if __name__ == '__main__':
    print('Testing Finnhub calendar...')
    print()

    cal = get_calendar(7)
    print(f'Status: {cal["status"]}')
    print(f'Events found: {len(cal["data"])}')
    for e in cal['data'][:10]:
        print(f'  [{e["impact"].upper()}] {e["date_awst"]} {e["time_awst"]} AWST - {e["event"]} - in {e["countdown"]}')
    print()

    print('--- NEXT HIGH IMPACT ---')
    alert = get_next_high_impact()
    if alert['found']:
        print(f'  {alert["event"]} at {alert["time_awst"]} - in {alert["countdown"]}')
    else:
        print('  None in next 24 hours')