from django.forms import ModelForm
import django.forms as forms
from distribution.models import CreneauHoraire


class CreneauForm(ModelForm):
    nombre_maximal_inscriptions_file_attente = forms.IntegerField()
    nombre_creneaux = forms.IntegerField()

    class Meta:
        model = CreneauHoraire
        fields = ['date_heure_debut', 'duree_en_minutes', 'nombre_maximal_inscriptions']


class DateForm(forms.Form):
    date = forms.DateField()
