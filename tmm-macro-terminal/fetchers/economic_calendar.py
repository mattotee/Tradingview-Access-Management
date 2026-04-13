from datetime import datetime, timezone, timedelta


# ============================================================
# US-FOCUSED ECONOMIC CALENDAR 2026
# Events that move crypto + risk assets
# NFP, CPI, FOMC, PPI, GDP, PCE, ISM, Retail Sales
# ============================================================

CALENDAR_2026 = [

    # ---- APRIL ----
    {'date': '2026-04-14', 'time_utc': '01:30', 'event': 'AU Employment Change', 'country': 'AU', 'impact': 'medium'},
    {'date': '2026-04-16', 'time_utc': '12:30', 'event': 'US Retail Sales MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-04-16', 'time_utc': '13:15', 'event': 'US Industrial Production', 'country': 'US', 'impact': 'medium'},
    {'date': '2026-04-17', 'time_utc': '12:30', 'event': 'US Initial Jobless Claims', 'country': 'US', 'impact': 'medium'},
    {'date': '2026-04-17', 'time_utc': '14:00', 'event': 'US Philadelphia Fed Index', 'country': 'US', 'impact': 'medium'},
    {'date': '2026-04-23', 'time_utc': '13:45', 'event': 'US S&P Global PMI Flash', 'country': 'US', 'impact': 'medium'},
    {'date': '2026-04-24', 'time_utc': '12:30', 'event': 'US GDP Growth Rate QoQ Flash', 'country': 'US', 'impact': 'high'},
    {'date': '2026-04-24', 'time_utc': '12:30', 'event': 'US Core PCE Price Index QoQ', 'country': 'US', 'impact': 'high'},
    {'date': '2026-04-24', 'time_utc': '12:30', 'event': 'US Initial Jobless Claims', 'country': 'US', 'impact': 'medium'},
    {'date': '2026-04-30', 'time_utc': '12:30', 'event': 'US Core PCE Price Index MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-04-30', 'time_utc': '14:00', 'event': 'US Consumer Confidence', 'country': 'US', 'impact': 'medium'},

    # ---- MAY ----
    {'date': '2026-05-01', 'time_utc': '14:00', 'event': 'US ISM Manufacturing PMI', 'country': 'US', 'impact': 'high'},
    {'date': '2026-05-02', 'time_utc': '12:30', 'event': 'US Non-Farm Payrolls', 'country': 'US', 'impact': 'high'},
    {'date': '2026-05-02', 'time_utc': '12:30', 'event': 'US Unemployment Rate', 'country': 'US', 'impact': 'high'},
    {'date': '2026-05-07', 'time_utc': '18:00', 'event': 'FOMC Rate Decision', 'country': 'US', 'impact': 'high'},
    {'date': '2026-05-07', 'time_utc': '18:30', 'event': 'Fed Chair Powell Press Conference', 'country': 'US', 'impact': 'high'},
    {'date': '2026-05-13', 'time_utc': '12:30', 'event': 'US CPI Inflation MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-05-13', 'time_utc': '12:30', 'event': 'US Core CPI MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-05-14', 'time_utc': '12:30', 'event': 'US PPI Final Demand MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-05-15', 'time_utc': '12:30', 'event': 'US Retail Sales MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-05-15', 'time_utc': '12:30', 'event': 'US Initial Jobless Claims', 'country': 'US', 'impact': 'medium'},
    {'date': '2026-05-21', 'time_utc': '13:45', 'event': 'US S&P Global PMI Flash', 'country': 'US', 'impact': 'medium'},
    {'date': '2026-05-28', 'time_utc': '12:30', 'event': 'US GDP Growth Rate QoQ Second', 'country': 'US', 'impact': 'high'},
    {'date': '2026-05-29', 'time_utc': '12:30', 'event': 'US Core PCE Price Index MoM', 'country': 'US', 'impact': 'high'},

    # ---- JUNE ----
    {'date': '2026-06-01', 'time_utc': '14:00', 'event': 'US ISM Manufacturing PMI', 'country': 'US', 'impact': 'high'},
    {'date': '2026-06-05', 'time_utc': '12:30', 'event': 'US Non-Farm Payrolls', 'country': 'US', 'impact': 'high'},
    {'date': '2026-06-05', 'time_utc': '12:30', 'event': 'US Unemployment Rate', 'country': 'US', 'impact': 'high'},
    {'date': '2026-06-11', 'time_utc': '12:30', 'event': 'US CPI Inflation MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-06-11', 'time_utc': '12:30', 'event': 'US Core CPI MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-06-17', 'time_utc': '18:00', 'event': 'FOMC Rate Decision', 'country': 'US', 'impact': 'high'},
    {'date': '2026-06-17', 'time_utc': '18:30', 'event': 'Fed Chair Powell Press Conference', 'country': 'US', 'impact': 'high'},
    {'date': '2026-06-25', 'time_utc': '12:30', 'event': 'US GDP Growth Rate QoQ Third', 'country': 'US', 'impact': 'high'},
    {'date': '2026-06-26', 'time_utc': '12:30', 'event': 'US Core PCE Price Index MoM', 'country': 'US', 'impact': 'high'},

    # ---- JULY ----
    {'date': '2026-07-01', 'time_utc': '14:00', 'event': 'US ISM Manufacturing PMI', 'country': 'US', 'impact': 'high'},
    {'date': '2026-07-02', 'time_utc': '12:30', 'event': 'US Non-Farm Payrolls', 'country': 'US', 'impact': 'high'},
    {'date': '2026-07-02', 'time_utc': '12:30', 'event': 'US Unemployment Rate', 'country': 'US', 'impact': 'high'},
    {'date': '2026-07-09', 'time_utc': '12:30', 'event': 'US CPI Inflation MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-07-09', 'time_utc': '12:30', 'event': 'US Core CPI MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-07-29', 'time_utc': '18:00', 'event': 'FOMC Rate Decision', 'country': 'US', 'impact': 'high'},
    {'date': '2026-07-29', 'time_utc': '18:30', 'event': 'Fed Chair Powell Press Conference', 'country': 'US', 'impact': 'high'},
    {'date': '2026-07-30', 'time_utc': '12:30', 'event': 'US GDP Growth Rate QoQ Advance', 'country': 'US', 'impact': 'high'},
    {'date': '2026-07-31', 'time_utc': '12:30', 'event': 'US Core PCE Price Index MoM', 'country': 'US', 'impact': 'high'},

    # ---- AUGUST ----
    {'date': '2026-08-03', 'time_utc': '14:00', 'event': 'US ISM Manufacturing PMI', 'country': 'US', 'impact': 'high'},
    {'date': '2026-08-07', 'time_utc': '12:30', 'event': 'US Non-Farm Payrolls', 'country': 'US', 'impact': 'high'},
    {'date': '2026-08-07', 'time_utc': '12:30', 'event': 'US Unemployment Rate', 'country': 'US', 'impact': 'high'},
    {'date': '2026-08-13', 'time_utc': '12:30', 'event': 'US CPI Inflation MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-08-13', 'time_utc': '12:30', 'event': 'US Core CPI MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-08-14', 'time_utc': '12:30', 'event': 'US PPI Final Demand MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-08-28', 'time_utc': '12:30', 'event': 'US Core PCE Price Index MoM', 'country': 'US', 'impact': 'high'},

    # ---- SEPTEMBER ----
    {'date': '2026-09-01', 'time_utc': '14:00', 'event': 'US ISM Manufacturing PMI', 'country': 'US', 'impact': 'high'},
    {'date': '2026-09-04', 'time_utc': '12:30', 'event': 'US Non-Farm Payrolls', 'country': 'US', 'impact': 'high'},
    {'date': '2026-09-04', 'time_utc': '12:30', 'event': 'US Unemployment Rate', 'country': 'US', 'impact': 'high'},
    {'date': '2026-09-10', 'time_utc': '12:30', 'event': 'US CPI Inflation MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-09-10', 'time_utc': '12:30', 'event': 'US Core CPI MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-09-16', 'time_utc': '18:00', 'event': 'FOMC Rate Decision', 'country': 'US', 'impact': 'high'},
    {'date': '2026-09-16', 'time_utc': '18:30', 'event': 'Fed Chair Powell Press Conference', 'country': 'US', 'impact': 'high'},
    {'date': '2026-09-25', 'time_utc': '12:30', 'event': 'US GDP Growth Rate QoQ Third', 'country': 'US', 'impact': 'high'},
    {'date': '2026-09-26', 'time_utc': '12:30', 'event': 'US Core PCE Price Index MoM', 'country': 'US', 'impact': 'high'},

    # ---- OCTOBER ----
    {'date': '2026-10-01', 'time_utc': '14:00', 'event': 'US ISM Manufacturing PMI', 'country': 'US', 'impact': 'high'},
    {'date': '2026-10-02', 'time_utc': '12:30', 'event': 'US Non-Farm Payrolls', 'country': 'US', 'impact': 'high'},
    {'date': '2026-10-02', 'time_utc': '12:30', 'event': 'US Unemployment Rate', 'country': 'US', 'impact': 'high'},
    {'date': '2026-10-08', 'time_utc': '12:30', 'event': 'US CPI Inflation MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-10-08', 'time_utc': '12:30', 'event': 'US Core CPI MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-10-28', 'time_utc': '18:00', 'event': 'FOMC Rate Decision', 'country': 'US', 'impact': 'high'},
    {'date': '2026-10-28', 'time_utc': '18:30', 'event': 'Fed Chair Powell Press Conference', 'country': 'US', 'impact': 'high'},
    {'date': '2026-10-29', 'time_utc': '12:30', 'event': 'US GDP Growth Rate QoQ Advance', 'country': 'US', 'impact': 'high'},
    {'date': '2026-10-30', 'time_utc': '12:30', 'event': 'US Core PCE Price Index MoM', 'country': 'US', 'impact': 'high'},

    # ---- NOVEMBER ----
    {'date': '2026-11-02', 'time_utc': '14:00', 'event': 'US ISM Manufacturing PMI', 'country': 'US', 'impact': 'high'},
    {'date': '2026-11-06', 'time_utc': '12:30', 'event': 'US Non-Farm Payrolls', 'country': 'US', 'impact': 'high'},
    {'date': '2026-11-06', 'time_utc': '12:30', 'event': 'US Unemployment Rate', 'country': 'US', 'impact': 'high'},
    {'date': '2026-11-12', 'time_utc': '12:30', 'event': 'US CPI Inflation MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-11-12', 'time_utc': '12:30', 'event': 'US Core CPI MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-11-13', 'time_utc': '12:30', 'event': 'US PPI Final Demand MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-11-25', 'time_utc': '12:30', 'event': 'US Core PCE Price Index MoM', 'country': 'US', 'impact': 'high'},

    # ---- DECEMBER ----
    {'date': '2026-12-01', 'time_utc': '14:00', 'event': 'US ISM Manufacturing PMI', 'country': 'US', 'impact': 'high'},
    {'date': '2026-12-04', 'time_utc': '12:30', 'event': 'US Non-Farm Payrolls', 'country': 'US', 'impact': 'high'},
    {'date': '2026-12-04', 'time_utc': '12:30', 'event': 'US Unemployment Rate', 'country': 'US', 'impact': 'high'},
    {'date': '2026-12-09', 'time_utc': '12:30', 'event': 'US CPI Inflation MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-12-09', 'time_utc': '12:30', 'event': 'US Core CPI MoM', 'country': 'US', 'impact': 'high'},
    {'date': '2026-12-09', 'time_utc': '19:00', 'event': 'FOMC Rate Decision', 'country': 'US', 'impact': 'high'},
    {'date': '2026-12-09', 'time_utc': '19:30', 'event': 'Fed Chair Powell Press Conference', 'country': 'US', 'impact': 'high'},
    {'date': '2026-12-18', 'time_utc': '12:30', 'event': 'US GDP Growth Rate QoQ Third', 'country': 'US', 'impact': 'high'},
    {'date': '2026-12-23', 'time_utc': '12:30', 'event': 'US Core PCE Price Index MoM', 'country': 'US', 'impact': 'high'},
]


def get_calendar(days_ahead=7):
    """
    Return upcoming economic events for the next N days
    Times converted to AWST for display
    """
    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc + timedelta(days=days_ahead)
    upcoming = []

    for event in CALENDAR_2026:
        event_dt_str = f'{event["date"]} {event["time_utc"]}'
        event_dt_utc = datetime.strptime(event_dt_str, '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc)

        if now_utc <= event_dt_utc <= cutoff:
            event_dt_awst = event_dt_utc + timedelta(hours=8)
            delta = event_dt_utc - now_utc
            hours_away = int(delta.total_seconds() // 3600)
            minutes_away = int((delta.total_seconds() % 3600) // 60)

            upcoming.append({
                'event': event['event'],
                'country': event['country'],
                'impact': event['impact'],
                'date_utc': event['date'],
                'time_utc': event['time_utc'],
                'time_awst': event_dt_awst.strftime('%H:%M'),
                'date_awst': event_dt_awst.strftime('%d %b'),
                'hours_away': hours_away,
                'minutes_away': minutes_away,
                'countdown': f'{hours_away}h {minutes_away}m' if hours_away < 48 else f'{int(hours_away/24)}d',
            })

    upcoming.sort(key=lambda x: x['date_utc'] + ' ' + x['time_utc'])
    print(f'[Calendar] Found {len(upcoming)} events in next {days_ahead} days')
    return {
        'status': 'ok',
        'data': upcoming,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


def get_next_high_impact():
    """
    Find the next high impact event within 24 hours for the alert banner
    """
    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc + timedelta(hours=24)

    for event in CALENDAR_2026:
        event_dt_str = f'{event["date"]} {event["time_utc"]}'
        event_dt_utc = datetime.strptime(event_dt_str, '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc)

        if event['impact'] == 'high' and now_utc <= event_dt_utc <= cutoff:
            event_dt_awst = event_dt_utc + timedelta(hours=8)
            delta = event_dt_utc - now_utc
            hours_away = int(delta.total_seconds() // 3600)
            minutes_away = int((delta.total_seconds() % 3600) // 60)
            return {
                'found': True,
                'event': event['event'],
                'country': event['country'],
                'time_awst': event_dt_awst.strftime('%H:%M AWST'),
                'countdown': f'{hours_away}h {minutes_away}m',
            }

    return {'found': False}


# Quick test
if __name__ == '__main__':
    print('Testing calendar...')
    cal = get_calendar(30)
    print(f'Status: {cal["status"]}')
    for e in cal['data'][:10]:
        print(f'  [{e["impact"].upper()}] {e["date_awst"]} {e["time_awst"]} AWST - {e["event"]} - in {e["countdown"]}')