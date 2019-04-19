import datetime

from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Apiculteur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    adressePApi = models.CharField(max_length=200, default='')
    adresseSApi = models.CharField(max_length=200, default='', null=True)
    codePostalApi = models.CharField(max_length=5, default='')
    villeApi = models.CharField(max_length=200, default='')

    telephoneApi = models.CharField(max_length=10, default='')

    numeroApi = models.CharField(max_length=200, default='')

    numeroSiretAgrit = models.CharField(max_length=200, default='')

    adressePGDSA = models.CharField(max_length=200, default='')
    adresseSGDSA = models.CharField(max_length=200, default='', null=True)
    codePostalGDSA = models.CharField(max_length=5, default='')
    villeGDSA = models.CharField(max_length=200, default='')

    PSEGDSA = models.CharField(max_length=200, default='')

    adressePVeterinaire = models.CharField(max_length=200, default='')
    adresseSVeterinaire = models.CharField(max_length=200, default='', null=True)
    codePostalVeterinaire = models.CharField(max_length=5, default='')
    villeVeterinaire = models.CharField(max_length=200, default='')

    telephoneVeterinaire = models.CharField(max_length=200, default='')

    adressePAgentSanitaire = models.CharField(max_length=200, default='')
    adresseSAgentSanitaire = models.CharField(max_length=200, default='', null=True)
    codePostalAgentSanitaire = models.CharField(max_length=5, default='')
    villeAgentSanitaire = models.CharField(max_length=200, default='')

    telephoneAgentSanitaire = models.CharField(max_length=10, default='')

    def __str__(self):
        return self.user


class Capteurs(models.Model):
    localisation = models.CharField(max_length=200)


class Rucher(models.Model):
    nom = models.CharField(max_length=200, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    adresseP = models.CharField(max_length=200, default='')
    adresseS = models.CharField(max_length=200, null=True, default='')
    codePostal = models.CharField(max_length=5, default='')
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


class TypeNourrissement(models.Model):
    nom = models.CharField(max_length=200)

    def __str__(self):
        return self.nom


class TypeAliment(models.Model):
    nom = models.CharField(max_length=200)

    def __str__(self):
        return self.nom


class Nourrissement(models.Model):
    colonie = models.ForeignKey(Colonie, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.datetime.now)
    typeNourrissement = models.ForeignKey(TypeNourrissement, on_delete=models.CASCADE, null=True)
    typeAliment = models.ForeignKey(TypeAliment, on_delete=models.CASCADE, null=True)
    produit = models.CharField(max_length=200, null=True)
    quantite = models.DecimalField(max_digits=12, decimal_places=3, null=True)
    note = models.CharField(max_length=1024, null=True)

    def __str__(self):
        return str("{} le {}".format(self.typeNourrissement, self.date))


class Traitement(models.Model):
    api = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    colonie = models.ForeignKey(Colonie, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.datetime.now)
    maladie = models.CharField(max_length=200, null=True)
    methode = models.CharField(max_length=200, null=True)
    posologie = models.CharField(max_length=200, null=True)
    remarques = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str("Traitement sur {} par {}".format(self.colonie, self.api))


class ProduitRecolte(models.Model):
    nom = models.CharField(max_length=200)

    def __str__(self):
        return self.nom


class Recolte(models.Model):
    colonie = models.ForeignKey(Colonie, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.datetime.now)
    produitRecolte = models.ForeignKey(ProduitRecolte, on_delete=models.CASCADE, null=True)
    quantite = models.DecimalField(max_digits=12, decimal_places=3, null=True)
    note = models.CharField(max_length=1024, null=True)

    def __str__(self):
        return str("Récolte sur {} le {}".format(self.colonie, self.date))


class Pesee(models.Model):
    colonie = models.ForeignKey(Colonie, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.datetime.now)
    poids = models.DecimalField(max_digits=12, decimal_places=3, null=True)
    note = models.CharField(max_length=1024, null=True)

    def __str__(self):
        return str("Pesée sur {} le {}".format(self.colonie, self.date))


class FeuilleVisite(models.Model):
    date = models.DateField()
    rucher = models.ForeignKey(Rucher, on_delete=models.CASCADE)
    colonie = models.ForeignKey(Colonie, on_delete=models.CASCADE)
    typeRuche = models.ForeignKey(TypeRuche, on_delete=models.CASCADE)
