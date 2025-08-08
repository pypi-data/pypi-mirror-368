# simulator/urls.py


from django.urls import path
from .views import CreateSimulationRun, LogAIResponse, GetRhythmLog, ExportRhythmLog
from django.http import JsonResponse


urlpatterns = [
    path('ping/', lambda request: JsonResponse({'pong': True})),
    path('runs/', CreateSimulationRun.as_view(), name='simulator-run-create'),
    path('logs/', LogAIResponse.as_view(), name='simulator-log-response'),
    path('rhythm/<int:run_id>/', GetRhythmLog.as_view(), name='simulator-rhythm-log'),
    path('export/<int:run_id>/', ExportRhythmLog.as_view(), name='simulator-export-log'),
]

