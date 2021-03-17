from django.urls import path

from . import views

urlpatterns = [
    path('', views.afficher_inscriptions, name='afficher_inscriptions'),
    path('creer_creneaux', views.creer_creneaux, name='creer_creneaux'),
    path('liste_attente', views.afficher_liste_attente, name='afficher_liste_attente'),
    path('planning_livraisons', views.planning_colis_a_livrer, name='planning_livraisons'),
    # path('nombre_inscriptions', views.compter_inscriptions, name='compter_inscriptions'),
]
