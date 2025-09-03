import requests

class GetAccessToken():
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.base_url = "https://api.helpscout.net/v2"

    def get_access_token(self):
        token_url = f"{self.base_url}/oauth2/token"

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        response = requests.post(token_url, data=data)

        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            return True
        else:
            print(f"Failed to get token: {response.status_code} - {response.text}")
            return False

    def ensure_valid_token(self):
        if not self.access_token:
            return self.get_access_token()
        return True
