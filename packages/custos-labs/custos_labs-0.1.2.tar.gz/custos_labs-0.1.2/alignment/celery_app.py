import os
from celery import Celery
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alignment.settings")

# Create Celery app
app = Celery("alignment")

# Configure the broker to use Upstash Redis with TLS
app.conf.broker_url = os.getenv("REDIS_URL")
app.conf.broker_use_ssl = {"ssl_cert_reqs": "none"} 

# Load the rest of Celery config from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks from all registered Django apps
app.autodiscover_tasks()
