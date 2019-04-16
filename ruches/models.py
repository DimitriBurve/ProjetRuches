import datetime

from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Capteurs(models.Model):
    localisation = models.CharField(max_length=200)


class Rucher(models.Model):
    nom = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    adresseP = models.CharField(max_length=200, default='')
    adresseS = models.CharField(max_length=200, null=True, default='')
    codePostal = models.CharField(max_length=6, default='')
    ville = models.CharField(max_length=200, default='')

    def __str__(self):
        return self.nom


class TypeRuche(models.Model):
    nom = models.CharField(max_length=200)

    def __str__(self):
        return self.nom


class Colonie(models.Model):
    nom = models.CharField(max_length=200)
    rucher = models.ForeignKey(Rucher, on_delete=models.CASCADE)
    type = models.ForeignKey(TypeRuche, on_delete=models.CASCADE)
    nombre_de_cadres = models.CharField(max_length=20)
    date = models.DateTimeField(default=datetime.datetime.now)
    remarque = models.CharField(max_length=1024, null=True)

    def __str__(self):
        return self.nom


class FeuilleVisite(models.Model):
    date = models.DateField()
    rucher = models.ForeignKey(Rucher, on_delete=models.CASCADE)
    colonie = models.ForeignKey(Colonie, on_delete=models.CASCADE)
    typeRuche = models.ForeignKey(TypeRuche, on_delete=models.CASCADE)

