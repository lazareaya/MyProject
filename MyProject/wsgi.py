"""
WSGI config for MyProject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import django
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MyProject.settings")

# Configure Django et exécute les migrations automatiquement au démarrage.
django.setup()
try:
    # Exécute les migrations de manière non interactive.
    call_command("migrate", interactive=False)
except Exception as e:
    # Vous pouvez loguer l'erreur ou l'imprimer ; à adapter selon vos besoins.
    print("Erreur lors de l'exécution des migrations :", e)

application = get_wsgi_application()
