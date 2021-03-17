from django.shortcuts import render
from .forms import ChoixCreneauForm, AnnulerRdvForm, ProfilForm, ChoixAttenteForm, DesinscriptionListeAttenteForm
from .models import InscriptionCreneau, InscriptionAttente
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from public.views import reponse
from django.utils import timezone


def texte_mail_inscription(username, inscription):
    texte = f"""Bonjour {username},
                        
Votre inscription a bien été prise en compte. Récupatulatif: {str(inscription)}
        
Bien cordialement,
L'équipe Epicer'INT"""
    return texte


def envoyer_mail(request, objet_mail, contenu_mail):
    """Il s'agit d'une fonction auxiliaire de la focntion choisir_creneau"""
    mail_beneficiaire = str(request.user.email)
    send_mail(objet_mail, contenu_mail, 'epicerie.int@gmail.com',
              [mail_beneficiaire], fail_silently=False)


@login_required
def choisir_creneau(request):
    """décommenter la ligne envoyer_mail(request, objet_mail, contenu_mail) pour envoyer les mails automatiques de
    confirmation."""
    if request.method == "POST":
        form = ChoixCreneauForm(request.POST)
        if form.is_valid():
            choix = form.cleaned_data.get('choix')
            inscription = InscriptionCreneau(creneau_horaire=choix, beneficiaire=request.user)
            date_inscription = inscription.creneau_horaire.date_heure_debut.date()
            distribution_actuelle = choix.distribution
            if distribution_actuelle.reservations_prioritaires:  # On teste d'abord si l'utilisateur est prioritaire.

                distribution_precedente = distribution_actuelle.liste_prioritaire
                inscriptions_attente_actuelles = InscriptionAttente.objects \
                    .filter(beneficiaire=request.user) \
                    .filter(distribution=distribution_precedente)
                if inscriptions_attente_actuelles:
                    utilisateur_prioritaire = True
                else:
                    utilisateur_prioritaire = False
            else:
                utilisateur_prioritaire = True # si les inscriptions sont ouvertes pour tout le monde, tous les utilisateurs sont prioritaires.

            if not utilisateur_prioritaire:
                return reponse(request, """Les inscriptions sont actuellement réservées aux personnes qui sont inscrites sur la liste d'attente. Vous n'en faites pas partie.""")

            else:
                inscriptions_actuelles = InscriptionCreneau.objects \
                    .filter(beneficiaire=request.user) \
                    .filter(creneau_horaire__date_heure_debut__date=date_inscription) \
                    .count()
                if not inscriptions_actuelles:
                    inscription.save()
                    for inscription_attente in InscriptionAttente.objects \
                            .filter(beneficiaire=request.user) \
                            .filter(distribution__date=date_inscription):
                        inscription_attente.delete()
                    contenu_mail = texte_mail_inscription(request.user.username, inscription)
                    objet_mail = 'Inscription créneau épicerINT'
                    # envoyer_mail(request, objet_mail, contenu_mail)
                    return reponse(request, "Votre choix a bien été enregistré.")
                else:
                    return reponse(request, "Vous êtes déjà inscrit à un créneau ce jour-là")

    else:
        form = ChoixCreneauForm()
        return render(request, 'creneaux_disponibles.html', {'form': form})


def creneaux_tous_complets(distribution):
    for creneau in distribution.creneaux.all():
        if not creneau.nombre_maximal_inscriptions == creneau.inscriptions_creneaux.all().count():
            return False
    return True


@login_required
def choisir_liste_attente(request):
    """On ne peut que choisir des ditributions dont les créneaux sont tous pleins et dont
    la liste d'attente n'est pas pleine (condition codée dans le fichier forms.py).
    On vérifie maintenant que l'utilisateur ne s'est pas déjà inscrit à un créneau aujourd'hui et qu'il n'est pas
    déjà inscrit dans la liste d'attente de la distribution qu'il a choisie."""
    if request.method == "POST":
        form = ChoixAttenteForm(request.POST)
        if form.is_valid():
            choix = form.cleaned_data.get('choix')
            inscription_attente = InscriptionAttente(distribution=choix, beneficiaire=request.user)
            distribution_attente = choix
            inscription_creneau_actuelle = InscriptionCreneau.objects \
                .filter(beneficiaire=request.user) \
                .filter(creneau_horaire__distribution=distribution_attente) \
                .count()
            inscription_attente_actuelle = InscriptionAttente.objects \
                .filter(beneficiaire=request.user) \
                .filter(distribution=distribution_attente) \
                .count()
            if not inscription_creneau_actuelle and not inscription_attente_actuelle:
                if creneaux_tous_complets(distribution_attente):
                    inscription_attente.save()
                    return reponse(request, "Vous avez bien été inscrit sur la file d'attente.")
                else:
                    return reponse(request, "Il reste des créneaux libres pour cette distribution !")
            elif inscription_creneau_actuelle:
                return reponse(request,
                               "Vous êtes déjà inscrit à un créneau horaire pour récupérer un colis ce jour-là.")
            elif inscription_attente_actuelle:
                return reponse(request, "Vous êtes déjà inscrit sur cette liste d'attente.")
    else:
        form = ChoixAttenteForm()
        return render(request, 'inscription_file_attente.html', {'form': form})


def texte_mail_desinscription(username):
    texte = f"""Bonjour {username},
                
Toutes vos inscriptions aux créneaux horaires proposés par Epicer'INT ont été annulées.

Bien cordialement,
L'équipe Epicer'INT"""
    return texte


@login_required
def annuler_rdv(request):
    """Décommenter la ligne envoyer_mail(request, objet_mail, contenu_mail) pour envoyer un mail automatique."""
    rdvs_utilisateur = request.user.rdvs.all()
    if request.method == "POST":
        form = AnnulerRdvForm(request.POST)
        if form.is_valid():
            annulation_rdv = form.cleaned_data.get('annuler_mes_rdv')
            if annulation_rdv:
                objet_mail = 'Désinscription créneaux épicerINT'
                contenu_mail = texte_mail_desinscription(request.user.username)
                # envoyer_mail(request, objet_mail, contenu_mail)
                for rdv_utilisateur in rdvs_utilisateur:
                    if rdv_utilisateur.creneau_horaire.date_heure_debut > timezone.now():
                        rdv_utilisateur.delete()
                    return render(request, 'mon_rdv.html')
            else:
                return render(request, 'mon_rdv.html', {'form': form, 'rdvs_utilisateur': rdvs_utilisateur})
        else:
            return reponse(request, "Formulaire invalide. Veuillez réessayer.")
    else:
        form = AnnulerRdvForm()
        return render(request, 'mon_rdv.html', {'form': form,
                                                'rdvs_utilisateur': rdvs_utilisateur})


@login_required
def desinscription_liste_attente(request):
    inscriptions_liste_attente = request.user.inscriptions_file_attente.all()
    if request.method == "POST":
        form = DesinscriptionListeAttenteForm(request.POST)
        if form.is_valid():
            quitter_liste_attente = form.cleaned_data.get('supprimer_mon_inscription')
            if quitter_liste_attente:
                for inscription_file_attente in inscriptions_liste_attente:
                    if inscription_file_attente.distribution.date >= timezone.now().date():
                        inscription_file_attente.delete()
                    return render(request, 'mes_attentes.html')
            else:
                return render(request, 'mes_attentes.html',
                              {'form': form, 'inscriptions_liste_attente': inscriptions_liste_attente})
        else:
            return reponse(request, "Formulaire invalide. Veuillez réessayer.")
    else:
        form = DesinscriptionListeAttenteForm()
        return render(request, 'mes_attentes.html', {'form': form,
                                                     'inscriptions_liste_attente': inscriptions_liste_attente})


@login_required
def modifier_profil(request):
    """Attention, ne fonctionne pas si le bénéficaire associé à l'utilisateur n'a pas été défini"""
    nom = request.user.username
    sexe = request.user.beneficiaire.sexe
    if request.method == "POST":
        form = ProfilForm(instance=request.user.beneficiaire, data=request.POST)
        if form.is_valid():
            form.save()
            return reponse(request, "Vos modifications ont bien été prises en compte.")
        else:
            return reponse(request, "Formulaire invalide. Veuillez réessayer.")
    else:
        form = ProfilForm()
        return render(request, 'modifier_profil.html', {'form': form, 'sexe': sexe, 'nom': nom})
