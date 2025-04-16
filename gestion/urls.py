from django.urls import path
from . import views
from .views import (
    HomeView, 
    # Véhicules
    VehiculeListView, VehiculeCreateView, VehiculeUpdateView, VehiculeDeleteView,
    VehiculeDisponibilitesManageView,  # Si vous avez une gestion de disponibilité pour les véhicules
    # Moniteurs
    MoniteurListView, MoniteurCreateView, MoniteurUpdateView, MoniteurDeleteView,
    MoniteurDisponibilitesManageView,
    # Élèves
    EleveListView, EleveCreateView, EleveUpdateView, EleveDeleteView,
    EleveDisponibilitesManageView,
)

urlpatterns = [
    # Page d'accueil
    path('', HomeView.as_view(), name='home'),

    # Routes pour les Véhicules
    path('vehicules/', VehiculeListView.as_view(), name='vehicules_list'),
    path('vehicules/ajouter/', VehiculeCreateView.as_view(), name='vehicule_add'),
    path('vehicules/modifier/<int:pk>/', VehiculeUpdateView.as_view(), name='vehicule_edit'),
    path('vehicules/supprimer/<int:pk>/', VehiculeDeleteView.as_view(), name='vehicule_delete'),
    path('vehicules/<int:pk>/disponibilites/manage/', VehiculeDisponibilitesManageView.as_view(), name='vehicule_disponibilites_manage'),
    path('vehicules/<int:pk>/disponibilites/manage/', views.manage_vehicule_disponibilites, name='vehicule_disponibilites_manage'),
    path('vehicules/<int:pk>/disponibilites/manage/', views.VehiculeDisponibilitesManageView.as_view(), name='vehicule_disponibilites_manage'),

    
    # Routes pour les Moniteurs
    path('moniteurs/', MoniteurListView.as_view(), name='moniteurs_list'),
    path('moniteurs/ajouter/', MoniteurCreateView.as_view(), name='moniteur_add'),
    path('moniteurs/modifier/<int:pk>/', MoniteurUpdateView.as_view(), name='moniteur_edit'),
    path('moniteurs/supprimer/<int:pk>/', MoniteurDeleteView.as_view(), name='moniteur_delete'),
    path('moniteurs/<int:pk>/disponibilites/manage/', MoniteurDisponibilitesManageView.as_view(), name='moniteur_disponibilites_manage'),
    path('moniteurs/<int:pk>/disponibilites/manage/', views.manage_moniteur_disponibilites, name='moniteur_disponibilites_manage'),
    
    

    # Routes pour les Élèves
    path('eleves/', EleveListView.as_view(), name='eleves_list'),
    path('eleves/ajouter/', EleveCreateView.as_view(), name='eleve_add'),
    path('eleves/modifier/<int:pk>/', EleveUpdateView.as_view(), name='eleve_edit'),
    path('eleves/supprimer/<int:pk>/', EleveDeleteView.as_view(), name='eleve_delete'),
    path('eleves/<int:pk>/disponibilites/manage/', EleveDisponibilitesManageView.as_view(), name='eleve_disponibilites_manage'),
    path('eleves/<int:pk>/disponibilites/manage/', views.manage_eleve_disponibilites, name='eleve_disponibilites_manage'),
    
    
]
