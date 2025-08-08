### custos/config.py

import requests

class CustosConfig:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.valid = self.validate_key()

    def validate_key(self) -> bool:
        # In production, point this to your real Django endpoint
        try:
            response = requests.get(
                "http://localhost:8000/api/token/validate/",
                headers={"Authorization": f"Token {self.api_key}"},
                timeout=3,
            )
            return response.status_code == 200
        except Exception:
            return False
