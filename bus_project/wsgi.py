import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bus_project.settings')

application = get_wsgi_application()

# Alias application as app for Vercel serverless function
app = application
