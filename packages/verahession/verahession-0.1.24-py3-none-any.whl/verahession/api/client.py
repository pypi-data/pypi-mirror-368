# verapylib/api/client.py

import requests

class vera_interface:
    def __init__(self, API_KEY, AGENT_NAME, USER_NAME="User"):
        self.API_CHAT_URL = "https://hessiondynamics.com/chat"
        self.api_key = API_KEY
        self.agent_name = AGENT_NAME
        self.user_name = USER_NAME

    def send(self, text: str):
        payload = {
            "text": text,
            "API": self.api_key,
            "agent_name": self.agent_name,
            "user_name": self.user_name
        }

        try:
            response = requests.post(self.API_CHAT_URL, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def rewrite(self, text: str):
        rewrite_url = "https://hessiondynamics.com/rewrite"
        payload = {
            "text": text,
            "API": self.api_key
        }
        try:
            response = requests.post(rewrite_url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
