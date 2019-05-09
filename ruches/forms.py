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
    users = User.objects.all()
    UsersChoices = []
    for u in users:
        UsersChoices.append((u.username, u.username))
    adresseS = forms.CharField(max_length=200, required=False)
    codePostal = forms.CharField(max_length=5, validators=[MinLengthValidator(5)])
    user = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=UsersChoices)

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

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super(RucheForm, self).__init__(*args, **kwargs)
        print('user : ', user)
        self.fields['rucher'] = forms.ChoiceField(choices=[(r.nom, r.nom) for r in Rucher.objects.filter(user=user)])

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
        fields = ['date', 'conditionClimatique']


class FeuilleVisiteAvantForm(ModelForm):
    TRAFIC_CHOICES = [
        ('Fort', 'Fort'),
        ('Normal', 'Normal'),
        ('Faible', 'Faible'),
    ]

    RENTRANT_POLLEN_CHOICES = [
        ("Oui", 'Oui'),
        ("Non", 'Non'),
    ]

    MORTES_EXTERIEUR_CHOICES = [
        ("Oui", 'Oui'),
        ("Non", 'Non'),
    ]

    traficEntreeRuche = forms.CharField(
        label="trafic à l'entrée de la ruche ",
        widget=forms.RadioSelect(choices=TRAFIC_CHOICES)
    )

    abeillesRentrantPollen = forms.CharField(
        label="Abeilles rentrant avec du pollen ",
        widget=forms.RadioSelect(choices=RENTRANT_POLLEN_CHOICES)
    )

    abeillesMortesExterieur = forms.CharField(
        label="Abeilles mortes à l'extérieur ",
        widget=forms.RadioSelect(choices=MORTES_EXTERIEUR_CHOICES)
    )

    class Meta:
        model = FeuilleVisite
        fields = ['traficEntreeRuche', 'abeillesRentrantPollen', 'abeillesMortesExterieur']


class FeuilleVisiteApresAttitudeCadresCouvainForm(ModelForm):
    ATTITUDE_CHOICES = [
        ('Calmes', 'Calmes'),
        ('Nerveuses', 'Nerveuses'),
        ('Agressives', 'Agressives'),
    ]

    BOOLEAN_CHOICES = [
        ("Oui", 'Oui'),
        ("Non", 'Non'),
    ]

    attitudeAbeilles = forms.CharField(
        label="Attitude des abeilles ",
        widget=forms.RadioSelect(choices=ATTITUDE_CHOICES)
    )

    partition = forms.CharField(
        label="Partition ",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    couvainCompact = forms.CharField(
        label="Compact",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    couvainMosaique = forms.CharField(
        label="Mosaïque",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    couvainChauve = forms.CharField(
        label="Chauve",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    presenceOeuf = forms.CharField(
        label="Présence d'oeufs",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    cadreCouvain = forms.CharField(
        label="Cadre de Couvain",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    nombreCadresOeuf = forms.IntegerField(required=False)
    nombreCadresCouvain2 = forms.IntegerField(required=False)

    class Meta:
        model = FeuilleVisite
        fields = ['attitudeAbeilles', 'partition', 'nombreCadresColonie',
                  'nombreRuellesOccupees', 'nombreCadresCouvain', 'nombreCadreCireGauffreeIntroduit',
                  'nombreHausse', 'couvainCompact', 'couvainMosaique', 'couvainChauve', 'presenceOeuf',
                  'nombreCadresOeuf', 'cadreCouvain', 'nombreCadresCouvain2']


class FeuilleVisiteApresReineBourdonsMaladieForm(ModelForm):
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
        ("Oui", 'Oui'),
        ("Non", 'Non'),
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

    MALADIE_CHOICES = [
        ('Rien', 'Rien'),
        ('Nosema', 'Nosema'),
        ('Couvain platré', 'Couvain platré'),
        ('Loque Européenne', 'Loque Européenne'),
        ('Loque Américaine', 'Loque Américaine'),
        ('Varroa', 'Varroa'),
        ('Autre', 'Autre'),
    ]

    origineReine = forms.CharField(
        label="Origine reine ",
        widget=forms.RadioSelect(choices=ORIGINE_CHOICES)
    )

    reinePresente = forms.CharField(
        label="Reine présente ",
        widget=forms.RadioSelect(choices=REINE_PRESENTE_CHOICES)
    )

    reineMarquee = forms.CharField(
        label="Reine marquée ",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    couleurReineMarque = forms.CharField(
        label="Couleur ",
        widget=forms.RadioSelect(choices=COULEUR_REINE_MARQUEE_CHOICES),
        required=False,
    )

    presenceCelluleRoyale = forms.CharField(
        label="Présence cellule Royale ",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    presenceCelluleRoyaleOrigine = forms.CharField(
        label="Oirigine cellule royale",
        widget=forms.RadioSelect(choices=CELLULE_ROYALE_CHOICES),
        required=False
    )

    celluleFauxBourdons = forms.CharField(
        label="Cellule Faux-Bourdons ",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    presenceFauxBourdons = forms.CharField(
        label="Présence Faux-Bourdons",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    maladieTraitement = forms.CharField(
        label="Maladie ",
        widget=forms.RadioSelect(choices=MALADIE_CHOICES)
    )

    methodeUtilisee = forms.CharField(widget=forms.Textarea, max_length=1024, required=False)

    class Meta:
        model = FeuilleVisite
        fields = ['origineReine', 'reinePresente', 'reineMarquee', 'couleurReineMarque',
                  'presenceCelluleRoyale', 'presenceCelluleRoyaleOrigine', 'celluleFauxBourdons',
                  'presenceFauxBourdons', 'maladieTraitement', 'methodeUtilisee']


class FeuilleVisiteApresNuisibleAutreNourriApportPonctionForm(ModelForm):
    NUISIBLE_CHOICES = [
        ('Rien', 'Rien'),
        ('Teigne', 'Teigne'),
        ('Scarabé', 'Scarabé'),
        ('Frelon Asiatique', 'Frelon Asiatique'),
        ('Guêpe', 'Guêpe'),
        ('Autre', 'Autre'),
    ]

    BOOLEAN_CHOICES = [
        ("Oui", 'Oui'),
        ("Non", 'Non'),
    ]

    ALIMENTS_CHOICES = [
        ('Rien', 'Rien'),
        ('Sirop', 'Sirop'),
        ('Sirop 50/50', 'Sirop 50/50'),
        ('Candy', 'Candy'),
        ('Autre', 'Autre'),
    ]

    APPORT_CHOICES = [
        ('Rien', 'Rien'),
        ('Miel', 'Miel'),
        ('Couvain', 'Couvain'),
        ('Abeilles', 'Abeilles'),
        ('Essaim nu ou sur cadre', 'Essaim nu ou sur cadre'),
        ('Reine', 'Reine'),
    ]

    PONCTION_CHOICES = [
        ('Rien', 'Rien'),
        ('Miel', 'Miel'),
        ('Couvain', 'Couvain'),
        ('Abeilles', 'Abeilles'),
        ('Essaim nu ou sur cadre', 'Essaim nu ou sur cadre'),
        ('Reine', 'Reine'),
    ]

    nuisible = forms.CharField(
        label="Nuisible",
        widget=forms.RadioSelect(choices=NUISIBLE_CHOICES)
    )

    recoltePropolis = forms.CharField(
        label="Récolte Propolis",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    recoltePollen = forms.CharField(
        label="Récolte Pollen",
        widget=forms.RadioSelect(choices=BOOLEAN_CHOICES)
    )

    typeAlimentNourrissement = forms.CharField(
        label="Type Aliment",
        widget=forms.RadioSelect(choices=ALIMENTS_CHOICES)
    )

    quantiteAlimentNourrissement = forms.IntegerField(required=False)

    apport = forms.CharField(
        label="Apport",
        widget=forms.RadioSelect(choices=APPORT_CHOICES)
    )

    provenanceApport = forms.CharField(required=False)

    ponction = forms.CharField(
        label="Apport",
        widget=forms.RadioSelect(choices=PONCTION_CHOICES)
    )

    destinationPonction = forms.CharField(required=False)

    class Meta:
        model = FeuilleVisite
        fields = ['nuisible', 'recoltePropolis', 'recoltePollen', 'typeAlimentNourrissement',
                  'quantiteAlimentNourrissement', 'apport', 'provenanceApport', 'ponction',
                  'destinationPonction']


class FeuilleVisiteApresManipulationRecolteForm(ModelForm):
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

    nombreHausseRecolte = forms.IntegerField(required=False)

    class Meta:
        model = FeuilleVisite
        fields = ['reineMarqueeManipulation', 'colonieDeplacee', 'essaimageNaturel', 'remerage',
                  'origineRemerage', 'divisionColonie', 'creationRuche', 'reunionColonie',
                  'liberationRuche', 'nombreHausseRecolte']


class FeuilleVisiteApresNotesForm(ModelForm):
    ETAT_CHOICES = [
        ('Normal', 'Normal'),
        ('A surveiller', 'A surveiller'),
        ('Critique', 'Critique')
    ]
    notes = forms.CharField(widget=forms.Textarea, max_length=1024, required=False)
    etatColonie = forms.CharField(widget=forms.RadioSelect(choices=ETAT_CHOICES))

    class Meta:
        model = FeuilleVisite
        fields = ['notes', 'etatColonie']
