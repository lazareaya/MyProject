# planning/management/commands/generate_planning.py

import datetime
from django.core.management.base import BaseCommand
from ortools.sat.python import cp_model

from planning.models import Seance
from gestion.models import Moniteur, Eleve, Vehicule


# Ajuste ce chemin si tes modèles se trouvent ailleurs.
# Exemple : from MyProject.gestion.models import ...
from gestion.models import (
    VehiculeDisponibilite, VehiculeNonDisponibilite,
    MoniteurDisponibilite, MoniteurNonDisponibilite,
    EleveDisponibilite
)




# ----------------------------------------------------------------------------
# FONCTIONS UTILITAIRES
# ----------------------------------------------------------------------------

def generate_recurring_intervals(rec_rule, start_date, end_date):
    """
    Génère une liste d'intervalles (tuples de datetime) pour une règle de disponibilité récurrente.
    rec_rule: dict avec clés "jours" (liste d'entiers, 0 pour lundi, ...),
              "start_time" et "end_time" (format "HH:MM:SS").
    """
    import datetime
    intervals = []
    current_date = start_date
    start_time = datetime.datetime.strptime(rec_rule["start_time"], "%H:%M:%S").time()
    end_time = datetime.datetime.strptime(rec_rule["end_time"], "%H:%M:%S").time()

    while current_date <= end_date:
        # current_date.weekday() : 0 = Lundi, 1 = Mardi, etc.
        if current_date.weekday() in rec_rule["jours"]:
            intervals.append((
                datetime.datetime.combine(current_date, start_time),
                datetime.datetime.combine(current_date, end_time)
            ))
        current_date += datetime.timedelta(days=1)
    return intervals


def subtract_exceptional_unavailability(intervals, exceptions):
    """
    Soustrait les indisponibilités exceptionnelles (exceptions) d'une liste d'intervalles (intervals).
    intervals: liste de (datetime_debut, datetime_fin)
    exceptions: liste de (datetime_debut, datetime_fin) à soustraire
    Retourne une nouvelle liste d'intervalles actifs.
    """
    result = []
    for interval in intervals:
        interval_start, interval_end = interval
        sub_intervals = [(interval_start, interval_end)]
        for exc_start, exc_end in exceptions:
            new_subs = []
            for (sub_start, sub_end) in sub_intervals:
                # Si l'indispo ne recouvre pas du tout ce sous-intervalle
                if exc_end <= sub_start or exc_start >= sub_end:
                    new_subs.append((sub_start, sub_end))
                else:
                    # Découpe éventuelle
                    if sub_start < exc_start:
                        new_subs.append((sub_start, exc_start))
                    if sub_end > exc_end:
                        new_subs.append((exc_end, sub_end))
            sub_intervals = new_subs
        result.extend(sub_intervals)
    # On enlève les potentiels vides
    result = [(s, e) for (s, e) in result if e > s]
    return result


def load_config_from_django():
    """
    Lit les données en base (Vehicule, Moniteur, Eleve) + leurs disponibilités
    et renvoie un dictionnaire 'config' sous la forme :
    {
      "vehicules": { "nom_vehicule": { "type": ..., "disponibilites": [...] } },
      "moniteurs": { "nom_moniteur": { ... } },
      "eleves":    { "nom_eleve": { ... } }
    }
    """
    planning_start = datetime.date(2025, 4, 6)
    planning_end   = datetime.date(2025, 5, 25)

    config = {
        "vehicules": {},
        "moniteurs": {},
        "eleves": {}
    }

    # ----------------------------------------------------------------
    # 1) VÉHICULES
    # ----------------------------------------------------------------
    vehicules_db = Vehicule.objects.all()
    for v in vehicules_db:
        v_data = {
            "type": v.type_vehicule,
            "disponibilites": []
        }
        # Disponibilités récurrentes
        intervals = []
        dispos = VehiculeDisponibilite.objects.filter(vehicule=v)
        for dispo in dispos:
            rec_rule = {
                "jours": [dispo.jour],  # Lundi=0, Mardi=1, ...
                "start_time": dispo.start_time.strftime("%H:%M:%S"),
                "end_time":   dispo.end_time.strftime("%H:%M:%S"),
            }
            intervals.extend(generate_recurring_intervals(rec_rule, planning_start, planning_end))

        # Indisponibilités exceptionnelles
        non_dispos = VehiculeNonDisponibilite.objects.filter(vehicule=v)
        exceptional = [
            (
                datetime.datetime.combine(nd.date_debut.date(), nd.date_debut.time()),
                datetime.datetime.combine(nd.date_fin.date(),   nd.date_fin.time())
            )
            for nd in non_dispos
        ]
        intervals = subtract_exceptional_unavailability(intervals, exceptional)

        v_data["disponibilites"] = intervals
        config["vehicules"][v.nom] = v_data

    # ----------------------------------------------------------------
    # 2) MONITEURS
    # ----------------------------------------------------------------
    moniteurs_db = Moniteur.objects.all()
    for m in moniteurs_db:
        m_data = {
            "max_heures_consecutives":     m.max_heures_consecutives,
            "heures_souhaitees_semaine":   m.heures_souhaitees_semaine,
            "heure_maximale_semaine":      m.heure_maximale_semaine,
            "disponibilites": []
        }
        intervals = []
        dispos_mon = MoniteurDisponibilite.objects.filter(moniteur=m)
        for dispo in dispos_mon:
            rec_rule = {
                "jours":      [dispo.jour],
                "start_time": dispo.start_time.strftime("%H:%M:%S"),
                "end_time":   dispo.end_time.strftime("%H:%M:%S"),
            }
            intervals.extend(generate_recurring_intervals(rec_rule, planning_start, planning_end))

        # Indisponibilités exceptionnelles (maladie, congés, etc.)
        mon_non_dispo = MoniteurNonDisponibilite.objects.filter(moniteur=m)
        exceptional = [
            (
                datetime.datetime.combine(nd.date_debut.date(), nd.date_debut.time()),
                datetime.datetime.combine(nd.date_fin.date(),   nd.date_fin.time())
            )
            for nd in mon_non_dispo
        ]
        intervals = subtract_exceptional_unavailability(intervals, exceptional)

        m_data["disponibilites"] = intervals
        config["moniteurs"][m.nom] = m_data

    # ----------------------------------------------------------------
    # 3) ÉLÈVES
    # ----------------------------------------------------------------
    eleves_db = Eleve.objects.all()
    for e in eleves_db:
        e_data = {
            "heures_a_effectuer":         e.heures_a_effectuer,
            "type_permis":                e.type_permis,
            "date_examen":                e.date_examen,
            "date_commencement_conduite": e.date_commencement_conduite,
            "secteur_examen":             e.secteur_examen,
            "max_heures_consecutives":    e.max_heures_consecutives,
            "nombre_seance_jour":         e.nombre_seance_jour or 1,
            "disponibilites":            {}
        }
        dispos_eleve = EleveDisponibilite.objects.filter(eleve=e).order_by("date", "start_time")
        for d in dispos_eleve:
            date_str = d.date.strftime("%Y-%m-%d")
            e_data["disponibilites"].setdefault(date_str, [])
            e_data["disponibilites"][date_str].append([
                d.start_time.strftime("%H:%M:%S"),
                d.end_time.strftime("%H:%M:%S"),
            ])

        config["eleves"][e.nom] = e_data

    return config






def generate_possible_sessions_for_day(day, planning_start_hour, planning_end_hour,
                                       moniteurs, eleves, vehicules):
    """
    Génère toutes les séances (sessions) possibles pour un jour donné,
    en croisant les disponibilités du moniteur, de l'élève et du véhicule.
    """
    possible_sessions = []
    possible_durations = [datetime.timedelta(hours=2), datetime.timedelta(hours=3)]
    day_start = datetime.datetime.combine(day, datetime.time(planning_start_hour, 0))
    day_end   = datetime.datetime.combine(day, datetime.time(planning_end_hour, 0))
    day_str   = day.strftime("%Y-%m-%d")

    for moniteur, mon_data in moniteurs.items():
        mon_intervals = [interval for interval in mon_data["disponibilites"]
                         if interval[0].date() == day]
        for eleve, eleve_data in eleves.items():
            # Générer des séances pour l'élève uniquement si le jour est compris
            # entre sa date_commencement_conduite et sa date_examen
            if day < eleve_data["date_commencement_conduite"] or day >= eleve_data["date_examen"]:
                continue
            if day_str not in eleve_data["disponibilites"]:
                continue
            # Convertir les chaînes "HH:MM:SS" en datetime
            eleve_intervals = []
            for interval in eleve_data["disponibilites"][day_str]:
                start_time = datetime.datetime.strptime(interval[0], "%H:%M:%S").time()
                end_time   = datetime.datetime.strptime(interval[1], "%H:%M:%S").time()
                eleve_intervals.append((datetime.datetime.combine(day, start_time),
                                        datetime.datetime.combine(day, end_time)))

            # La séance doit se terminer avant minuit du jour d'examen
            exam_dt = datetime.datetime.combine(eleve_data["date_examen"], datetime.time.min)

            for vehicule, veh_data in vehicules.items():
                if veh_data["type"] != eleve_data["type_permis"]:
                    continue
                veh_intervals = [interval for interval in veh_data["disponibilites"]
                                 if interval[0].date() == day]

                for m_interval in mon_intervals:
                    for e_interval in eleve_intervals:
                        inter_start = max(m_interval[0], e_interval[0], day_start)
                        inter_end   = min(m_interval[1], e_interval[1], day_end)
                        if inter_end <= inter_start:
                            continue
                        for v_interval in veh_intervals:
                            triple_start = max(inter_start, v_interval[0])
                            triple_end   = min(inter_end, v_interval[1], exam_dt)
                            if triple_end <= triple_start:
                                continue
                            for session_duration in possible_durations:
                                if session_duration > datetime.timedelta(hours=eleve_data["max_heures_consecutives"]):
                                    continue
                                if triple_end - triple_start >= session_duration:
                                    current_start = triple_start
                                    # On décale la fenêtre de 1h en 1h pour multiplier les créneaux possibles
                                    while current_start + session_duration <= triple_end:
                                        session = {
                                            "day": day,
                                            "moniteur": moniteur,
                                            "eleve": eleve,
                                            "vehicule": vehicule,
                                            "session_start": current_start,
                                            "session_end": current_start + session_duration,
                                            "duration": session_duration
                                        }
                                        possible_sessions.append(session)
                                        current_start += datetime.timedelta(hours=1)
    return possible_sessions





def create_decision_variables(sessions, model):
    return {i: model.NewBoolVar(f"session_{i}_selected") for i, _ in enumerate(sessions)}









def add_non_overlapping_constraints(model, sessions, session_vars, day,
                                    planning_start_hour, planning_end_hour,
                                    eleves, moniteurs, vehicules):
    """
    Empêche deux séances de se superposer pour un même élève / moniteur / véhicule.
    On itère sur chaque créneau horaire de la journée (ex. 8h-9h, 9h-10h, ...).
    """
    for hour in range(planning_start_hour, planning_end_hour):
        slot_start = datetime.datetime.combine(day, datetime.time(hour, 0))
        slot_end   = datetime.datetime.combine(day, datetime.time(hour+1, 0))

        for eleve in eleves.keys():
            sessions_covering = [
                i for i, s in enumerate(sessions)
                if s['eleve'] == eleve and s['day'] == day
                   and s['session_start'] <= slot_start
                   and s['session_end'] >= slot_end
            ]
            if sessions_covering:
                model.Add(sum(session_vars[i] for i in sessions_covering) <= 1)

        for moniteur in moniteurs.keys():
            sessions_covering = [
                i for i, s in enumerate(sessions)
                if s['moniteur'] == moniteur and s['day'] == day
                   and s['session_start'] <= slot_start
                   and s['session_end'] >= slot_end
            ]
            if sessions_covering:
                model.Add(sum(session_vars[i] for i in sessions_covering) <= 1)

        for vehicule in vehicules.keys():
            sessions_covering = [
                i for i, s in enumerate(sessions)
                if s['vehicule'] == vehicule and s['day'] == day
                   and s['session_start'] <= slot_start
                   and s['session_end'] >= slot_end
            ]
            if sessions_covering:
                model.Add(sum(session_vars[i] for i in sessions_covering) <= 1)


def add_student_daily_session_limit(model, sessions, session_vars, eleves, day):
    """
    Limite le nombre de séances par élève dans une journée à 'eleve["nombre_seance_jour"]'.
    """
    for eleve in eleves:
        relevant_sessions = [i for i, s in enumerate(sessions)
                             if s['eleve'] == eleve and s['day'] == day]
        model.Add(sum(session_vars[i] for i in relevant_sessions) <= eleves[eleve]['nombre_seance_jour'])


def add_moniteur_legal_max_constraint(model, sessions, session_vars,
                                      moniteurs, weekly_assigned, legal_max=39):
    """
    Limite le nombre total d'heures qu'un moniteur peut faire sur la semaine (max légal : 39).
    """
    for moniteur, mon_data in moniteurs.items():
        indices = [i for i, s in enumerate(sessions) if s["moniteur"] == moniteur]
        total_hours_expr = sum(
            int(sessions[i]['duration'].total_seconds() // 3600) * session_vars[i]
            for i in indices
        )
        already_assigned = weekly_assigned.get(moniteur, 0)
        model.Add(total_hours_expr + already_assigned <= legal_max)


def add_moniteur_personal_weekly_constraint(model, sessions, session_vars,
                                            moniteurs, weekly_assigned):
    """
    Limite le nombre d'heures pour un moniteur selon son 'heure_maximale_semaine'.
    """
    for moniteur, mon_data in moniteurs.items():
        indices = [i for i, s in enumerate(sessions) if s['moniteur'] == moniteur]
        total_hours_expr = sum(
            int(sessions[i]['duration'].total_seconds() // 3600) * session_vars[i]
            for i in indices
        )
        weekly_max = mon_data['heure_maximale_semaine']
        already_assigned = weekly_assigned.get(moniteur, 0)
        model.Add(total_hours_expr + already_assigned <= weekly_max)










def add_student_priority_penalty(model, sessions, session_vars, eleves, planning_start):
    """
    Objectif soft : pénaliser le déficit d'heures pour les élèves (urgent = date d'examen proche).
    """
    penalty_terms = []
    for s in eleves:
        required = eleves[s]['heures_a_effectuer']
        assigned_expr = sum(
            int(sessions[i]['duration'].total_seconds() // 3600) * session_vars[i]
            for i, sess in enumerate(sessions) if sess['eleve'] == s
        )
        deficit = model.NewIntVar(0, required, f"deficit_{s}")
        model.Add(deficit >= required - assigned_expr)

        days_remaining = (eleves[s]['date_examen'] - planning_start).days
        if days_remaining <= 0:
            # Si on est déjà le jour de l'examen ou après, on force le déficit à 0
            model.Add(deficit == 0)
            urgency = 100
        else:
            urgency = 100 // (days_remaining + 1)

        penalty_terms.append(urgency * deficit)
    return sum(penalty_terms)


def add_moniteur_priority_penalty(model, sessions, session_vars, moniteurs,
                                  penalty_coefficient=10, max_diff_bound=100):
    """
    Objectif soft : pénaliser le déficit d'heures pour les moniteurs
    qui souhaitent un certain nombre d'heures dans la semaine.
    """
    penalty_terms = []
    for moniteur, mon_data in moniteurs.items():
        indices = [i for i, s in enumerate(sessions) if s['moniteur'] == moniteur]
        total_hours_expr = sum(
            int(sessions[i]['duration'].total_seconds() // 3600) * session_vars[i]
            for i in indices
        )
        target = mon_data['heures_souhaitees_semaine']
        deficit = model.NewIntVar(0, max_diff_bound, f"deficit_{moniteur}")
        model.Add(deficit >= target - total_hours_expr)
        penalty_terms.append(penalty_coefficient * deficit)
    return sum(penalty_terms)








def check_all_students_hours_completed(eleves):
    """
    Vérifie si tous les élèves ont complété leurs heures.
    Retourne True si tous ont terminé, sinon False.
    """
    incomplete = {}
    for student, data in eleves.items():
        # Ici, 'eleves' est un dictionnaire initialisé dans load_config_from_django()
        if data["heures_a_effectuer"] > 0:
            incomplete[student] = data["heures_a_effectuer"]
    
    if not incomplete:
        print("Tous les élèves ont complété leurs heures de conduite avant leur date d'examen.")
        return True
    else:
        print("Les élèves suivants n'ont pas complété leurs heures de conduite :")
        for student, remaining in incomplete.items():
            print(f"  {student}: {remaining} heure(s) restante(s)")
        return False


def export_schedule_to_html(global_schedule, output_file="planning.html"):
    """
    Exporte le planning global dans un fichier HTML simple.
    """
    schedule_by_day = {}
    for sess in global_schedule:
        day_str = sess['day'].strftime("%Y-%m-%d")
        schedule_by_day.setdefault(day_str, []).append(sess)
    
    days = sorted(schedule_by_day.keys())
    time_slots = [datetime.time(hour, 0) for hour in range(8, 20)]
    
    html = """
    <html>
    <head>
      <meta charset="utf-8">
      <title>Planning de Conduite</title>
      <style>
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 5px; vertical-align: top; }
        th { background-color: #f0f0f0; }
      </style>
    </head>
    <body>
      <h1>Planning de Conduite</h1>
      <table>
        <tr>
          <th>Créneau</th>
    """
    for d in days:
        html += f"<th>{d}</th>"
    html += "</tr>\n"
    
    for slot in time_slots:
        slot_str = slot.strftime("%H:%M")
        html += f"<tr><td><strong>{slot_str}</strong></td>"
        for d in days:
            cell_content = ""
            if d in schedule_by_day:
                for sess in schedule_by_day[d]:
                    if sess['session_start'].time() == slot:
                        cell_content += (
                            f"<b>{sess['session_start'].strftime('%H:%M')}"
                            f"-{sess['session_end'].strftime('%H:%M')}</b><br>"
                            f"Moniteur: {sess['moniteur']}<br>"
                            f"Élève: {sess['eleve']}<br>"
                            f"Véhicule: {sess['vehicule']}<br><hr>"
                        )
            html += f"<td>{cell_content}</td>"
        html += "</tr>\n"
    
    html += """
      </table>
    </body>
    </html>
    """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Planning exporté dans {output_file}")








# ----------------------------------------------------------------------------
# FONCTION PRINCIPALE DE GÉNÉRATION DU PLANNING (Rolling Horizon)
# ----------------------------------------------------------------------------
def main():
    # 1) Vider la table Seance pour générer un planning vierge
    Seance.objects.all().delete()
    print("Table Seance vidée : l'ancien planning est supprimé.")

    # 2) Charger la configuration depuis Django
    config = load_config_from_django()
    vehicules = config["vehicules"]
    moniteurs = config["moniteurs"]
    eleves = config["eleves"]

    # 3) Définir la période de planification
    start_date = datetime.date(2025, 4, 6)
    end_date = datetime.date(2025, 5, 25)
    planning_start_hour = 8
    planning_end_hour = 20

    global_schedule = []
    # Initialiser le cumul hebdomadaire pour chaque moniteur
    weekly_assigned = {mon: 0 for mon in moniteurs.keys()}

    current_date = start_date
    while current_date <= end_date:
        # Ignorer les dimanches
        if current_date.weekday() == 6:
            current_date += datetime.timedelta(days=1)
            continue

        # Réinitialiser le cumul hebdomadaire chaque lundi
        if current_date.weekday() == 0:
            weekly_assigned = {mon: 0 for mon in moniteurs.keys()}

        # Créer un modèle CP-SAT pour le jour
        model_day = cp_model.CpModel()

        # Générer les séances possibles pour ce jour
        sessions_day = generate_possible_sessions_for_day(
            current_date, planning_start_hour, planning_end_hour, moniteurs, eleves, vehicules
        )
        if not sessions_day:
            current_date += datetime.timedelta(days=1)
            continue

        session_vars_day = create_decision_variables(sessions_day, model_day)

        # Contraintes Hard
        add_non_overlapping_constraints(
            model_day, sessions_day, session_vars_day,
            current_date, planning_start_hour, planning_end_hour, eleves, moniteurs, vehicules
        )
        add_student_daily_session_limit(
            model_day, sessions_day, session_vars_day, eleves, current_date
        )
        add_moniteur_legal_max_constraint(
            model_day, sessions_day, session_vars_day, moniteurs, weekly_assigned, legal_max=39
        )
        add_moniteur_personal_weekly_constraint(
            model_day, sessions_day, session_vars_day, moniteurs, weekly_assigned
        )

        # Contraintes Soft (objectifs)
        student_priority = add_student_priority_penalty(model_day, sessions_day, session_vars_day, eleves, current_date)
        moniteur_priority = add_moniteur_priority_penalty(model_day, sessions_day, session_vars_day, moniteurs)
        model_day.Minimize(student_priority + moniteur_priority)

        # Résoudre le modèle pour le jour courant
        solver_day = cp_model.CpSolver()
        status = solver_day.Solve(model_day)

        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            print(f"\nJournée planifiée : {current_date}")
            for i, sess in enumerate(sessions_day):
                if solver_day.Value(session_vars_day[i]) == 1:
                    global_schedule.append(sess)
                    hours = int(sess["duration"].total_seconds() // 3600)
                    
                    # Mise à jour de l'élève dans le dictionnaire local
                    eleves[sess["eleve"]]["heures_a_effectuer"] = max(
                        0,
                        eleves[sess["eleve"]]["heures_a_effectuer"] - hours
                    )
                    
                    # Mise à jour du cumul hebdomadaire pour le moniteur
                    weekly_assigned[sess["moniteur"]] += hours
                    # Mise à jour du souhait hebdomadaire du moniteur dans le dictionnaire local
                    moniteurs[sess["moniteur"]]["heures_souhaitees_semaine"] = max(
                        0,
                        moniteurs[sess["moniteur"]]["heures_souhaitees_semaine"] - hours
                    )

                    # MISE À JOUR en base : Actualiser l'objet Eleve pour que le champ heures_a_effectuer soit modifié
                    eleve_obj = Eleve.objects.get(nom=sess["eleve"])
                    eleve_obj.heures_a_effectuer = max(
                        0,
                        eleve_obj.heures_a_effectuer - hours
                    )
                    eleve_obj.save()

                    # CRÉATION de la séance en base
                    Seance.objects.create(
                        moniteur=Moniteur.objects.get(nom=sess["moniteur"]),
                        eleve=Eleve.objects.get(nom=sess["eleve"]),
                        vehicule=Vehicule.objects.get(nom=sess["vehicule"]),
                        start_datetime=sess["session_start"],
                        end_datetime=sess["session_end"]
                    )

                    print(
                        f"  Session : {sess['session_start'].time()} - {sess['session_end'].time()} | "
                        f"Moniteur: {sess['moniteur']}, Élève: {sess['eleve']}, Véhicule: {sess['vehicule']}"
                    )
        else:
            print(f"Aucune solution trouvée pour le jour {current_date}")

        current_date += datetime.timedelta(days=1)

    # Affichage global du planning dans la console
    print("\nPlanning global sur la période :")
    for sess in global_schedule:
        print(
            f"{sess['day']} {sess['session_start'].time()} - {sess['session_end'].time()} | "
            f"Moniteur: {sess['moniteur']}, Élève: {sess['eleve']}, Véhicule: {sess['vehicule']}"
        )

    # Vérification : tous les élèves ont-ils terminé leurs heures en base ?
    if check_all_students_hours_completed(eleves):
        print("Tous les élèves ont effectué leurs heures avant leur examen.")
    else:
        print("Certains élèves n'ont pas terminé leurs heures avant leur examen.")


class Command(BaseCommand):
    help = "Génère le planning de conduite (OR-Tools) en lisant les données Django."

    def handle(self, *args, **options):
        main()