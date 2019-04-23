from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from ruches.models import Colonie, Rucher, TypeRuche, FeuilleVisite, Apiculteur, Nourrissement, Traitement, \
    Recolte, Pesee


class UserForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)
    first_name = forms.CharField(max_length=254, required=True)
    last_name = forms.CharField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        help_texts = {
            'username': None,
            'password1': None,
            'password2': None,
        }


class ApiForm(forms.ModelForm):
    adresseSApi = forms.CharField(max_length=200, required=False)
    adresseSGDSA = forms.CharField(max_length=200, required=False)
    adresseSVeterinaire = forms.CharField(max_length=200, required=False)
    adresseSAgentSanitaire = forms.CharField(max_length=200, required=False)

    codePostalApi = forms.CharField(max_length=5, validators=[MinLengthValidator(5)])
    codePostalGDSA = forms.CharField(max_length=5, validators=[MinLengthValidator(5)])
    codePostalVeterinaire = forms.CharField(max_length=5, validators=[MinLengthValidator(5)])
    codePostalAgentSanitaire = forms.CharField(max_length=5, validators=[MinLengthValidator(5)])

    class Meta:
        model = Apiculteur
        fields = ['adressePApi', 'adresseSApi', 'codePostalApi', 'villeApi', 'telephoneApi', 'numeroApi',
                  'numeroSiretAgrit', 'adressePGDSA', 'adresseSGDSA', 'codePostalGDSA', 'villeGDSA', 'PSEGDSA',
                  'adressePVeterinaire', 'adresseSVeterinaire', 'codePostalVeterinaire', 'villeVeterinaire',
                  'telephoneVeterinaire', 'adressePAgentSanitaire', 'adresseSAgentSanitaire',
                  'codePostalAgentSanitaire', 'villeAgentSanitaire', 'telephoneAgentSanitaire']


class RucherForm(ModelForm):
    adresseS = forms.CharField(max_length=200, required=False)
    codePostal = forms.CharField(max_length=5, validators=[MinLengthValidator(5)])

    class Meta:
        model = Rucher
        fields = ['nom', 'user', 'adresseP', 'adresseS', 'codePostal', 'ville']


class RucheForm(ModelForm):
    remarque = forms.CharField(widget=forms.Textarea, max_length=1024, required=False)
    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )

    class Meta:
        model = Colonie
        fields = ['nom', 'rucher', 'type', 'nombre_de_cadres', 'date', 'remarque']


class NourrissementForm(ModelForm):
    note = forms.CharField(widget=forms.Textarea, max_length=1024, required=False)
    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )

    class Meta:
        model = Nourrissement
        fields = ['colonie', 'date', 'typeNourrissement', 'typeAliment', 'produit', 'quantite', 'note']


class TraitementForm(ModelForm):
    remarques = forms.CharField(widget=forms.Textarea, max_length=1024, required=False)
    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )

    class Meta:
        model = Traitement
        fields = ['api', 'colonie', 'date', 'maladie', 'methode', 'posologie', 'remarques']


class RecolteForm(ModelForm):
    note = forms.CharField(widget=forms.Textarea, max_length=1024, required=False)
    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )

    class Meta:
        model = Recolte
        fields = ['colonie', 'date', 'produitRecolte', 'quantite', 'note']


class PeseeForm(ModelForm):
    note = forms.CharField(widget=forms.Textarea, max_length=1024, required=False)
    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )

    class Meta:
        model = Pesee
        fields = ['colonie', 'date', 'poids', 'note']


class FeuilleVisiteDebutForm(ModelForm):
    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1',
        })
    )
    CONDITION_CLIMA_CHOICES = [
        ('Nuage', 'Nuage'),
        ('Soleil', 'Soleil'),
        ('Vent', 'Vent'),
    ]

    conditionClimatique = forms.CharField(
        label='Condition climatique : ',
        widget=forms.RadioSelect(choices=CONDITION_CLIMA_CHOICES, attrs={'display': 'inline-block'})
    )

    class Meta:
        model = FeuilleVisite
        fields = ['date', 'rucher', 'colonie', 'typeRuche', 'conditionClimatique']


class FeuilleVisiteAvantForm(ModelForm):

    TRAFIC_CHOICES = [
        ('Fort', 'Fort'),
        ('Normal', 'Normal'),
        ('Faible', 'Faible'),
    ]

    RENTRANT_POLLEN_CHOICES = [
        (True, 'Oui'),
        (False, 'Non'),
    ]

    MORTES_EXTERIEUR_CHOICES = [
        (True, 'Oui'),
        (False, 'Non'),
    ]

    traficEntreeRuche = forms.CharField(
        label="trafic à l'entrée de la ruche ",
        widget=forms.RadioSelect(choices=TRAFIC_CHOICES)
    )

    abeillesRentrantPollen = forms.BooleanField(
        label="Abeilles rentrant avec du pollen ",
        widget=forms.RadioSelect(choices=RENTRANT_POLLEN_CHOICES)
    )

    abeillesMortesExterieur = forms.BooleanField(
        label="Abeilles mortes à l'extérieur ",
        widget=forms.RadioSelect(choices=MORTES_EXTERIEUR_CHOICES)
    )

    class Meta:
        model = FeuilleVisite
        fields = ['traficEntreeRuche', 'abeillesRentrantPollen', 'abeillesMortesExterieur']


class FeuilleVisiteApresAttitudeForm(ModelForm):
    ATTITUDE_CHOICES = [
        ('Calmes', 'Calmes'),
        ('Nerveuses', 'Nerveuses'),
        ('Agressives', 'Agressives'),
    ]

    attitudeAbeilles = forms.CharField(
        label="Attitude des abeilles ",
        widget=forms.RadioSelect(choices=ATTITUDE_CHOICES)
    )

    class Meta:
        model = FeuilleVisite
        fields = ['attitudeAbeilles']


class FeuilleVisiteApresCadresForm(ModelForm):
    PARTITION_CHOICES = [
        (True, 'Oui'),
        (False, 'Non'),
    ]

    partitiion = forms.BooleanField(
        label="Partition ",
        widget=forms.RadioSelect(choices=PARTITION_CHOICES)
    )

    class Meta:
        model = FeuilleVisite
        fields = ['partition', 'nombreCadresColonie', 'nombreRuellesOccupees', 'nombreCadresCouvain', 'nombreCadreCireGauffreeIntroduit', 'nombreHausse']


class FeuilleVisiteApresCouvainForm(ModelForm):
    BOOLEAN_CHOICES = [
        (True, 'Oui'),
        (False, 'Non'),
    ]

    couvainCompact = forms.BooleanField(
        label="Compact",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    couvainMosaique = forms.BooleanField(
        label="Mosaïque",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    couvainChauve = forms.BooleanField(
        label="Chauve",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    presenceOeuf = forms.BooleanField(
        label="Présence d'oeufs",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    cadreCouvain = forms.BooleanField(
        label="Cadre de Couvain",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    nombreCadresOeuf = forms.IntegerField(required=False)
    nombreCadresCouvain2 = forms.IntegerField(required=False)

    class Meta:
        model = FeuilleVisite
        fields = ['couvainCompact', 'couvainMosaique', 'couvainChauve', 'presenceOeuf', 'nombreCadresOeuf', 'cadreCouvain', 'nombreCadresCouvain2']


class FeuilleVisiteApresReineForm(ModelForm):
    ORIGINE_CHOICES = [
        ('Elevage', 'Elevage'),
        ('Essaimage', 'Essaimage'),
        ('Remerrage', 'Remerrage')
    ]

    REINE_PRESENTE_CHOICES = [
        ('Vue', 'Vue'),
        ('Pas vue', 'Pas vue'),
        ('Absente', 'Absente'),
    ]

    BOOLEAN_CHOICES = [
        (True, 'Oui'),
        (False, 'Non'),
    ]

    COULEUR_REINE_MARQUEE_CHOICES = [
        ('Bleu', 'Bleu'),
        ('Blanc', 'Blanc'),
        ('Jaune', 'Jaune'),
        ('Rouge', 'Rouge'),
        ('Vert', 'Vert'),
    ]

    CELLULE_ROYALE_CHOICES = [
        ('Essaim', 'Essaim'),
        ('Sauveté', 'Sauveté'),
        ('Elevage', 'Elevage'),
    ]

    origineReine = forms.CharField(
        label="Origine reine ",
        widget=forms.RadioSelect(choices=ORIGINE_CHOICES)
    )

    reinePresente = forms.CharField(
        label="Reine présente ",
        widget=forms.RadioSelect(choices=REINE_PRESENTE_CHOICES)
    )

    reineMarquee = forms.BooleanField(
        label="Reine marquée ",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    couleurReineMarquee = forms.CharField(
        label="Couleur ",
        widget=forms.RadioSelect(choices=COULEUR_REINE_MARQUEE_CHOICES),
        required=False,
    )

    presenceCelluleRoyale = forms.BooleanField(
        label="Présence cellule Royale ",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    presenceCelluleRoyaleOrigine = forms.CharField(
        label="Oirigine cellule royale",
        widget=forms.RadioSelect(choices=CELLULE_ROYALE_CHOICES),
        required=False
    )

    class Meta:
        model = FeuilleVisite
        fields = ['origineReine', 'reinePresente', 'reineMarquee', 'couleurReineMarque', 'presenceCelluleRoyale', 'presenceCelluleRoyaleOrigine']


class FeuilleVisiteApresFauxBourdonsForm(ModelForm):
    BOOLEAN_CHOICES = [
        (True, 'Oui'),
        (False, 'Non'),
    ]

    celluleFauxBourdons = forms.BooleanField(
        label="Cellule Faux-Bourdons ",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    presenceFauxBourdons = forms.BooleanField(
        label="Présence Faux-Bourdons",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    class Meta:
        model = FeuilleVisite
        fields = ['celluleFauxBourdons', 'presenceFauxBourdons']


class FeuilleVisiteApresMaladieTraitementForm(ModelForm):
    MALADIE_CHOICES = [
        ('Rien', 'Rien'),
        ('Nosema', 'Nosema'),
        ('Couvain platré', 'Couvain platré'),
        ('Loque Européenne', 'Loque Européenne'),
        ('Loque Américaine', 'Loque Américaine'),
        ('Varroa', 'Varroa'),
        ('Autre', 'Autre'),
    ]

    maladieTraitement = forms.CharField(
        label="Maladie ",
        widget=forms.RadioSelect(choices=MALADIE_CHOICES)
    )

    methodeUtilisee = forms.CharField(widget=forms.Textarea, max_length=1024, required=False)

    class Meta:
        model = FeuilleVisite
        fields = ['maladieTraitement', 'methodeUtilisee']


class FeuilleVisiteApresNuisibleForm(ModelForm):
    NUISIBLE_CHOICES = [
        ('Rien', 'Rien'),
        ('Teigne', 'Teigne'),
        ('Scarabé', 'Scarabé'),
        ('Frelon Asiatique', 'Frelon Asiatique'),
        ('Guêpe', 'Guêpe'),
        ('Autre', 'Autre'),
    ]

    class Meta:
        model = FeuilleVisite
        fields = ['nuisible']


class FeuilleVisiteApresAutreForm(ModelForm):
    BOOLEAN_CHOICES = [
        (True, 'Oui'),
        (False, 'Non'),
    ]

    recoltePropolis = forms.BooleanField(
        label="Récolte Propolis",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    recoltePollen = forms.BooleanField(
        label="Récolte Pollen",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    class Meta:
        model = FeuilleVisite
        fields = ['recoltePropolis', 'recoltePollen']


class FeuilleVisiteApresNourrissementForm(ModelForm):
    ALIMENTS_CHOICES = [
        ('Rien', 'Rien'),
        ('Sirop', 'Sirop'),
        ('Sirop 50/50', 'Sirop 50/50'),
        ('Candy', 'Candy'),
        ('Autre', 'Autre'),
    ]

    typeAlimentNourrissement = forms.CharField(
        label="Type Aliment",
        widget=forms.RadioSelect(choices=ALIMENTS_CHOICES)
    )

    quantiteAlimentNourrissement = forms.IntegerField(required=False)

    class Meta:
        model = FeuilleVisite
        fields = ['typeAlimentNourrissement', 'quantiteAlimentNourrissement']


class FeuilleVisiteApresApportForm(ModelForm):
    APPORT_CHOICES = [
        ('Rien', 'Rien'),
        ('Miel', 'Miel'),
        ('Couvain', 'Couvain'),
        ('Abeilles', 'Abeilles'),
        ('Essaim nu ou sur cadre', 'Essaim nu ou sur cadre'),
        ('Reine', 'Reine'),
    ]

    apport = forms.CharField(
        label="Apport",
        widget=forms.RadioSelect(choices=APPORT_CHOICES)
    )

    provenanceApport = forms.CharField(required=False)

    class Meta:
        model = FeuilleVisite
        fields = ['apport', 'provenanceApport']


class FeuilleVisiteApresPonctionForm(ModelForm):
    PONCTION_CHOICES = [
        ('Rien', 'Rien'),
        ('Miel', 'Miel'),
        ('Couvain', 'Couvain'),
        ('Abeilles', 'Abeilles'),
        ('Essaim nu ou sur cadre', 'Essaim nu ou sur cadre'),
        ('Reine', 'Reine'),
    ]

    ponction = forms.CharField(
        label="Apport",
        widget=forms.RadioSelect(choices=PONCTION_CHOICES)
    )

    destinationPonction = forms.CharField(required=False)

    class Meta:
        model = FeuilleVisite
        fields = ['ponction', 'destinationPonction']


class FeuilleVisiteApresManipulationForm(ModelForm):
    COULEUR_REINE_MARQUEE_CHOICES = [
        ('Bleu', 'Bleu'),
        ('Blanc', 'Blanc'),
        ('Jaune', 'Jaune'),
        ('Rouge', 'Rouge'),
        ('Vert', 'Vert'),
    ]

    reineMarqueeManipulation = forms.CharField(
        label="Reine marquée ",
        widget=forms.RadioSelect(choices=COULEUR_REINE_MARQUEE_CHOICES),
        required=False
    )

    colonieDeplacee = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        }),
        required=False
    )

    essaimageNaturel = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker2'
        }),
        required=False
    )

    remerage = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker2'
        }),
        required=False
    )

    divisionColonie = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker2'
        }),
        required=False
    )

    reunionColonie = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker2'
        }),
        required=False
    )

    origineRemerage = forms.CharField(required=False)

    creationRuche = forms.CharField(required=False)

    liberationRuche = forms.CharField(required=False)

    class Meta:
        model = FeuilleVisite
        fields = ['reineMarqueeManipulation', 'colonieDeplacee', 'essaimageNaturel', 'remerage', 'origineRemerage', 'divisionColonie', 'creationRuche', 'reunionColonie', 'liberationRuche']


class FeuilleVisiteApresRecolteForm(ModelForm):
    nombreHausseRecolte = forms.IntegerField(required=False)

    class Meta:
        model = FeuilleVisite
        fields = ['nombreHausseRecolte']


class FeuilleVisiteApresNotesForm(ModelForm):
    notes = forms.CharField(widget=forms.Textarea, max_length=1024, required=False)

    class Meta:
        model = FeuilleVisite
        fields = ['notes']
