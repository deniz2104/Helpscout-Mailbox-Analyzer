import requests
from threading import Lock
import time
import random
from typing import Optional
from APIConnection.get_access_token import GetAccessToken


class CoreSystem:
    """
    Core system for making API requests with per-minute rate limiting and retries.
    """
    _request_lock = Lock()
    _session = requests.Session()
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.access_token: Optional[str] = None
        self.token_manager = GetAccessToken(client_id, client_secret)
        self.base_url: str = "https://api.helpscout.net/v2"

        self._minute_start = int(time.time() // 60) * 60
        self._limit = None
        self._remaining = None

    def _check_minute_window(self):
        now_minute = int(time.time() // 60) * 60
        if now_minute > self._minute_start:
            self._minute_start = now_minute
            self._limit = None
            self._remaining = None

    def make_request(self, endpoint: str, params: Optional[dict] = None, max_retries: int = 6) -> Optional[dict]:
        if not self.token_manager.ensure_valid_token():
            print("ERROR: Failed to get valid token")
            return None
        
        self.access_token = self.token_manager.access_token
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(max_retries + 1):
            with CoreSystem._request_lock:
                self._check_minute_window()

                if self._remaining is not None and self._remaining <= 0:
                    wait_time = (self._minute_start + 60) - time.time()
                    if wait_time > 0:
                        print(f"Rate limit reached, waiting {wait_time:.1f}s for next minute window...")
                        time.sleep(wait_time)
                        self._check_minute_window()

            try:
                response = CoreSystem._session.get(url, headers=headers, params=params, timeout=45)

                limit = response.headers.get("x-ratelimit-limit-minute")
                remaining = response.headers.get("x-ratelimit-remaining-minute")

                if limit and remaining:
                    self._limit = int(limit)
                    self._remaining = int(remaining)
                    print(f"Rate Limit: {self._remaining}/{self._limit} remaining this minute")

                if response.status_code == 200:
                    return response.json()
                
                elif response.status_code == 429:
                    wait_time = 1 + random.uniform(0.5, 1.0)
                    print(f"Rate limited, waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                    continue
                
                elif response.status_code in [500, 502, 503, 504]:
                    if attempt < max_retries:
                        wait_time = 1 + (attempt * 0.5) + random.uniform(0, 0.5)
                        print(f"Server error {response.status_code}, retrying in {wait_time:.1f}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"API Error after {max_retries} retries: {response.status_code} - {response.text}")
                        return None
                
                else:
                    print(f"API Error: {response.status_code} - {response.text}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    wait_time = 1 + (attempt * 0.5) + random.uniform(0, 0.5)
                    print(f"Request failed: {e}, retrying in {wait_time:.1f}s")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Request failed after {max_retries} retries: {e}")
                    return None  
        return None