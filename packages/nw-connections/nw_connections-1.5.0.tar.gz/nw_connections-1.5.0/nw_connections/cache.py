import json
from datetime import datetime, timedelta

class FileCache:
    def __init__(self, cache_file='cache.json'):
        self.cache_file = cache_file

    def get(self, key):
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
                if 'expires_at' in cache_data:
                    cache_data['expires_at'] = datetime.fromisoformat(cache_data['expires_at'])
                
                if 'expires_at' in cache_data and cache_data['expires_at'] < datetime.now():
                    return None
                return cache_data.get(key)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def set(self, key, value, timeout=None):
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            cache_data = {}
        
        cache_data[key] = value
        if timeout is not None:
            cache_data['expires_at'] = datetime.now() + timedelta(seconds=timeout)
        else:
            cache_data['expires_at'] = None
        
        # Serialize datetime objects to strings
        for k, v in cache_data.items():
            if isinstance(v, datetime):
                cache_data[k] = v.isoformat()
        
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f)