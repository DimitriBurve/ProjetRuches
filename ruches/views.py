from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
import json
import requests
from django.contrib.auth import login, authenticate
# from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django.contrib.auth.models import User

from static.fusioncharts import FusionCharts
from static.fusioncharts import FusionTable
from static.fusioncharts import TimeSeries

from ruches.models import Rucher, Colonie, Capteurs, TypeRuche, FeuilleVisite


# ensemble des vues


# vues communes

def home(request):
    return render(request, 'User/home.html')
    # return HttpResponse("Hello,world")


def header(apikey):
    return {'Authorization': 'Bearer {}'.format(apikey)}


def informationsUser(request):
    apikey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE1NTI0ODU5NTAsInN1YiI6IjU5MWIzZWI3NTBlMWZmMDAxYjY1ZTgxNiIsImp0aSI6Ijc1OGY1NzZkZjIyNzQxMjY3MWQyNTQyMDcyNmI4ODk4YTFiMDIyNDkifQ._pIsLsFhMHr7kkXyRRUOhuMdE08sqHuwyDm4JEVsBYY"

    r = requests.get("https://api.hl2.com/panorama/v1/applications/591b3eb750e1ff001b65e816/5c2e0114bd58d4013e7919d2/alerts/5cb43b5e10cd010020e908c6",
                     headers=header(apikey)).text
    print(r)
    # response = requete.urlopen("https://github.com/timeline.json")
    # data_test = json.load(response)

    # print(data_test)

    localisationsCapteurs = []

    with open('fixtures/Capteurs.json') as json_data:
        data_dict = json.load(json_data)

    # print(len(data_dict))
    for i in range(0, len(data_dict)):
        # print(data_dict[i]["fields"]["localisation"])
        localisationsCapteurs.append(data_dict[i]["fields"]["localisation"])

    # data_str = json.dumps(data_dict)
    # print(data_str)
    # data = json.load(open("/fixtures/Capteurs.json"))
    # capteurs = Capteurs.objects.all()

    return render(request, 'User/informationsUser.html', {'capteurs': localisationsCapteurs})


def capteurUser(request, nameCapteur):
    data = requests.get(
        'https://s3.eu-central-1.amazonaws.com/fusion.store/ft/data/adding-a-reference-line-data.json').text
    schema = requests.get(
        'https://s3.eu-central-1.amazonaws.com/fusion.store/ft/schema/adding-a-reference-line-schema.json').text

    # pour recuperer derniere temperature

    data2 = requests.get(
        'https://s3.eu-central-1.amazonaws.com/fusion.store/ft/data/adding-a-reference-line-data.json').json()

    derniereTemp = data2[len(data2) - 1][5]
    derniereHum = data2[len(data2) - 1][1]
    dernierPoids = data2[len(data2) - 1][3]

    fusionTable = FusionTable(schema, data)

    # graph pour temperatures

    timeSeriesTemp = TimeSeries(fusionTable)

    timeSeriesTemp.AddAttribute("caption", """{text: 'Températures de la ruche'}""")

    timeSeriesTemp.AddAttribute("yAxis", """[{
                                                plot: 'Temperature',
                                                title: 'Temperature',
                                                format:{
                                                suffix: '°C',
                                                },
                                                style: {
                                                title: {
                                                    'font-size': '14px'
                                                }
                                                },
                                                referenceLine: [{
                                                label: 'Temperature idéale',
                                                value: '10'
                                                }]
                                            }]""")

    # Create an object for the chart using the FusionCharts class constructor
    fcChartTemp = FusionCharts("timeseries", "ex1", 700, 450, "chart-temp", "json", timeSeriesTemp)

    # graph pour humidite

    timeSeriesHum = TimeSeries(fusionTable)

    timeSeriesHum.AddAttribute("caption", """{text: 'Humidité de la ruche'}""")

    timeSeriesHum.AddAttribute("yAxis", """[{
                                                plot: 'Carbon mono-oxide (mg/m^3)',
                                                title: 'Humidité',
                                                format:{
                                                    suffix: '%',
                                                },
                                                style: {
                                                    title: {
                                                        'font-size': '14px'
                                                    }
                                                },
                                                referenceLine: [{
                                                label: 'Humidité idéale',
                                                value: '5'
                                                }]
                                            }]""")

    fcChartHum = FusionCharts("timeseries", "ex2", 700, 450, "chart-hum", "json", timeSeriesHum)

    timeSeriesPoids = TimeSeries(fusionTable)

    timeSeriesPoids.AddAttribute("caption", """{text: 'Poids de la ruche'}""")

    timeSeriesPoids.AddAttribute("yAxis", """[{
                                                    plot: 'Benzene',
                                                    title: 'Poids',
                                                    format:{
                                                        suffix: 'kg',
                                                    },
                                                    style: {
                                                        title: {
                                                            'font-size': '14px'
                                                        }
                                                    },
                                                }]""")

    fcChartPoids = FusionCharts("timeseries", "ex3", 700, 450, "chart-poids", "json", timeSeriesPoids)

    return render(request, 'User/capteursUser.html',
                  {'nameCapteur': nameCapteur, 'graphTemp': fcChartTemp.render(), 'graphHum': fcChartHum.render(),
                   'graphPoids': fcChartPoids.render(),
                   'derniereTemp': derniereTemp, 'derniereHum': derniereHum, 'dernierPoids': dernierPoids})


def camerasUser(request):
    localisationsCapteurs = []

    with open('fixtures/Capteurs.json') as json_data:
        data_dict = json.load(json_data)

    for i in range(0, len(data_dict)):
        localisationsCapteurs.append(data_dict[i]["fields"]["localisation"])

    return render(request, 'User/camerasUser.html', {"capteurs": localisationsCapteurs})


def videoCamerasUser(request, nameCapteur):
    return render(request, 'User/videoCamerasUser.html', {'nameCapteur': nameCapteur})


# partie apiculteur

def afficherColonies(request):
    colonies = Colonie.objects.all()
    return render(request, 'Apiculteurs/afficherColonies.html', {'colonies': colonies})


def affichercoloniesRucher(request, rucher):
    colonies = Colonie.objects.all()
    return render(request, 'Apiculteurs/afficherColoniesRucher.html', {'colonies': colonies, 'rucher': rucher})


def afficherRuchers(request):
    ruchers = Rucher.objects.all()
    return render(request, 'Apiculteurs/afficherRuchers.html', {'ruchers': ruchers})


def ajouterColonie(request):
    listeRuchers = Rucher.objects.all()
    listeTypesRuche = TypeRuche.objects.all()
    if request.method == 'POST':
        print("true post")
        rucheForm = RucheForm(request.POST)
        if rucheForm.is_valid():
            print("true valid")
            rucheForm.save()
            return redirect('afficherColonies')
        else:
            print("else valid")
            form_errors = rucheForm.errors
            print(form_errors)
    else:
        print("else post")
        rucheForm = RucheForm()
    return render(request, 'Apiculteurs/createColonie.html',
                  {'form': rucheForm, 'listeRuchers': listeRuchers, 'listeTypesRuche': listeTypesRuche})


def ajouterRucher(request):
    if request.method == 'POST':
        form = RucherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('afficherRuchers')
        else:
            print(form.errors)
            return render(request, 'Apiculteurs/createRucher.html', {'form': form})

    else:
        form = RucherForm()
    return render(request, 'Apiculteurs/createRucher.html',
                  {'form': form})


def modifierColonies(request):
    colonies = Colonie.objects.all()
    return render(request, 'Apiculteurs/modifierColonies.html', {'colonies': colonies})


def modifierRuchers(request):
    ruchers = Rucher.objects.all()
    return render(request, 'Apiculteurs/modifierRuchers.html', {'ruchers': ruchers})


def supprimerColonies(request):
    colonies = Colonie.objects.all()
    return render(request, 'Apiculteurs/supprimerColonies.html', {'colonies': colonies})


def validSupprimerColonie(request, colonie, rucher):
    if request.method == 'POST':
        print(rucher)
        try:
            u = Colonie.objects.filter(nom=colonie)
            # u = u.filter(rucher=rucher)
            for colonie in u:
                print("colonie : ", colonie.rucher)
                if colonie.rucher.nom == rucher:
                    print("test")
                    colonie.delete()
                    break
            # u.delete()
        except Rucher.DoesNotExist:
            print("not exist")
        except Exception as e:
            print("exception : ", e)

        # return render(request, 'Admin/showsUsersAdmin.html', {'users': users})

    return redirect('afficherColonies')


def supprimerRuchers(request):
    ruchers = Rucher.objects.all()
    return render(request, 'Apiculteurs/supprimerRuchers.html', {'ruchers': ruchers})


def validSupprimerRucher(request, rucher):
    if request.method == 'POST':
        try:
            u = Rucher.objects.get(nom=rucher)
            print("rucher : ", u)
            u.delete()
        except Rucher.DoesNotExist:
            print("not exist")
        except Exception as e:
            print("exception : ", e)

        # return render(request, 'Admin/showsUsersAdmin.html', {'users': users})

    return redirect('afficherRuchers')


# partie inscription et mon compte

def inscription(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        api_form = ApiForm(request.POST)
        if user_form.is_valid() and api_form.is_valid():
            user_form.save()
            api_form.save()
            username = user_form.cleaned_data.get('username')
            raw_password = user_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
        else:
            print("test invalid form")
            form_errors = user_form.errors
            print(form_errors)
            erreurs = []
            for error in form_errors:
                if error == "password2":
                    erreurs.append("Erreur mot de passe")
                if error == "username":
                    erreurs.append("Erreur Username")
            return render(request, 'registration/inscription.html', {'user_form': user_form, 'api_form':api_form,'errorsForm': erreurs})
    else:
        print("test error post")
        user_form = UserForm()
        api_form = ApiForm()
    return render(request, 'registration/inscription.html', {'user_form': user_form, 'api_form': api_form})


def monCompte(request):
    return render(request, 'registration/myAccount.html')


def detailsMonCompte(request, user_id):
    user = User.objects.get(pk=user_id)
    print(user)
    return render(request, 'registration/detailsAccount.html', {'user': user})


def modifierMonCompte(request):
    return render(request, 'registration/modifyAccount.html')


# partie admin

@staff_member_required
def showUsersAdmin(request):
    users = User.objects.all()
    return render(request, 'Admin/showsUsersAdmin.html', {'users': users})


@staff_member_required
def deleteUserAdmin(request, username):
    if request.method == 'POST':
        try:
            u = User.objects.get(username=username)
            print("user : ", u)
            u.delete()
        except User.DoesNotExist:
            print("not exist")
        except Exception as e:
            print("exception : ", e)

        # return render(request, 'Admin/showsUsersAdmin.html', {'users': users})

    return redirect('showUsersAdmin')


@staff_member_required
def detailsUserAdmin(request, username):
    userEdit = User.objects.get(username=username)
    return render(request, 'Admin/detailsUserAdmin.html', {'userEdit': userEdit})
