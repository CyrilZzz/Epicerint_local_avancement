from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
# https://stackoverflow.com/questions/12003736/django-login-required-decorator-for-a-superuser
# from django.contrib.humanize.templatetags.humanize import naturaltime
from datetime import datetime, timedelta
from .forms import CreneauForm, DateForm
from distribution.models import InscriptionCreneau, CreneauHoraire, Distribution, InscriptionAttente
from public.views import reponse


@staff_member_required
def afficher_inscriptions(request):
    creneaux_horaires = CreneauHoraire.objects.all()
    tableau_double_entree = []
    liste_dates_debut = []
    nombre_maximal_global_inscriptions = 1
    for creneau_horaire in creneaux_horaires:  # mettre un max à la place
        if creneau_horaire.nombre_maximal_inscriptions > nombre_maximal_global_inscriptions:
            nombre_maximal_global_inscriptions = creneau_horaire.nombre_maximal_inscriptions
        tableau_double_entree.append(creneau_horaire.inscriptions_creneaux.all())
        liste_dates_debut.append(str(creneau_horaire))
    return render(
        request, 'affichage_inscriptions.html', {'tableau_double_entree': zip(liste_dates_debut, tableau_double_entree),
                                                 'nombre_maximal_global_inscriptions': range(
                                                     1, nombre_maximal_global_inscriptions + 1),
                                                 }
    )


# renommer la variable créneau horaire qui porte à confusion


@staff_member_required
def afficher_liste_attente(request):
    """Il est vraiment difficile de transposer le tableau car le code HTML nous oblige
    à remplir un tableau ligne par ligne et on ne peut pas le faire colonne par colonne.
    On utilisera donc du code Javascript pour transposer le tableau à la fin.
    Même en transposant avec numpy avant, c'est inadéquat."""
    longueur_maximale_liste_attente = 0
    distributions = Distribution.objects.all()
    tableau_double_entree = []
    liste_distributions = []
    for distribution in distributions:
        longueur_candidate = distribution.inscriptions_en_attente.all().count()
        if longueur_candidate > longueur_maximale_liste_attente:
            longueur_maximale_liste_attente = longueur_candidate
        tableau_double_entree.append(distribution.inscriptions_en_attente.all())
        liste_distributions.append(distribution)
    return render(
        request, 'affichage_liste_attente.html', {
            'tableau_double_entree': zip(liste_distributions, tableau_double_entree),
            'longueur_maximale_liste_attente': range(
                1, longueur_maximale_liste_attente + 1)
        })


def creer_creneaux_automatiquement(distribution, date_heure_debut, duree, nombre_creneaux, nombre_maximal_inscriptions):
    """Cette fonction auxiliaire est appelée dans creer_creneaux. Elle a été testée et elle fonctionne."""
    for i in range(nombre_creneaux):
        creneau = CreneauHoraire(distribution=distribution, date_heure_debut=date_heure_debut, duree_en_minutes=duree,
                                 nombre_maximal_inscriptions=nombre_maximal_inscriptions)
        creneau.save()
        date_heure_debut += timedelta(minutes=duree)


@staff_member_required
def creer_creneaux(request):
    if request.method == "POST":
        form = CreneauForm(request.POST)
        if form.is_valid():
            date_heure_debut = form.cleaned_data.get('date_heure_debut')
            duree = form.cleaned_data.get('duree_en_minutes')
            nombre_maximal_inscriptions = form.cleaned_data.get('nombre_maximal_inscriptions')
            nombre_maximal_inscriptions_file_attente = form.cleaned_data.get('nombre_maximal_inscriptions_file_attente')
            nombre_creneaux = form.cleaned_data.get('nombre_creneaux')
            distribution_existante = Distribution.objects.filter(date=date_heure_debut.date())
            if not distribution_existante:
                distribution_precedente = Distribution.objects \
                    .filter(date__lt=date_heure_debut.date())
                distribution_suivante = Distribution.objects \
                    .filter(date__gt=date_heure_debut.date())
                if not distribution_precedente and not distribution_suivante:
                    distribution = Distribution(
                        date=date_heure_debut.date(),
                        nombre_maximal_inscriptions_file_attente=nombre_maximal_inscriptions_file_attente,
                        reservations_prioritaires=False)
                elif not distribution_precedente and distribution_suivante:
                    distribution = Distribution(
                        date=date_heure_debut.date(),
                        nombre_maximal_inscriptions_file_attente=nombre_maximal_inscriptions_file_attente,
                        reservations_prioritaires=False)
                    distribution.save()
                    distribution_suivante_la_plus_proche = distribution_suivante.order_by('-date').last()
                    distribution_suivante_la_plus_proche.liste_prioritaire = distribution
                    distribution_suivante_la_plus_proche.save()
                elif distribution_precedente and distribution_suivante:
                    distribution = Distribution(
                        date=date_heure_debut.date(),
                        nombre_maximal_inscriptions_file_attente=nombre_maximal_inscriptions_file_attente,
                        reservations_prioritaires=False)
                    distribution.save()
                    distribution_suivante_la_plus_proche = distribution_suivante.order_by('-date').last()
                    distribution_suivante_la_plus_proche.liste_prioritaire = distribution
                    distribution_suivante_la_plus_proche.save()
                    distribution.liste_prioritaire = distribution_precedente.order_by('-date').first()
                else:  # i.e. distribution_precedente and not distribution_suivante
                    distribution_precedente_la_plus_recente = distribution_precedente.order_by('-date').first()
                    distribution = Distribution(
                        date=date_heure_debut.date(),
                        nombre_maximal_inscriptions_file_attente=nombre_maximal_inscriptions_file_attente,
                        reservations_prioritaires=False,
                        liste_prioritaire=distribution_precedente_la_plus_recente)
                distribution.save()
            else:
                distribution = Distribution.objects.get(date=date_heure_debut.date())

            creer_creneaux_automatiquement(distribution, date_heure_debut, duree, nombre_creneaux,
                                           nombre_maximal_inscriptions)
            return reponse(request, f"""Avec ce planning, {nombre_creneaux * nombre_maximal_inscriptions} 
colis devront êtres distribués.""")
        else:
            return reponse(request, "Le formulaire est invalide.")
    else:
        form = CreneauForm()
        return render(request, 'creer_creneaux.html', {'form': form})


@staff_member_required
def planning_colis_a_livrer(request):
    liste_dates = []
    liste_nombre_colis_maximum = []
    liste_nombre_colis_total = []
    liste_nombre_colis_femme = []
    liste_nombre_colis_homme = []
    liste_nombre_maximal_beneficiaires_attente = []
    liste_nombre_beneficiaires_attente = []
    distributions = reversed(Distribution.objects.all().order_by('-date'))
    if distributions:
        for distribution in distributions:
            nombre_maximal_beneficiaires_attente = distribution.nombre_maximal_inscriptions_file_attente
            nombre_beneficiaires_attente = InscriptionAttente.objects \
                .filter(distribution=distribution) \
                .count()
            nombre_inscriptions_homme_journee = InscriptionCreneau.objects \
                .filter(creneau_horaire__distribution=distribution) \
                .filter(beneficiaire__beneficiaire__sexe='masculin') \
                .count()
            nombre_inscriptions_femme_journee = InscriptionCreneau.objects \
                .filter(creneau_horaire__distribution=distribution) \
                .filter(beneficiaire__beneficiaire__sexe='féminin') \
                .count()
            nombre_inscriptions_total_journee = nombre_inscriptions_homme_journee + nombre_inscriptions_femme_journee
            nombre_colis_maximum = 0
            for creneau in distribution.creneaux.all():
                nombre_colis_maximum += creneau.nombre_maximal_inscriptions
            liste_dates.append(distribution)
            liste_nombre_colis_maximum.append(nombre_colis_maximum)
            liste_nombre_colis_femme.append(nombre_inscriptions_femme_journee)
            liste_nombre_colis_homme.append(nombre_inscriptions_homme_journee)
            liste_nombre_colis_total.append(nombre_inscriptions_total_journee)
            liste_nombre_maximal_beneficiaires_attente.append(nombre_maximal_beneficiaires_attente)
            liste_nombre_beneficiaires_attente.append(nombre_beneficiaires_attente)
        return render(request, 'planning_colis.html', {
            'liste_date_colis': zip(liste_dates, liste_nombre_colis_maximum,
                                    liste_nombre_colis_total, liste_nombre_colis_femme,
                                    liste_nombre_colis_homme,
                                    liste_nombre_maximal_beneficiaires_attente, liste_nombre_beneficiaires_attente)})
    else:
        return reponse(request, "Aucune distribution n'a été prévue pour le moment.")

# @staff_member_required
# def compter_inscriptions(request):
#     if request.method == "POST":
#         form = DateForm(request.POST)
#         if form.is_valid():
#             date = form.cleaned_data.get('date')
#             nombre_inscriptions_homme_journee = InscriptionCreneau.objects\
#                 .filter(creneau_horaire__distribution__date=date)\
#                 .filter(beneficiaire__beneficiaire__sexe='masculin')\
#                 .count()
#             nombre_inscriptions_femme_journee = InscriptionCreneau.objects \
#                 .filter(creneau_horaire__distribution__date=date) \
#                 .filter(beneficiaire__beneficiaire__sexe='féminin') \
#                 .count()
#             if (not nombre_inscriptions_homme_journee) and (not nombre_inscriptions_femme_journee):
#                 reponse_requete = "Il n'y a aucune inscription ce jour-là."
#                 return render(request, 'reponses_requetes.html', {'reponse_requete': reponse_requete})
#             else:
#                 return reponse(request, f"""Il y a {nombre_inscriptions_femme_journee} femme(s)
# et {nombre_inscriptions_homme_journee} homme(s) inscrit(es) ce jour-là. Total : {nombre_inscriptions_homme_journee + nombre_inscriptions_femme_journee} inscription(s).""")
#         else:
#             return reponse(request, "formulaire invalide")
#     else:
#         form = DateForm()
#         return render(request, 'nombre_inscriptions.html', {'form': form})
