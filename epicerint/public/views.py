from datetime import datetime
from .models import Annonce
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def contacts(request):
    return render(request, 'contacts.html')


@login_required
def accueil(request):
    annonces = Annonce.objects.all()
    annonces = reversed(annonces)
    return render(request, 'annonces.html', {'annonces': annonces})


def reponse(request, reponse_requete):
    return render(request, 'reponses_requetes.html', {'reponse_requete': reponse_requete})
