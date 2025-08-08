# alignment/urls.py



from django.urls import path, include
from api.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('grappelli/', include('grappelli.urls')),
    path('api/', include('api.urls')),
    path("api/chatbot-ai/", include("chatbot_ai.urls")),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/auth/social/', include('allauth.socialaccount.urls')),
    path('accounts/', include('allauth.urls')),
    path('explorer/', include('explorer.urls')),
    path("simulator/", include("simulator.urls")),
]


