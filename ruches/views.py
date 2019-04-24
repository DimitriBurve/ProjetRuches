from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
import json
import requests
from django.contrib.auth import login, authenticate
# from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse

from .forms import *
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
# from django.core.urlresolvers import reverse
from static.fusioncharts import FusionCharts
from static.fusioncharts import FusionTable
from static.fusioncharts import TimeSeries

from ruches.models import Rucher, Colonie, Capteurs, TypeRuche, TypeAliment, TypeNourrissement, \
    Nourrissement, FeuilleVisite


# ensemble des vues


# vues communes

def home(request):
    return render(request, 'User/home.html')
    # return HttpResponse("Hello,world")


def header(apikey):
    return {'Authorization': 'Bearer {}'.format(apikey)}


def informationsUser(request):
    apikey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE1NTI0ODU5NTAsInN1YiI6IjU5MWIzZWI3NTBlMWZmMDAxYjY1ZTgxNiIsImp0aSI6Ijc1OGY1NzZkZjIyNzQxMjY3MWQyNTQyMDcyNmI4ODk4YTFiMDIyNDkifQ._pIsLsFhMHr7kkXyRRUOhuMdE08sqHuwyDm4JEVsBYY"

    r = requests.get(
        "https://api.hl2.com/panorama/v1/applications/591b3eb750e1ff001b65e816/5c2e0114bd58d4013e7919d2/alerts/5cb43b5e10cd010020e908c6",
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
    return render(request, 'Apiculteurs/affichage/afficherColonies.html', {'colonies': colonies})


def affichercoloniesRucher(request, rucher):
    colonies = Colonie.objects.all()
    return render(request, 'Apiculteurs/affichage/afficherColoniesRucher.html',
                  {'colonies': colonies, 'rucher': rucher})


def afficherNourrissement(request):
    nourrissementsObj = Nourrissement.objects.all()
    nourrissements = []
    for n in nourrissementsObj:
        if n.typeNourrissement is None:
            n.delete()
        else:
            nourrissements.append(n)
    return render(request, 'Apiculteurs/affichage/afficherNourrissements.html', {'nourrissements': nourrissements})


def afficherPesees(request):
    peseesObj = Pesee.objects.all()
    pesees = []
    for p in peseesObj:
        if p.poids is None:
            p.delete()
        else:
            pesees.append(p)
    return render(request, 'Apiculteurs/affichage/afficherPesees.html', {'pesees': pesees})


def afficherRecoltes(request):
    recoltesObj = Recolte.objects.all()
    recoltes = []
    for r in recoltesObj:
        if r.produitRecolte is None:
            r.delete()
        else:
            recoltes.append(r)
    return render(request, 'Apiculteurs/affichage/afficherRecoltes.html', {'recoltes': recoltes})


def afficherRuchers(request):
    ruchers = Rucher.objects.all()
    return render(request, 'Apiculteurs/affichage/afficherRuchers.html', {'ruchers': ruchers})


def afficherTraitement(request):
    traitementsObj = Traitement.objects.all()
    traitements = []
    for t in traitementsObj:
        if t.maladie is None:
            t.delete()
        else:
            traitements.append(t)
    return render(request, 'Apiculteurs/affichage/afficherTraitements.html', {'traitements': traitements})


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
    return render(request, 'Apiculteurs/creation/createColonie.html',
                  {'form': rucheForm, 'listeRuchers': listeRuchers, 'listeTypesRuche': listeTypesRuche})


def ajouterNourrissement(request, rucher, colonie):
    rucherObj = Rucher.objects.get(nom=rucher)
    colonieObj = Colonie.objects.get(rucher=rucherObj, nom=colonie)
    listeTypeNourrissement = TypeNourrissement.objects.all()
    listeTypeAliment = TypeAliment.objects.all()

    if request.method == 'POST':
        obj = Nourrissement.objects.create(colonie=colonieObj)
        nourrissementForm = NourrissementForm(request.POST, instance=obj)
        if nourrissementForm.is_valid():
            nourrissementForm.save()
            return redirect('afficherNourrissement')
    else:
        obj = Nourrissement.objects.create(colonie=colonieObj)
        nourrissementForm = NourrissementForm(instance=obj)
    return render(request, 'Apiculteurs/creation/createNourrissement.html',
                  {'form': nourrissementForm, 'listeTypeNourrissement': listeTypeNourrissement,
                   'listeTypeAliment': listeTypeAliment})


def ajouterPesee(request, rucher, colonie):
    rucherObj = Rucher.objects.get(nom=rucher)
    colonieObj = Colonie.objects.get(rucher=rucherObj, nom=colonie)

    if request.method == 'POST':
        obj = Pesee.objects.create(colonie=colonieObj)
        peseeForm = PeseeForm(request.POST, instance=obj)
        if peseeForm.is_valid():
            peseeForm.save()
            return redirect('afficherPesees')
    else:
        obj = Pesee.objects.create(colonie=colonieObj)
        peseeForm = PeseeForm(instance=obj)
    return render(request, 'Apiculteurs/creation/createPesee.html', {'form': peseeForm})


def ajouterRecolte(request, rucher, colonie):
    rucherObj = Rucher.objects.get(nom=rucher)
    colonieObj = Colonie.objects.get(rucher=rucherObj, nom=colonie)

    if request.method == 'POST':
        obj = Recolte.objects.create(colonie=colonieObj)
        recolteForm = RecolteForm(request.POST, instance=obj)
        if recolteForm.is_valid():
            recolteForm.save()
            return redirect('afficherRecoltes')
    else:
        obj = Recolte.objects.create(colonie=colonieObj)
        recolteForm = RecolteForm(instance=obj)
    return render(request, 'Apiculteurs/creation/createRecolte.html', {'form': recolteForm})


def ajouterRucher(request):
    if request.method == 'POST':
        form = RucherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('afficherRuchers')
        else:
            print(form.errors)
            return render(request, 'Apiculteurs/creation/createRucher.html', {'form': form})

    else:
        form = RucherForm()
    return render(request, 'Apiculteurs/creation/createRucher.html',
                  {'form': form})


def ajouterTraitement(request, rucher, colonie):
    rucherObj = Rucher.objects.get(nom=rucher)
    colonieObj = Colonie.objects.get(rucher=rucherObj, nom=colonie)
    if request.method == 'POST':
        obj = Traitement.objects.create(colonie=colonieObj)
        traitementForm = TraitementForm(request.POST, instance=obj)
        if traitementForm.is_valid():
            traitementForm.save()
            return redirect('afficherTraitements')
    else:
        obj = Traitement.objects.create(colonie=colonieObj)
        traitementForm = TraitementForm(instance=obj)
    return render(request, 'Apiculteurs/creation/createTraitement.html', {'form': traitementForm})


def modifierColonies(request):
    colonies = Colonie.objects.all()
    return render(request, 'Apiculteurs/modification/modifierColonies.html', {'colonies': colonies})


def modifierRuchers(request):
    ruchers = Rucher.objects.all()
    return render(request, 'Apiculteurs/modification/modifierRuchers.html', {'ruchers': ruchers})


def supprimerColonies(request):
    colonies = Colonie.objects.all()
    return render(request, 'Apiculteurs/suppression/supprimerColonies.html', {'colonies': colonies})


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


def validSupprimerNourrissement(request, n_id):
    if request.method == 'POST':
        try:
            n = Nourrissement.objects.get(pk=n_id)
            n.delete()
        except Nourrissement.DoesNotExist:
            print("not exist")
        except Exception as e:
            print(e)

    return redirect('afficherNourrissements')


def validSupprimerPesee(request, p_id):
    if request.method == 'POST':
        try:
            p = Pesee.objects.get(pk=p_id)
            p.delete()
        except Pesee.DoesNotExist:
            print("not exist")
        except Exception as e:
            print(e)
    return redirect('afficherPesees')


def validSupprimerRecolte(request, r_id):
    if request.method == 'POST':
        try:
            r = Recolte.objects.get(pk=r_id)
            r.delete()
        except Recolte.DoesNotExist:
            print("not exist")
        except Exception as e:
            print(e)
    return redirect('afficherRecoltes')


def supprimerRuchers(request):
    ruchers = Rucher.objects.all()
    return render(request, 'Apiculteurs/suppression/supprimerRuchers.html', {'ruchers': ruchers})


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


def validSupprimerTraitement(request, t_id):
    if request.method == 'POST':
        try:
            t = Traitement.objects.get(pk=t_id)
            t.delete()
        except Traitement.DoesNotExist:
            print("not exist")
        except Exception as e:
            print(e)

    return redirect('afficherTraitements')


# partie feuille visite
def createFeuillevisite(request, rucher, colonie, etape):
    global feuille
    rucherObj = Rucher.objects.get(nom=rucher)
    colonieObj = Colonie.objects.get(nom=colonie, rucher=rucherObj)

    # feuille = FeuilleVisite.objects.all()
    # print(feuille)
    if request.method == 'POST':
        if etape == 1:
            print("post 1")
            obj = FeuilleVisite.objects.create(rucher=rucherObj, colonie=colonieObj, typeRuche=colonieObj.type)
            form = FeuilleVisiteDebutForm(request.POST, instance=obj)
            if form.is_valid():
                print("1 is valid")
                form.save()
                dateForm = form.cleaned_data.get('date')
                feuille = FeuilleVisite.objects.get(date=dateForm, rucher=rucherObj, colonie=colonieObj)
                print("feuille 2: ", feuille)
                # obj.delete()
                etape += 1
                print("etape : ", etape)
            else:
                print(form.errors)
        elif etape == 2:
            try:
                form = FeuilleVisiteAvantForm(request.POST, instance=feuille)
                if form.is_valid():
                    print("2 is valid")
                    form.save()
                    etape += 1
                else:
                    print(form.errors)
            except Exception as e:
                pass
        elif etape == 3:
            try:
                form = FeuilleVisiteApresAttitudeCadresCouvainForm(request.POST, instance=feuille)
                if form.is_valid():
                    print("3 is valid")
                    form.save()
                    etape += 1
            except Exception as e:
                pass
        elif etape == 4:
            try:
                form = FeuilleVisiteApresReineBourdonsMaladieForm(request.POST, instance=feuille)
                if form.is_valid():
                    print("4 is valid")
                    form.save()
                    etape += 1
            except Exception as e:
                pass
        elif etape == 5:
            try:
                form = FeuilleVisiteApresNuisibleAutreNourriApportPonctionForm(request.POST, instance=feuille)
                if form.is_valid():
                    print("5 is valid")
                    form.save()
                    etape += 1
            except Exception as e:
                pass
        elif etape == 6:
            try:
                form = FeuilleVisiteApresManipulationRecolteForm(request.POST, instance=feuille)
                if form.is_valid():
                    print("6 is valid")
                    form.save()
                    etape += 1
            except Exception as e:
                pass
        elif etape == 7:
            try:
                form = FeuilleVisiteApresNotesForm(request.POST, instance=feuille)
                if form.is_valid():
                    print("7 is valid")
                    form.save()
            except Exception as e:
                pass
        return redirect('createFeuilleVisite', rucher, colonie, etape)
    else:
        form = FeuilleVisiteDebutForm()
        if etape == 1:
            print("else etape 1")
            obj = FeuilleVisite.objects.create(rucher=rucherObj, colonie=colonieObj, typeRuche=colonieObj.type)
            form = FeuilleVisiteDebutForm(instance=obj)
            obj.delete()
        elif etape == 2:
            print("else etape 2")
            form = FeuilleVisiteAvantForm()
        elif etape == 3:
            form = FeuilleVisiteApresAttitudeCadresCouvainForm()
        elif etape == 4:
            form = FeuilleVisiteApresReineBourdonsMaladieForm()
        elif etape == 5:
            form = FeuilleVisiteApresNuisibleAutreNourriApportPonctionForm()
        elif etape == 6:
            form = FeuilleVisiteApresManipulationRecolteForm()
        elif etape == 7:
            form = FeuilleVisiteApresNotesForm()

        return render(request, 'Apiculteurs/creation/createFeuilleVisite.html',
                      {'form': form, 'rucher': rucher, 'colonie': colonie, 'etape': etape})


def afficherFeuilles(request):
    feuilles = FeuilleVisite.objects.all()
    return render(request, 'Apiculteurs/affichage/afficherFeuillesVisite.html', {'feuilles': feuilles})


def feuillePDF(request, f_id):
    fPDF = FeuilleVisite.objects.get(pk=f_id)
    return render(request, 'Apiculteurs/affichage/afficherFeuillePDF.html', {'f': fPDF})


# partie inscription et mon compte

def inscription(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user_form.save()
            username = user_form.cleaned_data.get('username')
            raw_password = user_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            obj = Apiculteur.objects.create(user=user)
            api_form = ApiForm(request.POST, instance=obj)
            if api_form.is_valid():
                api_form.save()
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
            return render(request, 'registration/inscription.html',
                          {'user_form': user_form, 'errorsForm': erreurs})
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
