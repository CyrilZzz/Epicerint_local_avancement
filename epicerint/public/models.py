from django.db import models
from django.contrib import admin
from django.core.files.storage import FileSystemStorage
# Create your models here.


class Annonce(models.Model):
    titre = models.CharField(max_length=100)
    contenu = models.TextField()
    date_publication = models.DateTimeField(auto_now_add=True)
    # Inutile de préciser la date d'ajout dans l'interface d'adminisatration.
    # cela est fait automatiquement grâce à auto_now_add=True

    def __str__(self):
        return self.titre


# on créer une classe image avec une clé étrangère pour que plusieurs images
# puissent être associées à une même annonce.

class Image(models.Model):
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField()


class ImageInline(admin.TabularInline):
    model = Image


class AnnonceAdmin(admin.ModelAdmin):
    inlines = [ImageInline, ]
