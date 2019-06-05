from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Rucher)
admin.site.register(models.Colonie)
admin.site.register(models.Apiculteur)
admin.site.register(models.TypeRuche)
admin.site.register(models.Nourrissement)
admin.site.register(models.TypeNourrissement)
admin.site.register(models.TypeAliment)
admin.site.register(models.Traitement)
admin.site.register(models.ProduitRecolte)
admin.site.register(models.Recolte)
admin.site.register(models.Pesee)
admin.site.register(models.FeuilleVisite)
admin.site.register(models.Capteurs)

