import requests
from typing import Optional

class LLMClient:
    def __init__(self, config):
        self.config = config

    def generate(self, prompt: str) -> Optional[str]:
        if self.config.provider == "gemini":
            return self._call_gemini(prompt)
        else:
            raise NotImplementedError(f"Provider {self.config.provider} is not supported.")

    def _call_gemini(self, prompt: str) -> Optional[str]:
        headers = {
            "Content-Type": "application/json",
            # "Authorization": f"Bearer {self.config.api_key}"
        }
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self.config.temperature,
                "maxOutputTokens": self.config.max_tokens
            }
        }
        url = f"{self.config.base_url}/v1beta/models/{self.config.model}:generateContent"
        url += f"?key={self.config.api_key}"
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=self.config.timeout)
            if response.status_code != 200:
                print(f"[LLM Error] {response.status_code} - {response.text}")
                return None
            response.raise_for_status()
            json_response = response.json()
            candidates = json_response.get("candidates", [])
            result = candidates[0]["content"]["parts"][0]["text"] if candidates else None
            return result
        except Exception as e:
            print(f"[LLM Error] {e}")
            return None
