# custos/context.py


class CustosSession:
    def _init_(self, api_key):
        from custos.guardian import CustosGuardian
        self.guardian = CustosGuardian(api_key=api_key)

    def _enter_(self):
        return self.guardian

    def _exit_(self, exc_type, exc_val, exc_tb):
        # Export simulation run if needed
        if self.guardian.simulator:
            print("Exporting Simulator Log:")
            print(self.guardian.simulator.export())