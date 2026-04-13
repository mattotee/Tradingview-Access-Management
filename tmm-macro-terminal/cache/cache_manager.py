import json
import os
from datetime import datetime, timezone

# ============================================================
# CACHE DIRECTORY
# All cache files stored as JSON in /cache/
# ============================================================

CACHE_DIR = os.path.join(os.path.dirname(__file__))

# TTL (time-to-live) in seconds per data type
# How long before we consider the cache stale and re-fetch
TTL = {
    'crypto':   60,       # 1 minute - prices move fast
    'indices':  300,      # 5 minutes - markets update regularly
    'commodities': 300,   # 5 minutes
    'fx':       300,      # 5 minutes
    'news':     300,      # 5 minutes
    'macro':    3600,     # 1 hour - FRED data updates slowly
    'calendar': 21600,    # 6 hours - events don't change often
    'sessions': 60,       # 1 minute - session open/close status
}


def get_cache_path(key):
    """
    Returns the full file path for a cache key
    eg: 'crypto' -> /cache/crypto.json
    """
    return os.path.join(CACHE_DIR, f'{key}.json')


def read_cache(key):
    """
    Read cached data for a given key
    Returns the data if fresh, or None if stale/missing
    Also returns stale data with a flag if API is down
    """
    path = get_cache_path(key)

    if not os.path.exists(path):
        print(f'[Cache] MISS - {key} (no file)')
        return None, False

    try:
        with open(path, 'r') as f:
            cached = json.load(f)

        cached_at = cached.get('cached_at')
        if not cached_at:
            return None, False

        # Calculate age of cache
        cached_time = datetime.fromisoformat(cached_at)
        now = datetime.now(timezone.utc)
        age_seconds = (now - cached_time).total_seconds()
        ttl = TTL.get(key, 300)

        if age_seconds < ttl:
            print(f'[Cache] HIT - {key} (age: {int(age_seconds)}s / ttl: {ttl}s)')
            return cached.get('data'), False
        else:
            print(f'[Cache] STALE - {key} (age: {int(age_seconds)}s / ttl: {ttl}s)')
            # Return stale data with flag - better than nothing if API is down
            return cached.get('data'), True

    except Exception as e:
        print(f'[Cache] ERROR reading {key}: {e}')
        return None, False


def write_cache(key, data):
    """
    Write data to cache file with current timestamp
    """
    path = get_cache_path(key)

    try:
        cache_entry = {
            'cached_at': datetime.now(timezone.utc).isoformat(),
            'key': key,
            'data': data
        }

        with open(path, 'w') as f:
            json.dump(cache_entry, f, indent=2)

        print(f'[Cache] WRITE - {key}')
        return True

    except Exception as e:
        print(f'[Cache] ERROR writing {key}: {e}')
        return False


def invalidate_cache(key=None):
    """
    Delete cache file/s
    Pass a key to delete one, or None to delete all
    """
    if key:
        path = get_cache_path(key)
        if os.path.exists(path):
            os.remove(path)
            print(f'[Cache] INVALIDATED - {key}')
    else:
        # Nuke all cache files
        for filename in os.listdir(CACHE_DIR):
            if filename.endswith('.json'):
                os.remove(os.path.join(CACHE_DIR, filename))
        print(f'[Cache] INVALIDATED - all cache files cleared')


def get_or_fetch(key, fetch_fn):
    """
    Main helper - tries cache first, falls back to live fetch
    If live fetch fails, returns stale cache with stale flag
    This is the function all API routes will use
    """
    # Try fresh cache first
    data, is_stale = read_cache(key)

    if data is not None and not is_stale:
        return {'data': data, 'stale': False, 'source': 'cache'}

    # Cache miss or stale - fetch fresh data
    print(f'[Cache] Fetching fresh data for {key}...')
    try:
        result = fetch_fn()

        if result.get('status') == 'ok':
            write_cache(key, result.get('data'))
            return {'data': result.get('data'), 'stale': False, 'source': 'live'}
        else:
            # Fetch failed - return stale cache if we have it
            if data is not None:
                print(f'[Cache] Fetch failed for {key} - returning stale data')
                return {'data': data, 'stale': True, 'source': 'stale_cache'}
            return {'data': None, 'stale': True, 'source': 'error'}

    except Exception as e:
        print(f'[Cache] Exception fetching {key}: {e}')
        if data is not None:
            return {'data': data, 'stale': True, 'source': 'stale_cache'}
        return {'data': None, 'stale': True, 'source': 'error'}


# Quick test
if __name__ == '__main__':
    print('Testing cache manager...')
    print()

    # Test write
    print('--- WRITE TEST ---')
    test_data = {'price': 70000, 'symbol': 'BTC'}
    write_cache('test', test_data)

    # Test read (should be fresh)
    print('--- READ TEST ---')
    data, stale = read_cache('test')
    print(f'Data: {data}')
    print(f'Stale: {stale}')

    # Test invalidate
    print('--- INVALIDATE TEST ---')
    invalidate_cache('test')
    data, stale = read_cache('test')
    print(f'After invalidate - Data: {data}')

    print()
    print('All done.')