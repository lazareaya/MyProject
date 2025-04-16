from django.forms import inlineformset_factory
from .models import (
    Vehicule, VehiculeDisponibilite,
    Moniteur, MoniteurDisponibilite,
    Eleve, EleveDisponibilite
)

VehiculeDisponibiliteFormSet = inlineformset_factory(
    Vehicule,
    VehiculeDisponibilite,
    fields=('jour', 'start_time', 'end_time'),
    extra=3,  # tu peux modifier ce nombre pour afficher plus de lignes vides par défaut
    can_delete=True
)

MoniteurDisponibiliteFormSet = inlineformset_factory(
    Moniteur, MoniteurDisponibilite,
    fields=('jour', 'start_time', 'end_time'),
    extra=1, can_delete=True
)

EleveDisponibiliteFormSet = inlineformset_factory(
    Eleve, EleveDisponibilite,
    fields=('date', 'start_time', 'end_time'),
    extra=1, can_delete=True
)
