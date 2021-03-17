from django.contrib import admin
from .models import Annonce, AnnonceAdmin

admin.site.register(Annonce, AnnonceAdmin)
