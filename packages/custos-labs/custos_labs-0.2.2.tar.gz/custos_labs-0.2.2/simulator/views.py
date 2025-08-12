# simulator/views.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from api.apikey_auth import APIKeyAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from django.db.models import Avg
from django.core.cache import cache
import random

from .models import SimulationRun, SimulatorLog
from .serializers import SimulationRunSerializer
from custos.guardian import CustosGuardian
from api.models import APIKey

ACTIVE_RUN_TTL_SECONDS = 60 * 60 * 8  # 8 hours


class CreateSimulationRun(APIView):
    authentication_classes = [TokenAuthentication]
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
        if api_key:
            cache.set(f"active_run:{api_key.id}", run.id, timeout=ACTIVE_RUN_TTL_SECONDS)

        return Response({
            "run_id": run.id,
            "alignment_score": 100.0,
            "status": run.status,
            "started_at": run.started_at,
            "ended_at": run.ended_at,
            "api_key_prefix": api_key.prefix if api_key else None,
        }, status=201)


class ListSimulationRuns(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        runs = SimulationRun.objects.filter(user=request.user).order_by("-started_at")
        return Response(SimulationRunSerializer(runs, many=True).data)


class LogAIResponse(APIView):
    """
    POST /simulator/logs/
    Body:
      - kind: "response" | "heartbeat"   (default: "response")
      - prompt?: str
      - response?: str
      - confidence?: float
      - run_id?: int  (optional; with ApiKey auth we auto-select/create a run)
    Auth:
      - ApiKey <RAW>  (preferred; auto-start/attach to active run)
      - Token <USER_TOKEN> (allowed; requires run_id)
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [APIKeyAuthentication, TokenAuthentication]

    def _get_or_create_active_run(self, request):
        """Return cached active run for this API key, or create a new one."""
        auth_obj = getattr(request, "auth", None)
        if not isinstance(auth_obj, APIKey):
            return None

        # 1) cached active run?
        active_id = cache.get(f"active_run:{auth_obj.id}")
        if active_id:
            run = SimulationRun.objects.filter(id=active_id, user=request.user).first()
            if run and run.status in ("active", "warning"):
                return run

        # 2) latest open run?
        run = (SimulationRun.objects
               .filter(user=request.user, api_key=auth_obj, status__in=("active", "warning"))
               .order_by("-started_at")
               .first())
        if run:
            cache.set(f"active_run:{auth_obj.id}", run.id, timeout=ACTIVE_RUN_TTL_SECONDS)
            return run

        # 3) create fresh run
        run = SimulationRun.objects.create(user=request.user, api_key=auth_obj)
        cache.set(f"active_run:{auth_obj.id}", run.id, timeout=ACTIVE_RUN_TTL_SECONDS)
        return run

    def post(self, request):
        kind = (request.data.get("kind") or "response").lower()
        run_id = request.data.get("run_id")
        prompt = request.data.get("prompt", "")
        response_text = request.data.get("response", "")
        try:
            confidence = float(request.data.get("confidence", 1.0))
        except Exception:
            confidence = 1.0

        if kind == "response" and not response_text:
            return Response({"error": "response is required for kind=response"}, status=400)

        if run_id:
            run = SimulationRun.objects.filter(id=run_id, user=request.user).first()
            if not run:
                return Response({"error": "Simulation run not found"}, status=404)
        else:
            run = self._get_or_create_active_run(request)
            if not run:
                return Response({"error": "run_id required for this auth method"}, status=400)

        # API key context (optional)
        api_key_str = None
        if hasattr(request.auth, "key"):  # Token auth obj
            api_key_str = request.auth.key
        elif isinstance(request.auth, APIKey):
            api_key_str = f"{request.auth.prefix}..."

        # defaults
        score = run.alignment_score or 100.0
        color, violations, flatline = "green", [], False

        if kind == "response":
            guardian = CustosGuardian(api_key=api_key_str or "custos")
            try:
                guardian.evaluate(prompt, response_text)
                score = 100.0
            except Exception as e:
                score = max(run.alignment_score - 50.0, 0.0)
                color = "red"
                violations = getattr(e, "result", {}).get("violations", ["misalignment"])
                flatline = True
                run.status = "misaligned"
                run.ended_at = now()
                run.alignment_score = score
                run.save()
        else:
            # heartbeat: add tiny jitter to make HRV move
            jitter = random.uniform(-0.8, 0.8)
            score = max(0.0, min(100.0, (run.alignment_score or 100.0) + jitter))

        log = SimulatorLog.objects.create(
            run=run,
            response=response_text if kind == "response" else "",
            prompt=prompt if kind == "response" else "",
            alignment_score=score,
            color=color,
            flatline=flatline,
            violations=violations,
            confidence=confidence,
        )

        if not flatline:
            avg = SimulatorLog.objects.filter(run=run).aggregate(
                Avg('alignment_score')
            )["alignment_score__avg"] or 100.0
            run.alignment_score = avg
            if score < 70.0:
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
            "run_id": run.id,
        }, status=201)


class GetRhythmLog(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, run_id):
        run = SimulationRun.objects.filter(id=run_id, user=request.user).first()
        if not run:
            return Response({"error": "Simulation run not found"}, status=404)

        logs = SimulatorLog.objects.filter(run=run).order_by('timestamp')
        heartbeat = [{
            "timestamp": log.timestamp,
            "alignment_score": log.alignment_score,
            "color": log.color,
            "flatline": log.flatline,
            "violations": log.violations,
            "confidence": log.confidence,
            "prompt": log.prompt,
            "response": log.response,
        } for log in logs]

        resp = Response({
            "run_id": run.id,
            "status": run.status,
            "alignment_score": run.alignment_score,
            "heartbeat": heartbeat,
            "ended_at": run.ended_at,
        })
        resp["Cache-Control"] = "no-store"
        return resp


class ExportRhythmLog(APIView):
    """Optional export endpoint used by your URLs; add it back to avoid import errors."""
    permission_classes = [IsAuthenticated]

    def get(self, request, run_id):
        run = SimulationRun.objects.filter(id=run_id, user=request.user).first()
        if not run:
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
        return Response(export, status=200)
