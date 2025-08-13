import requests
import time


class SlackSessionManager:
    _instance = None
    _session = None
    _created_time = 0
    RENEWAL_INTERVAL = 300  # 5 minutes

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_session(self):
        current_time = time.time()
        if self._session is None or (current_time - self._created_time) > self.RENEWAL_INTERVAL:
            self._session = requests.Session()
            self._created_time = current_time
        return self._session