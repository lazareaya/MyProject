# planning/views.py

from django.shortcuts import render
from django.http import JsonResponse
from .models import Seance
from gestion.models import Eleve

def check_all_students_hours_completed():
    """
    Vérifie si tous les élèves ont complété leurs heures de conduite.
    Parcourt tous les élèves et s'il en trouve avec un nombre d'heures > 0,
    renvoie False et un message listant ces élèves et leur nombre d'heures restantes.
    Sinon, renvoie True et un message indiquant que tous les élèves sont à jour.
    """
    incomplete = {}
    for eleve in Eleve.objects.all():
        # On suppose que l'attribut "heures_a_effectuer" est stocké dans le modèle Eleve.
        if eleve.heures_a_effectuer > 0:
            incomplete[eleve.nom] = eleve.heures_a_effectuer

    if not incomplete:
        return (True, "Tous les élèves ont complété leurs heures de conduite avant leur date d'examen.")
    else:
        msg = "Les élèves suivants n'ont pas complété leurs heures : "
        for student, hours in incomplete.items():
            msg += f"{student} ({hours}h)  "
        return (False, msg)




def calendar_view(request):
    completed, completion_message = check_all_students_hours_completed()
    context = {
        'completion_status': completed,
        'completion_message': completion_message,
    }
    return render(request, 'planning/calendar.html', context)
   

def api_seances(request):
    """
    Renvoie toutes les séances (Seance) au format JSON pour FullCalendar.
    """
    seances = Seance.objects.all()
    events = []
    
    # Pour chaque séance en base, on construit un "event" selon la norme FullCalendar
    for s in seances:
        events.append({
            "id": s.id,
            # On inclut Moniteur, Élève, Véhicule dans le titre (ou tu peux séparer)
            "title": f"{s.eleve.nom} / {s.moniteur.nom} / {s.vehicule.nom}",
            
            # start / end : ISO 8601 => ex. "2025-04-14T15:00:00"
            "start": s.start_datetime.isoformat(),
            "end":   s.end_datetime.isoformat(),
            
            # extendedProps : infos supplémentaires si besoin
            # "extendedProps": {
            #     "vehicule": s.vehicule.nom,
            # }
        })
    
    # Retourne la liste d'événements au format JSON
    return JsonResponse(events, safe=False)
