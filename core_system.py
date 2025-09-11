import requests
from threading import Lock
import time
import random
from typing import Optional
from get_access_token import GetAccessToken

class CoreSystem:
    _last_request_time = 0
    _request_lock = Lock()
    _min_request_interval = 0.01
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id :str = client_id
        self.client_secret :str = client_secret
        self.access_token :Optional[str] = None
        self.token_manager = GetAccessToken(client_id, client_secret)

        self.base_url :str = "https://api.helpscout.net/v2"

    def _rate_limit(self):
        with CoreSystem._request_lock:
            current_time = time.time()
            time_since_last = current_time - CoreSystem._last_request_time
            
            if time_since_last < CoreSystem._min_request_interval:
                sleep_time = CoreSystem._min_request_interval - time_since_last
                time.sleep(sleep_time)
            
            CoreSystem._last_request_time = time.time()

    def make_request(self, endpoint: str, params: Optional[dict] = None, max_retries: int = 3) -> Optional[dict]:
        if not self.token_manager.ensure_valid_token():
            print("ERROR: Failed to get valid token")
            return None
        
        self.access_token = self.token_manager.access_token
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(max_retries + 1):
            self._rate_limit()
            
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    wait_time = 0.6 + (attempt * 0.2) + random.uniform(0, 0.3)
                    print(f"Rate limited, waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                    continue
                elif response.status_code in [500, 502, 503, 504]:
                    if attempt < max_retries:
                        wait_time = 0.6 + (attempt * 0.2) + random.uniform(0, 0.3)
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
                    wait_time = 0.6 + (attempt * 0.2) + random.uniform(0, 0.3)
                    print(f"Request failed: {e}, retrying in {wait_time:.1f}s")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Request failed after {max_retries} retries: {e}")
                    return None
        return None