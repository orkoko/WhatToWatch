import time

class TimeBasedCache:
    def __init__(self, expiration_seconds):
        self.expiration_seconds = expiration_seconds
        self.cache = {}
        self.timestamps = {}

    def get(self, key):
        if key in self.cache:
            if time.time() - self.timestamps[key] < self.expiration_seconds:
                return self.cache[key]
            else:
                del self.cache[key]
                del self.timestamps[key]
        return None

    def set(self, key, value):
        self.cache[key] = value
        self.timestamps[key] = time.time()
