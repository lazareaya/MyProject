from django.db import models
from django.core.validators import MinValueValidator

DAY_CHOICES = (
    (0, 'Lundi'),
    (1, 'Mardi'),
    (2, 'Mercredi'),
    (3, 'Jeudi'),
    (4, 'Vendredi'),
    (5, 'Samedi'),
    (6, 'Dimanche'),
)

VEHICULE_TYPE_CHOICES = (
    ('manuel', 'Manuel'),
    ('auto', 'Auto'),
)

PERMIS_CHOICES = (
    ('manuel', 'Manuel'),
    ('auto', 'Auto'),
)

# ---------------------
#   Modèles Véhicules
# ---------------------

class Vehicule(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    type_vehicule = models.CharField(max_length=50, choices=VEHICULE_TYPE_CHOICES)

    def __str__(self):
        return self.nom


class VehiculeDisponibilite(models.Model):
    """
    Disponibilités récurrentes du véhicule (ex. tous les lundis de 8h à 12h).
    """
    vehicule = models.ForeignKey(
        Vehicule,
        related_name='disponibilites_rec',
        on_delete=models.CASCADE
    )
    jour = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.vehicule.nom} - {self.get_jour_display()} ({self.start_time} - {self.end_time})"


class VehiculeNonDisponibilite(models.Model):
    """
    Indisponibilités exceptionnelles (pannes, réparations, etc.)
    """
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    motif = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Non dispo {self.vehicule.nom} du {self.date_debut} au {self.date_fin}"


# ---------------------
#   Modèles Moniteurs
# ---------------------

class Moniteur(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    max_heures_consecutives = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    heures_souhaitees_semaine = models.PositiveIntegerField()
    heure_maximale_semaine = models.PositiveIntegerField()

    def __str__(self):
        return self.nom


class MoniteurDisponibilite(models.Model):
    """
    Disponibilités récurrentes du moniteur.
    """
    moniteur = models.ForeignKey(
        Moniteur,
        related_name='disponibilites_rec',
        on_delete=models.CASCADE
    )
    jour = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.moniteur.nom} - {self.get_jour_display()} ({self.start_time} - {self.end_time})"


class MoniteurNonDisponibilite(models.Model):
    """
    Indisponibilités ponctuelles ou exceptionnelles du moniteur (maladie, congés, etc.)
    """
    moniteur = models.ForeignKey(Moniteur, on_delete=models.CASCADE)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    motif = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Non dispo {self.moniteur.nom} du {self.date_debut} au {self.date_fin}"


class PreferenceHeureCommencement(models.Model):
    moniteur = models.ForeignKey(
        Moniteur,
        related_name='preferences_heure_commencement',
        on_delete=models.CASCADE
    )
    jour = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    heure_commencement = models.TimeField()

    def __str__(self):
        return f"{self.moniteur.nom} - {self.get_jour_display()} : {self.heure_commencement}"


# ---------------------
#   Modèles Élèves
# ---------------------

class Eleve(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    heures_a_effectuer = models.PositiveIntegerField()
    type_permis = models.CharField(max_length=20, choices=PERMIS_CHOICES)
    date_examen = models.DateField()
    date_commencement_conduite = models.DateField()
    secteur_examen = models.CharField(max_length=100)
    max_heures_consecutives = models.PositiveIntegerField()
    nombre_seance_jour = models.PositiveIntegerField(null=True, blank=True)

    # Historique des moniteurs ayant suivi l'élève
    historique_moniteurs = models.ManyToManyField(
        Moniteur,
        blank=True,
        related_name="eleves_historiques"
    )

    def __str__(self):
        return self.nom


class EleveDisponibilite(models.Model):
    """
    Disponibilités ponctuelles de l'élève (jours et heures exactes).
    """
    eleve = models.ForeignKey(
        Eleve,
        related_name='disponibilites',
        on_delete=models.CASCADE
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.eleve.nom} - {self.date} ({self.start_time} - {self.end_time})"
