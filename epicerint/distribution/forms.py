from django import forms
from django.utils import timezone
from django.forms import ModelForm
from .models import CreneauHoraire, Beneficiaire, Distribution
from django.db.models import F, Count


class ChoixAttenteForm(forms.Form): # j'aurais préféré faire une requête où on n'affiche rien s'il reste des places de créneaux en filtrant sur
    choix = forms.ModelChoiceField( # la fonction créneaux tous complets... Mais c'est une requête très avancée. Mieux vaut
        # bien lire la doc sur les requêtes et les expressions de requêtes avant de se lancer dansle code.
        queryset=Distribution.objects
            .annotate(num_inscriptions=Count("inscriptions_en_attente"))
            .filter(num_inscriptions__lt=F('nombre_maximal_inscriptions_file_attente'))
            .filter(date__gte=timezone.now().date())  # gte : greater or equal
    )


class ChoixCreneauForm(forms.Form):
    choix = forms.ModelChoiceField(
        queryset=CreneauHoraire.objects
            .annotate(num_inscriptions=Count("inscriptions_creneaux"))  # rajoute colonne nommée num_inscriptions virtuelle qui compte le nombre d'inscriptions de chaque créneau
            .filter(num_inscriptions__lt=F('nombre_maximal_inscriptions'))
            .filter(date_heure_debut__gt=timezone.now())
    )


class AnnulerRdvForm(forms.Form):
    annuler_mes_rdv = forms.BooleanField(required=False)


class DesinscriptionListeAttenteForm(forms.Form):
    supprimer_mon_inscription = forms.BooleanField(required=False)


class ProfilForm(ModelForm):
    class Meta:
        model = Beneficiaire
        exclude = ('user',)
