from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from ruches.models import Colonie, Rucher, TypeRuche, FeuilleVisite


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
