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
from django.contrib.auth import get_user_model

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


django.setup()
User = get_user_model()

# Créez un superuser si aucun n'existe (exemple de création avec des valeurs par défaut)
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('Lazare', 's2244145@gmail.com', 'IUGZ2752HGCS')