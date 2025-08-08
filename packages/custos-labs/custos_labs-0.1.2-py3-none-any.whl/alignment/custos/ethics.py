# custos/ethics.py

class EthicsRegistry:
    def __init__(self):
        self.ethical_values = {
            "do_no_harm": True,
            "respect_autonomy": True,
            "fairness": True,
            "transparency": True,
            "privacy": True,
            "human_control": True,
            "authenticity": True,
        }

    def get_ethics(self):
        return self.ethical_values
