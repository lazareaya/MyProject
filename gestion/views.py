from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from .models import Vehicule, Moniteur, Eleve
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from .forms import (
    VehiculeDisponibiliteFormSet,
    MoniteurDisponibiliteFormSet,
    EleveDisponibiliteFormSet
)





# Page d'accueil
class HomeView(TemplateView):
    template_name = "gestion/home.html"

# --- Gestion des Disponibilités pour les Véhicules ---
class VehiculeDisponibilitesManageView(View):
    template_name = 'gestion/vehicule_disponibilites_manage.html'

    def get(self, request, pk):
        vehicule = get_object_or_404(Vehicule, pk=pk)
        formset = VehiculeDisponibiliteFormSet(instance=vehicule)
        return render(request, self.template_name, {'vehicule': vehicule, 'formset': formset})

    def post(self, request, pk):
        vehicule = get_object_or_404(Vehicule, pk=pk)
        formset = VehiculeDisponibiliteFormSet(request.POST, instance=vehicule)
        if formset.is_valid():
            formset.save()
            return redirect('vehicules_list')
        return render(request, self.template_name, {'vehicule': vehicule, 'formset': formset})


# Vehicule Disponibilités
def manage_vehicule_disponibilites(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if request.method == 'POST':
        formset = VehiculeDisponibiliteFormSet(request.POST, instance=vehicule)
        if formset.is_valid():
            formset.save()
            return redirect('vehicules_list')
    else:
        formset = VehiculeDisponibiliteFormSet(instance=vehicule)
    return render(request, 'gestion/vehicule_disponibilites_manage.html', {'vehicule': vehicule, 'formset': formset})




    
# --- Vues pour les Véhicules ---

class VehiculeListView(ListView):
    model = Vehicule
    template_name = 'gestion/vehicules_list.html'
    context_object_name = 'vehicules'

class VehiculeCreateView(CreateView):
    model = Vehicule
    fields = ['nom', 'type_vehicule']
    template_name = 'gestion/vehicule_form.html'
    success_url = reverse_lazy('vehicules_list')

class VehiculeUpdateView(UpdateView):
    model = Vehicule
    fields = ['nom', 'type_vehicule']
    template_name = 'gestion/vehicule_form.html'
    success_url = reverse_lazy('vehicules_list')

class VehiculeDeleteView(DeleteView):
    model = Vehicule
    template_name = 'gestion/vehicule_confirm_delete.html'
    success_url = reverse_lazy('vehicules_list')








# --- Vues pour les Moniteurs (similaires, à adapter selon vos besoins) ---

# Moniteur Disponibilités
def manage_moniteur_disponibilites(request, pk):
    moniteur = get_object_or_404(Moniteur, pk=pk)
    if request.method == 'POST':
        formset = MoniteurDisponibiliteFormSet(request.POST, instance=moniteur)
        if formset.is_valid():
            formset.save()
            return redirect('moniteurs_list')
    else:
        formset = MoniteurDisponibiliteFormSet(instance=moniteur)
    return render(request, 'gestion/moniteur_disponibilites_manage.html', {'moniteur': moniteur, 'formset': formset})



class MoniteurDisponibilitesManageView(TemplateView):
    template_name = 'gestion/moniteur_disponibilites_manage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        moniteur_pk = self.kwargs.get('pk')
        moniteur = get_object_or_404(Moniteur, pk=moniteur_pk)
        context['moniteur'] = moniteur
        # Ici, vous ajouterez la logique pour passer le formset de disponibilités pour le moniteur
        return context

class MoniteurListView(ListView):
    model = Moniteur
    template_name = 'gestion/moniteurs_list.html'
    context_object_name = 'moniteurs'

class MoniteurCreateView(CreateView):
    model = Moniteur
    fields = ['nom', 'max_heures_consecutives', 'heures_souhaitees_semaine', 'heure_maximale_semaine']
    template_name = 'gestion/moniteur_form.html'
    success_url = reverse_lazy('moniteurs_list')

class MoniteurUpdateView(UpdateView):
    model = Moniteur
    fields = ['nom', 'max_heures_consecutives', 'heures_souhaitees_semaine', 'heure_maximale_semaine']
    template_name = 'gestion/moniteur_form.html'
    success_url = reverse_lazy('moniteurs_list')

class MoniteurDeleteView(DeleteView):
    model = Moniteur
    template_name = 'gestion/moniteur_confirm_delete.html'
    success_url = reverse_lazy('moniteurs_list')







# --- Vues pour les Élèves (similaires, à adapter selon vos besoins) ---


# Eleve Disponibilités
def manage_eleve_disponibilites(request, pk):
    eleve = get_object_or_404(Eleve, pk=pk)
    if request.method == 'POST':
        formset = EleveDisponibiliteFormSet(request.POST, instance=eleve)
        if formset.is_valid():
            formset.save()
            return redirect('eleves_list')
    else:
        formset = EleveDisponibiliteFormSet(instance=eleve)
    return render(request, 'gestion/eleve_disponibilites_manage.html', {'eleve': eleve, 'formset': formset})




class EleveDisponibilitesManageView(TemplateView):
    template_name = 'gestion/eleve_disponibilites_manage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        eleve_pk = self.kwargs.get('pk')
        eleve = get_object_or_404(Eleve, pk=eleve_pk)
        context['eleve'] = eleve
        return context

class EleveListView(ListView):
    model = Eleve
    template_name = 'gestion/eleves_list.html'
    context_object_name = 'eleves'

class EleveCreateView(CreateView):
    model = Eleve
    fields = [
        'nom',
        'heures_a_effectuer',
        'type_permis',
        'date_examen',
        'date_commencement_conduite',
        'secteur_examen',
        'max_heures_consecutives',
        'nombre_seance_jour',
        'historique_moniteurs'
    ]
    template_name = 'gestion/eleve_form.html'
    success_url = reverse_lazy('eleves_list')

class EleveUpdateView(UpdateView):
    model = Eleve
    fields = [
        'nom',
        'heures_a_effectuer',
        'type_permis',
        'date_examen',
        'date_commencement_conduite',
        'secteur_examen',
        'max_heures_consecutives',
        'nombre_seance_jour',
        'historique_moniteurs'
    ]
    template_name = 'gestion/eleve_form.html'
    success_url = reverse_lazy('eleves_list')

class EleveDeleteView(DeleteView):
    model = Eleve
    template_name = 'gestion/eleve_confirm_delete.html'
    success_url = reverse_lazy('eleves_list')
