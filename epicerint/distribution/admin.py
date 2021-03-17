from django.contrib import admin
from .models import CreneauHoraire, InscriptionCreneau,\
    Beneficiaire, InscriptionAttente, Distribution, ColisNonRecupere
# Register your models here.

admin.site.register(CreneauHoraire)
admin.site.register(InscriptionCreneau)
admin.site.register(Beneficiaire)
admin.site.register(InscriptionAttente)
admin.site.register(Distribution)
admin.site.register(ColisNonRecupere)
