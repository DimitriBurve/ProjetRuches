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
        return str("{}".format(self.user))


class Capteurs(models.Model):
    localisation = models.CharField(max_length=200)


class Rucher(models.Model):
    nom = models.CharField(max_length=200, unique=True)
    user = models.ManyToManyField(User, null=True)
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
    nombre_de_cadres = models.IntegerField()
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
    date = models.DateTimeField(default=datetime.datetime.now)
    rucher = models.ForeignKey(Rucher, on_delete=models.CASCADE)
    colonie = models.ForeignKey(Colonie, on_delete=models.CASCADE)
    typeRuche = models.ForeignKey(TypeRuche, on_delete=models.CASCADE)
    conditionClimatique = models.CharField(max_length=200, null=True)

    traficEntreeRuche = models.CharField(max_length=200, null=True)
    abeillesRentrantPollen = models.CharField(max_length=200, null=True)
    abeillesMortesExterieur = models.CharField(max_length=200, null=True)

    attitudeAbeilles = models.CharField(max_length=200, null=True)

    partition = models.CharField(max_length=200, null=True)

    nombreCadresColonie = models.IntegerField(null=True)
    nombreRuellesOccupees = models.IntegerField(null=True)
    nombreCadresCouvain = models.IntegerField(null=True)
    nombreCadreCireGauffreeIntroduit = models.IntegerField(null=True)
    nombreHausse = models.IntegerField(null=True)

    couvainCompact = models.CharField(max_length=200, null=True)
    couvainMosaique = models.CharField(max_length=200, null=True)
    couvainChauve = models.CharField(max_length=200, null=True)
    presenceOeuf = models.CharField(max_length=200, null=True)
    nombreCadresOeuf = models.IntegerField(null=True)
    cadreCouvain = models.CharField(max_length=200, null=True)
    nombreCadresCouvain2 = models.IntegerField(null=True)

    origineReine = models.CharField(max_length=200, null=True)
    reinePresente = models.CharField(max_length=200, null=True)
    reineMarquee = models.CharField(max_length=200, null=True)
    couleurReineMarque = models.CharField(max_length=200, null=True)
    presenceCelluleRoyale = models.CharField(max_length=200, null=True)
    presenceCelluleRoyaleOrigine = models.CharField(max_length=200, null=True)

    celluleFauxBourdons = models.CharField(max_length=200, null=True)
    presenceFauxBourdons = models.CharField(max_length=200, null=True)

    maladieTraitement = models.CharField(max_length=200, null=True)
    methodeUtilisee = models.CharField(max_length=1024, null=True)

    nuisible = models.CharField(max_length=200, null=True)

    recoltePropolis = models.CharField(max_length=200, null=True)
    recoltePollen = models.CharField(max_length=200, null=True)

    typeAlimentNourrissement = models.CharField(max_length=200, null=True)
    quantiteAlimentNourrissement = models.DecimalField(max_digits=12, decimal_places=3, null=True)
    uniteNourrissement = models.CharField(max_length=2, null=True)

    apport = models.CharField(max_length=200, null=True)
    provenanceApport = models.CharField(max_length=200, null=True)

    ponction = models.CharField(max_length=200, null=True)
    destinationPonction = models.CharField(max_length=200, null=True)

    reineMarqueeManipulation = models.CharField(max_length=200, null=True)
    colonieDeplacee = models.DateTimeField(null=True)
    destinationDeplacee = models.CharField(max_length=200, null=True)
    essaimageNaturel = models.DateTimeField(null=True)
    remerage = models.DateTimeField(null=True)
    origineRemerage = models.CharField(max_length=200, null=True)
    divisionColonie = models.DateTimeField(null=True)
    creationRuche = models.CharField(max_length=200, null=True)
    reunionColonie = models.DateTimeField(null=True)
    liberationRuche = models.CharField(max_length=200, null=True)

    nombreHausseRecolte = models.IntegerField(null=True)

    notes = models.CharField(max_length=1024, null=True)
    etatColonie = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str("Visite sur {} {} {} le {}".format(self.rucher, self.colonie, self.typeRuche, self.date))
