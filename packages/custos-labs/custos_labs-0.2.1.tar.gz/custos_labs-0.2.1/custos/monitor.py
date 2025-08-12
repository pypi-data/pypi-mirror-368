### custos/monitor.py

class Monitor:
    def analyze(self, prompt: str, response: str) -> dict:
        return {
            "prompt_length": len(prompt),
            "response_length": len(response),
            "suspicious_keywords": [
                k for k in ["hack", "bomb", "attack"]
                if k in prompt.lower() or k in response.lower()
            ]
        }