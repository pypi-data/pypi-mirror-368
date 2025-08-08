# simulator/views.py


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import SimulationRun, SimulatorLog
from .serializers import SimulationRunSerializer, SimulatorLogSerializer
from custos.guardian import CustosGuardian
from django.utils.timezone import now
from django.db.models import Avg
from .permissions import IsSimulationOwner
from api.models import APIKey


class CreateSimulationRun(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        api_key_id = request.data.get("api_key_id")
        api_key = None
        if api_key_id:
            try:
                api_key = APIKey.objects.get(id=api_key_id, user=request.user)
            except APIKey.DoesNotExist:
                return Response({"error": "Invalid API key selected."}, status=400)

        run = SimulationRun.objects.create(user=request.user, api_key=api_key)
        return Response({
            "run_id": run.id,
            "alignment_score": 100,
            "status": run.status,
            "started_at": run.started_at,
            "ended_at": run.ended_at,
            "api_key_prefix": api_key.prefix if api_key else None,
        }, status=201)

class LogAIResponse(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        run_id = request.data.get("run_id")
        response_text = request.data.get("response", "")
        prompt = request.data.get("prompt", "") 
        confidence = request.data.get("confidence", 1.0)  

        api_key = request.auth.key if hasattr(request.auth, 'key') else None
        if not run_id or not response_text:
            return Response({"error": "run_id and response are required"}, status=400)
        try:
            run = SimulationRun.objects.get(id=run_id, user=request.user)
        except SimulationRun.DoesNotExist:
            return Response({"error": "Simulation run not found"}, status=404)

        guardian = CustosGuardian(api_key=api_key or "dummy")

        try:
            result = guardian.evaluate(prompt, response_text)
            score = 100
            color = "green"
            violations = []
            flatline = False
        except Exception as e:
            score = max(run.alignment_score - 50, 0)
            color = "red"
            violations = getattr(e, "result", {}).get("violations", ["misalignment"])
            flatline = True
            run.status = "misaligned"
            run.ended_at = now()
            run.alignment_score = score
            run.save()

        log = SimulatorLog.objects.create(
            run=run,
            response=response_text,
            prompt=prompt,
            alignment_score=score,
            color=color,
            flatline=flatline,
            violations=violations,
            confidence=confidence,
        )

        # Update running average if not misaligned
        if not flatline:
            avg = SimulatorLog.objects.filter(run=run).aggregate(
                Avg('alignment_score')
            )["alignment_score__avg"] or 100
            run.alignment_score = avg
            if score < 70:
                run.status = "warning"
            run.save()

        return Response({
            "log_id": log.id,
            "timestamp": log.timestamp,
            "alignment_score": score,
            "color": color,
            "flatline": flatline,
            "violations": violations,
            "run_status": run.status,
            "confidence": confidence,
            "ended_at": run.ended_at,
        }, status=201)

class GetRhythmLog(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, run_id):
        try:
            run = SimulationRun.objects.get(id=run_id, user=request.user)
        except SimulationRun.DoesNotExist:
            return Response({"error": "Simulation run not found"}, status=404)

        logs = SimulatorLog.objects.filter(run=run).order_by('timestamp')
        data = [
            {
                "timestamp": log.timestamp,
                "alignment_score": log.alignment_score,
                "color": log.color,
                "flatline": log.flatline,
                "violations": log.violations,
                "confidence": log.confidence,
                "prompt": log.prompt,
                "response": log.response,
            }
            for log in logs
        ]
        return Response({
            "run_id": run.id,
            "status": run.status,
            "alignment_score": run.alignment_score,
            "heartbeat": data,
            "ended_at": run.ended_at,
        })

class ExportRhythmLog(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, run_id):
        try:
            run = SimulationRun.objects.get(id=run_id, user=request.user)
        except SimulationRun.DoesNotExist:
            return Response({"error": "Simulation run not found"}, status=404)

        logs = SimulatorLog.objects.filter(run=run).order_by('timestamp')
        export = []
        for log in logs:
            export.append({
                "timestamp": str(log.timestamp),
                "alignment_score": log.alignment_score,
                "color": log.color,
                "flatline": log.flatline,
                "violations": log.violations,
                "prompt": log.prompt,
                "response": log.response,
                "confidence": log.confidence,
            })
        return Response(export)
