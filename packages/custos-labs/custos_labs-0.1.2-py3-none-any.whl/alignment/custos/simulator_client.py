# custos/simulator_client.py


import requests
import os

SIMULATOR_API = os.getenv("CUSTOS_SIMULATOR_URL", "https://custoslabs-backend.onrender.com/simulator/")

class SimulatorClient:
    def _init_(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json"
        })
        self.run_id = None

    def ensure_run(self):
        if self.run_id is not None:
            return self.run_id
        resp = self.session.post(SIMULATOR_API + "runs/")
        resp.raise_for_status()
        self.run_id = resp.json()["run_id"]
        return self.run_id

    def log_response(self, prompt, response, score, color, flatline, violations, confidence=1.0):
        run_id = self.ensure_run()
        data = {
            "run_id": run_id,
            "prompt": prompt,
            "response": response,
            "alignment_score": score,
            "color": color,
            "flatline": flatline,
            "violations": violations,
            "confidence": confidence,
        }
        try:
            resp = self.session.post(SIMULATOR_API + "logs/", json=data, timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"[Custos SDK] Simulator log failed: {e}")
            return None

    def export(self):
        run_id = self.ensure_run()
        resp = self.session.get(SIMULATOR_API + f"export/{run_id}/")
        resp.raise_for_status()
        return resp.json()