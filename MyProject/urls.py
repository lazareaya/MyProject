# MyProject/urls.py
from django.contrib import admin
from django.urls import path, include
from planning.admin import admin_site as planning_admin_site

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gestion.urls')), 
    path('planning-admin/', planning_admin_site.urls),# Ceci inclut toutes les URLs définies dans gestion/urls.py à la racine
    path('planning/', include('planning.urls')),
]
