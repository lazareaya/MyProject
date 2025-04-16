from django.contrib import admin
from django import forms
from .models import (
    Vehicule, VehiculeDisponibilite, VehiculeNonDisponibilite,
    Moniteur, MoniteurDisponibilite, PreferenceHeureCommencement,
    Eleve, EleveDisponibilite, MoniteurNonDisponibilite
)


class EleveAdminForm(forms.ModelForm):
    class Meta:
        model = Eleve
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(EleveAdminForm, self).__init__(*args, **kwargs)
        self.fields['historique_moniteurs'].initial = []


class EleveDisponibiliteInline(admin.TabularInline):
    model = EleveDisponibilite
    extra = 1


class EleveAdmin(admin.ModelAdmin):
    form = EleveAdminForm
    list_display = ('nom', 'date_examen', 'date_commencement_conduite', 'secteur_examen', 'heures_a_effectuer')
    inlines = [EleveDisponibiliteInline]
    filter_horizontal = ('historique_moniteurs',)

admin.site.register(Eleve, EleveAdmin)


class VehiculeDisponibiliteInline(admin.TabularInline):
    model = VehiculeDisponibilite
    extra = 1

# Nouvel inline pour gérer les indisponibilités exceptionnelles
class VehiculeNonDisponibiliteInline(admin.TabularInline):
    model = VehiculeNonDisponibilite
    extra = 1


class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_vehicule')
    inlines = [VehiculeDisponibiliteInline, VehiculeNonDisponibiliteInline]
    search_fields = ('nom', 'type_vehicule')

admin.site.register(Vehicule, VehiculeAdmin)


class MoniteurDisponibiliteInline(admin.TabularInline):
    model = MoniteurDisponibilite
    extra = 1

class PreferenceHeureCommencementInline(admin.TabularInline):
    model = PreferenceHeureCommencement
    extra = 1
    
class MoniteurNonDisponibiliteInline(admin.TabularInline):
    model = MoniteurNonDisponibilite
    extra = 1


class MoniteurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'max_heures_consecutives', 'heures_souhaitees_semaine', 'heure_maximale_semaine')
    inlines = [MoniteurDisponibiliteInline, PreferenceHeureCommencementInline,MoniteurNonDisponibiliteInline]
    search_fields = ('nom',)

admin.site.register(Moniteur, MoniteurAdmin)
