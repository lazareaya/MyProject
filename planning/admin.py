
from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import redirect



# Import de la fonction de génération du planning depuis le module de commande.
# Assure-toi que ce chemin est correct selon ton organisation.
from planning.management.commands.generate_planning import main as generate_planning

# Définition d'un AdminSite personnalisé pour y ajouter notre vue customisée.
class PlanningAdminSite(admin.AdminSite):
    site_header = "Administration du Planning"

    def get_urls(self):
        # Récupère les URLs par défaut de l'admin
        urls = super().get_urls()
        # Ajoute notre URL personnalisée pour re-générer le planning
        custom_urls = [
            path('re_generate/', self.admin_view(self.re_generate), name='re_generate'),
        ]
        return custom_urls + urls

    def re_generate(self, request):
        """
        Vue qui déclenche la régénération complète du planning.
        Accessible depuis l'URL /admin/re_generate/
        """
        try:
            # Appel de la fonction principale de génération du planning.
            generate_planning()
            messages.success(request, "Le planning a été régénéré avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la régénération du planning: {e}")
        # Redirige vers l'index de l'admin
        return redirect(reverse('admin:index'))

# Instanciation de l'admin site personnalisé.
admin_site = PlanningAdminSite(name='planningadmin')

# On peut enregistrer ici un ou plusieurs modèles, par exemple le modèle Seance.
from planning.models import Seance
admin_site.register(Seance)