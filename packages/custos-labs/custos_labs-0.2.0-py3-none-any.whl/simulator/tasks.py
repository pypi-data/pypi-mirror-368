# simulator/tasks.py


from celery import shared_task
from .models import SimulationRun

@shared_task
def monitor_alignment(sim_id):
    sim = SimulationRun.objects.get(id=sim_id)
    # Placeholder for future auto-monitor logic
    print(f"Monitor running for Simulation {sim_id}: status={sim.status}")
