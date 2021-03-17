from django.urls import path

from . import views

urlpatterns = [
    path('', views.choisir_creneau, name='choisir_creneau'),
    path('inscription_file_attente', views.choisir_liste_attente, name='choisir_liste_attente'),
    path('mes_rdv', views.annuler_rdv, name='annuler_rdv'),
    path('modifier_profil', views.modifier_profil, name='modifier_profil'),
    path('mes_attentes', views.desinscription_liste_attente, name='mes_attentes')
]
