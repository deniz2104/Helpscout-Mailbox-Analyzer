import requests
from typing import Optional
from get_access_token import GetAccessToken

class CoreSystem:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id :str = client_id
        self.client_secret :str = client_secret
        self.access_token :Optional[str] = None
        self.token_manager = GetAccessToken(client_id, client_secret)

        self.base_url :str = "https://api.helpscout.net/v2"

    def make_request(self, endpoint: str, params: Optional[dict] = None) -> Optional[dict]:
        if not self.token_manager.ensure_valid_token():
            print("ERROR: Failed to get valid token")
            return None
        
        self.access_token = self.token_manager.access_token
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return None