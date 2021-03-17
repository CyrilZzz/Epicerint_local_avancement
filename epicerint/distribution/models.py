from django.db import models
from django.contrib.auth.models import User
import locale
# from django.contrib.humanize.templatetags.humanize import naturaltime, naturalday
from django.utils.timezone import localtime
from datetime import datetime
from django.utils import timezone


# class DistributionManager(models.Manager):
#     def creneaux_tous_complets(self):
#         for creneau in self.creneaux.all():
#             if not creneau.nombre_maximal_inscriptions == creneau.inscriptions_creneaux.all().count():
#                 return False
#         return True


class Distribution(models.Model):
    nombre_maximal_inscriptions_file_attente = models.IntegerField()
    date = models.DateField()
    liste_prioritaire = models.OneToOneField('self', on_delete=models.CASCADE, related_name='distribution_avantageuse', blank=True, null=True)
    # models.PROTECT : On ne peut pas supprimer une liste d'attente si
    # une distribution qui l'utilise comme liste de personnes prioritaires existe.
    # on_delete = models.CASCADE n'est pas optimale...
    reservations_prioritaires = models.BooleanField()  # Si le booléen vaut True, seules les personnes prioritaires peuvent s'inscrire
    # creneaux_tous_complets = DistributionManager()

    def __str__(self):
        return f"Distribution du {self.date.strftime('%d %b')}"


class Beneficiaire(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='beneficiaire')
    CHOIX_SEXE = [
        ('masculin', 'masculin'),
        ('féminin', 'féminin'),
    ]
    sexe = models.CharField(
        max_length=10,
        choices=CHOIX_SEXE,
        default='masculin',
    )

    def __str__(self):
        return self.user.username


class InscriptionAttente(models.Model):
    distribution = models.ForeignKey(
        Distribution, on_delete=models.CASCADE, related_name='inscriptions_en_attente')
    beneficiaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscriptions_file_attente')

    def __str__(self):
        return str(self.distribution)


class CreneauHoraire(models.Model):
    distribution = models.ForeignKey(Distribution, on_delete=models.CASCADE, related_name='creneaux')
    date_heure_debut = models.DateTimeField()
    duree_en_minutes = models.IntegerField()
    nombre_maximal_inscriptions = models.IntegerField()

    def __str__(self):
        locale.setlocale(locale.LC_TIME, '')
        return str(localtime(self.date_heure_debut).strftime('le %d %b à %Hh%M'))


class InscriptionCreneau(models.Model):
    """UNE PERSONNE, UNE HORAIRE"""
    creneau_horaire = models.ForeignKey(CreneauHoraire, on_delete=models.CASCADE, related_name='inscriptions_creneaux')
    beneficiaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rdvs')
    # colis_recupere = models.BooleanField()

    def __str__(self):
        return f"créneau horaire: {self.creneau_horaire}, bénéficiaire: {self.beneficiaire} "


class ColisNonRecupere(models.Model):
    creneau_horaire = models.ForeignKey(CreneauHoraire, on_delete=models.CASCADE, related_name='colis_non_recuperes')
    beneficiaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='colis_manques')

    def __str__(self):
        return f"{self.beneficiaire} n'a pas pris son colis pendant le {self.creneau_horaire}."


# def creer_utilisateurs(n):
#     """copier coller le corps de cette fonction dans le terminal.
#     Attention, il faut avoir supprimé tous les utilisateurs avant pour faire le ménage."""
#     from django.contrib.auth.models import User
#     noms = ['abc' + str(k) for k in range(1, 21)]
#     for nom in noms:
#         user = User.objects.create_user(nom, 'cyrilza@yahoo.fr', 'mot_de_passe')
#         user.save()


# from distribution.models import Beneficiaire
#
# from distribution.models import Beneficiaire
# In [8]: for user in User.objects.all():
#    ...:     beneficiaire = Beneficiaire(user=user, sexe='masculin')
#    ...:     beneficiaire.save()
# code pour créer des beneficiaires
