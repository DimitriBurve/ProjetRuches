import datetime
import json
from cgi import escape
from collections import OrderedDict
from io import BytesIO

import qrcode as qrcode
import requests
from PIL import Image
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from weasyprint import HTML
from xhtml2pdf import pisa
from xlwt import Workbook, easyxf

from ruches.models import Rucher, Colonie, Capteurs, TypeAliment, TypeNourrissement, \
    Nourrissement, FeuilleVisite
from static.fusioncharts import FusionCharts
from static.fusioncharts import FusionTable
from static.fusioncharts import TimeSeries
from .forms import *


# ensemble des vues


# vues communes
# page d'accueil
def home(request):
    return render(request, 'User/home.html')

# affichage des capteurs par ruchers
def informationsUser(request):

    # capteurs = json.load(open("fixtures/capteurs.json"))
    capteurs = Capteurs.objects.all()

    localisationsCapteurs = []

    ruchers = Rucher.objects.all()
    for r in ruchers:
        localisationsCapteurs.append(r)

    return render(request, 'User/informationsUser.html', {'ruchers': localisationsCapteurs, 'capteurs': capteurs})


# affichage des données du capteur, on appelle sur un an les données,
# on augmente l'heure de 2h puis on crée les graphes
def capteurUser(request, idCapteur, rucher, colonie):
    headers = {'Accept': 'application/json',
               'Authorization': 'key ttn-account-v2.Qtqp9AOEIJf5PYahJkhIt1mthIlpIbUz2iIj32DXTYY'}

    response = requests.get(
        "https://ruche_thib.data.thethingsnetwork.org/api/v2/query?last=365d",
        headers=headers).json()

    dataCapteur = []

    # en commentaire si pas de lien pour recuperer donnees capteurs

    for resp in response:
        if resp['device_id'] == idCapteur:
            date = resp['time']
            temp = date.split('T')
            temp2 = temp[1].split('Z')
            temp3 = temp2[0].split('.')
            dateTemp = temp3[0].split(':')
            hours = (int(dateTemp[0]) + 2) % 24
            hourF = str(hours) + ":" + dateTemp[1] + ":" + dateTemp[2]
            datef = temp[0] + " " + str(hourF)

            # temp

            dataCapteur.append([datef,
                                86,
                                resp['humidity'],
                                resp['temperature']])

    # dataCapteurJson = json.load(open("fixtures/data.json"))
    #
    # for d in dataCapteurJson:
    #     # print(d)
    #     dataCapteur.append([d['time'],
    #                         d['bat'],
    #                         d['hum'],
    #                         d['temp']])

    # print(dataCapteur)

    schema = json.load(open("fixtures/schema.json"))

    # pour recuperer derniere temperature

    derniereTemp = dataCapteur[len(dataCapteur) - 1][3]
    derniereHum = dataCapteur[len(dataCapteur) - 1][2]
    dernierBat = dataCapteur[len(dataCapteur) - 1][1]

    print(dataCapteur)
    fusionTable = FusionTable(schema, dataCapteur)

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
    fcChartTemp = FusionCharts("timeseries", "ex1", "100%", "100%", "chart-temp", "json", timeSeriesTemp)

    # graph pour humidite

    timeSeriesHum = TimeSeries(fusionTable)

    timeSeriesHum.AddAttribute("caption", """{text: 'Humidité de la ruche'}""")

    timeSeriesHum.AddAttribute("yAxis", """[{
                                                plot: 'Humidite (%)',
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

    fcChartHum = FusionCharts("timeseries", "ex2", "100%", "100%", "chart-hum", "json", timeSeriesHum)

    timeSeriesPoids = TimeSeries(fusionTable)

    timeSeriesPoids.AddAttribute("caption", """{text: 'Batterie du capteur'}""")

    timeSeriesPoids.AddAttribute("yAxis", """[{
                                                    plot: 'Batterie (%)',
                                                    title: 'Batterie',
                                                    format:{
                                                        suffix: '%',
                                                    },
                                                    style: {
                                                        title: {
                                                            'font-size': '14px'
                                                        }
                                                    },
                                                }]""")

    fcChartPoids = FusionCharts("timeseries", "ex3", "100%", "100%", "chart-poids", "json", timeSeriesPoids)

    # Load dial indicator values from simple string array# e.g.dialValues = ["52", "10", "81", "95"]
    dialValues = str(dernierBat)

    # widget data is passed to the `dataSource` parameter, as dict, in the form of key-value pairs.
    dataSource = OrderedDict()

    # The `widgetConfig` dict contains key-value pairs of data for widget attribute
    widgetConfig = OrderedDict()
    widgetConfig["caption"] = "% bat du capteur"
    widgetConfig["lowerLimit"] = "0"
    widgetConfig["upperLimit"] = "100"
    widgetConfig["showValue"] = "1"
    widgetConfig["numberSuffix"] = "%"
    widgetConfig["theme"] = "fusion"
    widgetConfig["showToolTip"] = "0"

    # The `colorData` dict contains key-value pairs of data for ColorRange of dial
    colorRangeData = OrderedDict()
    colorRangeData["color"] = [{
        "minValue": "0",
        "maxValue": "25",
        "code": "#F2726F"
    },
        {
            "minValue": "25",
            "maxValue": "50",
            "code": "#FFC533"
        },
        {
            "minValue": "50",
            "maxValue": "75",
            "code": "#FFC533"
        },
        {
            "minValue": "75",
            "maxValue": "100",
            "code": "#62B58F"
        }
    ]

    # Convert the data in the `dialData` array into a format that can be consumed by FusionCharts.
    dialData = OrderedDict()
    dialData["dial"] = []

    dataSource["chart"] = widgetConfig
    dataSource["colorRange"] = colorRangeData
    dataSource["dials"] = dialData

    # Iterate through the data in `dialValues` and insert into the `dialData["dial"]` list.
    # The data for the `dial`should be in an array wherein each element of the
    # array is a JSON object# having the `value` as keys.
    # for i in range(len(dialValues)):
    dialData["dial"].append({
        "value": dialValues
    })
    # Create an object for the angular-gauge using the FusionCharts class constructor
    # The widget data is passed to the `dataSource` parameter.

    angulargaugeWidget = FusionCharts("angulargauge", "ex4", "100%", "100%", "chart-bat", "json", dataSource)

    return render(request, 'User/capteursUser.html',
                  {'nameCapteur': idCapteur, 'graphTemp': fcChartTemp.render(), 'graphHum': fcChartHum.render(),
                   'graphPoids': fcChartPoids.render(),
                   'derniereTemp': derniereTemp, 'derniereHum': derniereHum, 'dernierBat': dernierBat,
                   'batGraph': angulargaugeWidget.render(), 'rucher': rucher, 'colonie': colonie})


def jsonView(request):
    received_json_data = json.loads(request.body)

    return render(request, 'User/testjson.html', {'test': received_json_data})


# permet de récupérer l'url de la vidéo et de l'afficher
def videoCamerasUser(request, c_id):
    col = Colonie.objects.get(pk=c_id)
    capteur = Capteurs.objects.get(colonie=col)
    return render(request, 'User/videoCamerasUser.html', {'nameCapteur': capteur.idCamera, 'rucher': col.rucher, 'colonie': col})


# permet d'ajouter le nom du capteur et l'url de la vidéo
@login_required(login_url='/auth/login/')
def ajouterCapCam(request):
    if request.method == 'POST':
        print("true post")
        capCamForm = AjouterCapCamForm(request.POST)
        if capCamForm.is_valid():
            print("true valid")
            capCamForm.save()
            return redirect('infosUser')
        else:
            print("else valid")
            form_errors = capCamForm.errors
            print(form_errors)
    else:
        print("else post")
        capCamForm = AjouterCapCamForm()
    return render(request, 'Apiculteurs/creation/createCapCam.html',
                  {'form': capCamForm})


# permet de modifer le nom du capteur et l'url de la vidéo
@login_required(login_url='/auth/login/')
def modifCapCam(request,cap_id):
    capteur = Capteurs.objects.get(pk=cap_id)
    if request.method == 'POST':
        print("true post")
        capCamForm = AjouterCapCamForm(request.POST, instance=capteur)
        if capCamForm.is_valid():
            print("true valid")
            capCamForm.save()
            return redirect('infosUser')
        else:
            print("else valid")
            form_errors = capCamForm.errors
            print(form_errors)
    else:
        print("else post")
        capCamForm = AjouterCapCamForm(instance=capteur)
    return render(request, 'Apiculteurs/modification/modifierCapCam.html',
                  {'form': capCamForm})


# permet de supprimer un capteur et caméra
@login_required(login_url='/auth/login/')
def validSupprimerCapCam(request, cap_id):
    if request.method == 'POST':
        try:
            cap = Capteurs.objects.get(pk=cap_id)
            cap.delete()
        except Capteurs.DoesNotExist:
            print("not exist")
        except Exception as e:
            print(e)

    return redirect('infosUser')

# partie apiculteur


# permet de générer un qrcode
@login_required(login_url='/auth/login/')
def render_png_to_pdf(request, c_id):
    link_to_post = "127.0.0.1:8000/afficherColonieId/{}".format(c_id)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=4,
    )
    qr.add_data(link_to_post)
    qr.make(fit=True)

    img = qr.make_image()
    img.save('static/ProjetRuches/images/qrcode.png')

    image_data = Image.open("static/ProjetRuches/images/qrcode.png")
    filename = 'static/ProjetRuches/images/qrcode.png'

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="qrcode.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawImage(filename, 0, 650)

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response


# permet d'afficher la page d'une colonie avec toutes ses infos
# on supprime les objets vide de la base de données afin de ne pas tromper l'utilisateur
# on trie tout par ordre déchronologique puis on récupère les dernières infos
@login_required(login_url='/auth/login/')
def afficherColonieId(request, c_id):
    colonie = Colonie.objects.get(pk=c_id)
    nourrissementsObj = Nourrissement.objects.all().filter(colonie=colonie)
    peseesObj = Pesee.objects.all().filter(colonie=colonie)
    recoltesObj = Recolte.objects.all().filter(colonie=colonie)
    traitementsObj = Traitement.objects.all().filter(colonie=colonie)
    feuillesObj = FeuilleVisite.objects.all().filter(colonie=colonie)

    for n in nourrissementsObj:
        if n.typeNourrissement is None:
            n.delete()

    for p in peseesObj:
        if p.poids is None:
            p.delete()

    for r in recoltesObj:
        if r.produitRecolte is None:
            r.delete()

    for t in traitementsObj:
        if t.maladie is None:
            t.delete()

    for f in feuillesObj:
        if f.notes is None:
            f.delete()

    feuillesObj = sorted(feuillesObj, key=lambda a: a.date, reverse=True)
    nourrissementsObj = sorted(nourrissementsObj, key=lambda a: a.date, reverse=True)
    traitementsObj = sorted(traitementsObj, key=lambda a: a.date, reverse=True)
    recoltesObj = sorted(recoltesObj, key=lambda a: a.date, reverse=True)
    peseesObj = sorted(peseesObj, key=lambda a: a.date, reverse=True)

    etatFeuilles = []
    feuilles = []

    for f in feuillesObj:
        feuilles.append(f)
        break

    test = False
    etat = ''

    etatReine = ''
    remarque = ''
    remarques = []

    for f in feuilles:
        etatReine = f.reinePresente

    for f in feuilles:
        if f.colonie == colonie:
            test = True
            etat = f.etatColonie
            remarque = f.notes
            break
        else:
            test = False
    if test:
        etatFeuilles.append({'colonie': colonie, 'etat': etat})
        remarques.append({'colonie': colonie, 'remarque': remarque})
    else:
        etatFeuilles.append({'colonie': colonie, 'etat': 'rien'})
        remarques.append({'colonie': colonie, 'remarque': ''})

    print(etatFeuilles)

    return render(request, 'Apiculteurs/affichage/afficherColonieId.html',
                  {'c': colonie, 'feuilles': feuillesObj, 'nourri': nourrissementsObj,
                   'trait': traitementsObj, 'recoltes': recoltesObj, 'pesees': peseesObj,
                   'etatColonie': etatFeuilles, 'etatReine': etatReine, 'remarques': remarques})


# on affiche toutes les colonies avec les infos principales le tout trié comme pour une seule colonie
# on supprime aussi les objets incomplets de la base de données
@login_required(login_url='/auth/login/')
def afficherColonies(request):
    colonies = Colonie.objects.all()

    feuillesObj = FeuilleVisite.objects.all()
    nourrissementsObj = Nourrissement.objects.all()
    peseesObj = Pesee.objects.all()
    recoltesObj = Recolte.objects.all()
    traitementsObj = Traitement.objects.all()

    for f in feuillesObj:
        if f.notes is None:
            f.delete()

    for n in nourrissementsObj:
        if n.typeNourrissement is None:
            n.delete()

    for p in peseesObj:
        if p.poids is None:
            p.delete()

    for r in recoltesObj:
        if r.produitRecolte is None:
            r.delete()

    for t in traitementsObj:
        if t.maladie is None:
            t.delete()

    etatFeuilles = []
    feuilles = []

    for c in colonies:
        feuillesObj = FeuilleVisite.objects.all().filter(colonie=c)
        feuillesObj = sorted(feuillesObj, key=lambda a: a.date, reverse=True)
        for f in feuillesObj:
            feuilles.append(f)
            break

    test = False
    etat = ''
    etat2 = ''
    remarque = ''

    etatReine = []
    remarques = []

    for c in colonies:
        for f in feuilles:

            if f.colonie == c:
                test = True
                etat = f.etatColonie
                etat2 = f.reinePresente
                remarque = f.notes
                break
            else:
                test = False
        if test:
            etatFeuilles.append({'colonie': c, 'etat': etat})
            etatReine.append({'colonie': c, 'etatReine': etat2})
            remarques.append({'colonie': c, 'remarque': remarque})
        else:
            etatFeuilles.append({'colonie': c, 'etat': 'rien'})
            etatReine.append({'colonie': c, 'etatReine': 'none'})
            remarques.append({'colonie': c, 'remarque': ''})
    print(etatFeuilles)

    colonies = sorted(colonies, key=lambda a: a.rucher.nom)

    return render(request, 'Apiculteurs/affichage/afficherColonies.html',
                  {'colonies': colonies, 'etatColonie': etatFeuilles, 'etatReine': etatReine, 'remarques': remarques})


# on affiche les colonies du rucher sélectionné comme précédemment
@login_required(login_url='/auth/login/')
def affichercoloniesRucher(request, rucher):
    colonies = Colonie.objects.all()
    etatFeuilles = []
    feuilles = []
    for c in colonies:
        feuillesObj = FeuilleVisite.objects.all().filter(colonie=c)
        feuillesObj = sorted(feuillesObj, key=lambda a: a.date, reverse=True)
        for f in feuillesObj:
            feuilles.append(f)
            break

    test = False
    etat = ''
    etat2 = ''
    remarque = ''

    etatReine = []
    remarques = []

    for c in colonies:
        for f in feuilles:

            if f.colonie == c:
                test = True
                etat = f.etatColonie
                etat2 = f.reinePresente
                remarque = f.notes
                break
            else:
                test = False
        if test:
            etatFeuilles.append({'colonie': c, 'etat': etat})
            etatReine.append({'colonie': c, 'etatReine': etat2})
            remarques.append({'colonie': c, 'remarque': remarque})
        else:
            etatFeuilles.append({'colonie': c, 'etat': 'rien'})
            etatReine.append({'colonie': c, 'etatReine': 'none'})
            remarques.append({'colonie': c, 'remarque': ''})
    print(etatFeuilles)

    return render(request, 'Apiculteurs/affichage/afficherColoniesRucher.html',
                  {'colonies': colonies, 'rucher': rucher, 'etatColonie': etatFeuilles, 'etatReine': etatReine,
                   'remarques': remarques})


# on affiche les ruchers en selectionant leurs infos à afficher
@login_required(login_url='/auth/login/')
def afficherRuchers(request):
    ruchers = Rucher.objects.all()
    colonies = Colonie.objects.all()
    for c in colonies:
        print(c)
        colonieObj = Colonie.objects.get(nom=c.nom, rucher=c.rucher)
        feuillesObj = FeuilleVisite.objects.all().filter(colonie=colonieObj)
        for f in feuillesObj:
            if f.notes is None:
                f.delete()
    nombreColoRuchers = []

    # on compte le nombre de colonies par rucher
    nombre = 0
    for r in ruchers:
        for c in colonies:
            if c.rucher == r:
                nombre += 1
        nombreColoRuchers.append({'rucher': r, 'nombre': nombre})
        nombre = 0

    print(nombreColoRuchers)

    return render(request, 'Apiculteurs/affichage/afficherRuchers.html',
                  {'ruchers': ruchers, 'nombreColo': nombreColoRuchers})


# on appelle le formulaire et on ajoute une colonie à la bdd
@login_required(login_url='/auth/login/')
def ajouterColonie(request):
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
        user = request.user
        rucheForm = RucheForm()
    return render(request, 'Apiculteurs/creation/createColonie.html',
                  {'form': rucheForm})


# on ajoute ici aussi une colonie mais avec le rucher déjà prérempli
@login_required(login_url='/auth/login/')
def ajouterColonieRucher(request, rucher):
    rucherObj = Rucher.objects.get(nom=rucher)

    if request.method == 'POST':
        print("true post")
        obj = Colonie.objects.create(rucher=rucherObj)
        rucheForm = RucheRucherForm(request.POST, instance=obj)
        if rucheForm.is_valid():
            print("true valid")
            rucheForm.save()
            coloniesObj = Colonie.objects.all()
            for c in coloniesObj:
                if c.nombre_de_cadres is None:
                    c.delete()
            return redirect('afficherColoniesRucher', rucher)
        else:
            print("else valid")
            form_errors = rucheForm.errors
            print(form_errors)
    else:
        print("else post")
        obj = Colonie.objects.create(rucher=rucherObj)
        rucheForm = RucheRucherForm(instance=obj)
    return render(request, 'Apiculteurs/creation/createColonieRucher.html',
                  {'form': rucheForm, 'rucher': rucher})


# pareil avec l'ajout de nourrissements
@login_required(login_url='/auth/login/')
def ajouterNourrissement(request, rucher, colonie):
    rucherObj = Rucher.objects.get(nom=rucher)
    colonieObj = Colonie.objects.get(rucher=rucherObj, nom=colonie)

    if request.method == 'POST':
        obj = Nourrissement.objects.create(colonie=colonieObj)
        nourrissementForm = NourrissementForm(request.POST, instance=obj)
        if nourrissementForm.is_valid():
            nourrissementForm.save()
            nourrissementsObj = Nourrissement.objects.all()
            for n in nourrissementsObj:
                if n.typeNourrissement is None:
                    n.delete()
            return redirect('afficherColonieId', colonieObj.id)
    else:
        obj = Nourrissement.objects.create(colonie=colonieObj)
        nourrissementForm = NourrissementForm(instance=obj)
    return render(request, 'Apiculteurs/creation/createNourrissement.html',
                  {'form': nourrissementForm, 'rucher': rucher, 'colonie': colonie})


@login_required(login_url='/auth/login/')
def ajouterPesee(request, rucher, colonie):
    rucherObj = Rucher.objects.get(nom=rucher)
    colonieObj = Colonie.objects.get(rucher=rucherObj, nom=colonie)

    if request.method == 'POST':
        obj = Pesee.objects.create(colonie=colonieObj)
        peseeForm = PeseeForm(request.POST, instance=obj)
        if peseeForm.is_valid():
            peseeForm.save()
            peseesObj = Pesee.objects.all()
            for p in peseesObj:
                if p.poids is None:
                    p.delete()
            return redirect('afficherColonieId', colonieObj.id)
    else:
        obj = Pesee.objects.create(colonie=colonieObj)
        peseeForm = PeseeForm(instance=obj)
    return render(request, 'Apiculteurs/creation/createPesee.html',
                  {'form': peseeForm, 'colonie': colonie, 'rucher': rucher})


@login_required(login_url='/auth/login/')
def ajouterRecolte(request, rucher, colonie):
    rucherObj = Rucher.objects.get(nom=rucher)
    colonieObj = Colonie.objects.get(rucher=rucherObj, nom=colonie)

    if request.method == 'POST':
        obj = Recolte.objects.create(colonie=colonieObj)
        recolteForm = RecolteForm(request.POST, instance=obj)
        if recolteForm.is_valid():
            recolteForm.save()
            recoltesObj = Recolte.objects.all()
            for r in recoltesObj:
                if r.produitRecolte is None:
                    r.delete()
            return redirect('afficherColonieId', colonieObj.id)
    else:
        obj = Recolte.objects.create(colonie=colonieObj)
        recolteForm = RecolteForm(instance=obj)
    return render(request, 'Apiculteurs/creation/createRecolte.html',
                  {'form': recolteForm, 'colonie': colonie, 'rucher': rucher})


@login_required(login_url='/auth/login/')
def ajouterRucher(request):
    if request.method == 'POST':
        form = RucherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('afficherRuchers')
        else:
            print(form.errors)
            # return render(request, 'Apiculteurs/creation/createRucher.html', {'form': form})

    else:
        form = RucherForm()
    return render(request, 'Apiculteurs/creation/createRucher.html',
                  {'form': form})


@login_required(login_url='/auth/login/')
def ajouterTraitement(request, rucher, colonie):
    rucherObj = Rucher.objects.get(nom=rucher)
    colonieObj = Colonie.objects.get(rucher=rucherObj, nom=colonie)
    if request.method == 'POST':
        obj = Traitement.objects.create(colonie=colonieObj)
        traitementForm = TraitementForm(request.POST, instance=obj)
        if traitementForm.is_valid():
            traitementForm.save()
            traitementsObj = Traitement.objects.all()
            for t in traitementsObj:
                if t.maladie is None:
                    t.delete()
            return redirect('afficherColonieId', colonieObj.id)
    else:
        obj = Traitement.objects.create(colonie=colonieObj)
        traitementForm = TraitementForm(instance=obj)
    return render(request, 'Apiculteurs/creation/createTraitement.html',
                  {'form': traitementForm, 'colonie': colonie, 'rucher': rucher})


# permet de modifier une colonie
@login_required(login_url='/auth/login/')
def modifierColonieId(request, c_id):
    colonie = Colonie.objects.get(pk=c_id)
    if request.method == 'POST':
        form = RucheForm(request.POST, instance=colonie)
        if form.is_valid():
            form.save()
            return redirect('afficherColonieId', c_id)
        else:
            print(form.errors)
    else:
        form = RucheForm(instance=colonie)
        return render(request, 'Apiculteurs/modification/modifierColonieId.html', {'form': form})


# permet de modifier un rucher
@login_required(login_url='/auth/login/')
def modifierRucherId(request, r_id):
    rucher = Rucher.objects.get(pk=r_id)
    if request.method == 'POST':
        form = RucherForm(request.POST, instance=rucher)
        if form.is_valid():
            form.save()
            return redirect('afficherRuchers')
    else:
        form = RucherForm(instance=rucher)
    return render(request, 'Apiculteurs/modification/modifierRucherId.html', {'form': form})


# permet de supprimer une colonie
@login_required(login_url='/auth/login/')
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


@login_required(login_url='/auth/login/')
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


@login_required(login_url='/auth/login/')
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


@login_required(login_url='/auth/login/')
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


@login_required(login_url='/auth/login/')
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


@login_required(login_url='/auth/login/')
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
@login_required(login_url='/auth/login/')
def createFeuillevisite(request, rucher, colonie, etape):
    global feuille
    rucherObj = Rucher.objects.get(nom=rucher)
    colonieObj = Colonie.objects.get(nom=colonie, rucher=rucherObj)

    if request.method == 'POST':
        if etape == 1:
            print("post 1")
            obj = FeuilleVisite.objects.create(rucher=rucherObj, colonie=colonieObj, typeRuche=colonieObj.type)
            form = FeuilleVisiteDebutForm(request.POST, instance=obj)
            if form.is_valid():
                print("1 is valid")
                form.save()
                dateForm = form.cleaned_data.get('date')
                feuillesObj = FeuilleVisite.objects.all().filter(date=dateForm)
                feuille = feuillesObj[len(feuillesObj) - 1]
                print(feuille.conditionClimatique)
                print("feuille 2: ", feuille)
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
                else:
                    print(form.errors)
            except Exception as e:
                pass
        elif etape == 5:
            try:
                form = FeuilleVisiteApresNuisibleAutreNourriApportPonctionForm(request.POST, instance=feuille)
                if form.is_valid():
                    print("5 is valid")
                    form.save()
                    etape += 1
                else:
                    print(form.errors)
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
                    etape += 1
                    print("+1")
            except Exception as e:
                pass
        if etape != 8:
            return redirect('createFeuilleVisite', rucher, colonie, etape)
        else:
            colonieObj = Colonie.objects.get(nom=colonie, rucher=rucherObj)
            feuillesObj = FeuilleVisite.objects.all().filter(colonie=colonieObj)
            for f in feuillesObj:
                if f.notes is None:
                    f.delete()
            return redirect('afficherColonieId', colonieObj.id)
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


@login_required(login_url='/auth/login/')
def feuillePDF(request, f_id):
    fPDF = FeuilleVisite.objects.get(pk=f_id)
    return render(request, 'Apiculteurs/affichage/afficherFeuillePDF.html', {'f': fPDF})


@login_required(login_url='/auth/login/')
def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))


@login_required(login_url='/auth/login/')
def export_pdf_Feuille(request, f_id):
    fPDF = FeuilleVisite.objects.get(pk=f_id)

    html_string = render_to_string('Apiculteurs/affichage/afficherFeuillePDF.html', {'f': fPDF})

    html = HTML(string=html_string)
    html.write_pdf(target='/tmp/mypdf.pdf')

    fs = FileSystemStorage('/tmp')
    with fs.open('mypdf.pdf') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        date = str(fPDF.date)
        temp = date.split(' ')
        print(temp)
        temp2 = temp[0].split('-')
        date = str("{}-{}-{}".format(temp2[2], temp2[1], temp2[0]))
        name = str("visite {}-{}-{}.pdf".format(fPDF.colonie.nom, fPDF.rucher.nom, date))
        print(name)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(name)
        return response

    return response


@login_required(login_url='/auth/login/')
def afficherRegistreColonieId(request, r_id):
    rucher = Rucher.objects.get(pk=r_id)
    colonies = Colonie.objects.all().filter(rucher=rucher)
    annees = []
    anneeToDay = datetime.date.today().year
    anneeColonieCrea = 999999
    for colonie in colonies:
        if colonie.date.year < anneeColonieCrea:
            anneeColonieCrea = colonie.date.year
    print(anneeToDay)
    print(anneeColonieCrea)
    for i in range(anneeColonieCrea, anneeToDay + 1):
        annees.append(i)
    return render(request, 'Apiculteurs/affichage/afficherRegistres.html',
                  {'annees': annees, 'r_id': r_id, 'rucher': rucher})


@login_required(login_url='/auth/login/')
def registreXLS(request, r_id, annee, user_id):
    userObj = User.objects.get(pk=user_id)
    api = Apiculteur.objects.get(user=userObj)
    feuillesVisites = FeuilleVisite.objects.all()
    feuillesVisites = sorted(feuillesVisites, key=lambda a: a.date, reverse=False)
    rucher = Rucher.objects.get(pk=r_id)
    colonies = Colonie.objects.all().filter(rucher=rucher)

    path = "/tmp/mycla.xls"

    styleT = easyxf(
        'font: height 440, bold 1; alignment: horizontal center, vertical center')
    styleP1T = easyxf('font: height 320, bold 1; alignment: vertical center')
    styleP1 = easyxf('font: height 280, bold 1; alignment: vertical center')
    styleP2 = easyxf('font: height 240; alignment: vertical center')

    classeur = Workbook()

    feuillePGarde = classeur.add_sheet("Page de garde")
    feuillePGarde.portrait = False

    feuillePGarde.write_merge(0, 2, 0, 11, str("REGISTRE D'ÉLEVAGE {}".format(annee)), styleT)

    feuillePGarde.write_merge(4, 5, 0, 3, str("Nom prénom apiculteur :"), styleP1)
    feuillePGarde.write_merge(4, 5, 4, 11, str("{} {} ".format(userObj.last_name, userObj.first_name)), styleP2)

    feuillePGarde.write_merge(6, 7, 0, 3, str("Adresse :"), styleP1)
    feuillePGarde.write_merge(6, 7, 4, 11, str(
        "{} {} - {} {}".format(api.adressePApi, api.adresseSApi, api.codePostalApi, api.villeApi)), styleP2)

    feuillePGarde.write_merge(8, 9, 0, 3, str("Rucher :"), styleP1)
    feuillePGarde.write_merge(8, 9, 4, 11, str(
        "{}".format(rucher.nom)), styleP2)

    feuillePGarde.write_merge(10, 11, 0, 3, str("N°API :"), styleP1)
    feuillePGarde.write_merge(10, 11, 4, 11, str(
        "{}".format(api.numeroApi)), styleP2)

    feuillePGarde.write_merge(12, 13, 0, 3, str("N°SIRET ou Numagrit :"), styleP1)
    feuillePGarde.write_merge(12, 13, 4, 11, str(
        "{}".format(api.numeroSiretAgrit)), styleP2)

    feuillePGarde.write_merge(15, 16, 0, 3, str("Adherent GDSA"), styleP1T)

    feuillePGarde.write_merge(17, 18, 0, 3, str("Adresse :"), styleP1)
    feuillePGarde.write_merge(17, 18, 4, 11, str(
        "{} {} - {} {}".format(api.adressePGDSA, api.adresseSGDSA, api.codePostalGDSA, api.villeGDSA)), styleP2)

    feuillePGarde.write_merge(19, 20, 0, 3, str("PSE :"), styleP1)
    feuillePGarde.write_merge(19, 20, 4, 11, str(
        "{}".format(api.PSEGDSA)), styleP2)

    feuillePGarde.write_merge(22, 23, 0, 3, str("Veterinaire"), styleP1T)

    feuillePGarde.write_merge(24, 25, 0, 3, str("Adresse :"), styleP1)
    feuillePGarde.write_merge(24, 25, 4, 11, str(
        "{} {} - {} {}".format(api.adressePVeterinaire, api.adresseSVeterinaire, api.codePostalVeterinaire,
                               api.villeVeterinaire)), styleP2)

    feuillePGarde.write_merge(26, 27, 0, 3, str("Téléphone :"), styleP1)
    feuillePGarde.write_merge(26, 27, 4, 11, str(
        "{}".format(api.telephoneVeterinaire)), styleP2)

    feuillePGarde.write_merge(29, 30, 0, 3, str("Agent sanitaire"), styleP1T)

    feuillePGarde.write_merge(31, 32, 0, 3, str("Adresse :"), styleP1)
    feuillePGarde.write_merge(31, 32, 4, 11, str(
        "{} {} - {} {}".format(api.adressePAgentSanitaire, api.adresseSAgentSanitaire, api.codePostalAgentSanitaire,
                               api.villeAgentSanitaire)), styleP2)

    feuillePGarde.write_merge(33, 34, 0, 3, str("Téléphone :"), styleP1)
    feuillePGarde.write_merge(33, 34, 4, 11, str(
        "{}".format(api.telephoneAgentSanitaire)), styleP2)

    feuillePGarde.write_merge(36, 37, 0, 3, str("Nombre de colonies au printemps :"), styleP1)
    feuillePGarde.write_merge(36, 37, 4, 11, str(
        ""), styleP2)

    feuillePGarde.write_merge(38, 39, 0, 3, str("Nombre de colonies hivernées :"), styleP1)
    feuillePGarde.write_merge(38, 39, 4, 11, str(
        ""), styleP2)

    feuilleMouv = classeur.add_sheet("Mouvements des colonies")
    feuilleMouv.portrait = False

    styleT2 = easyxf(
        'font: height 300; alignment: horizontal center, vertical center; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color gray25')
    styleP1T2 = easyxf(
        'font: height 260; alignment: horizontal center, vertical center; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color gray25')
    feuilleMouv.write_merge(0, 0, 0, 11, "Mouvements des colonies", styleT2)

    feuilleMouv.write_merge(1, 1, 0, 1, "Identification colonie", styleP1T2)
    feuilleMouv.write_merge(1, 1, 2, 3, "Date", styleP1T2)
    feuilleMouv.write_merge(1, 1, 4, 5, "Rucher d'origine", styleP1T2)
    feuilleMouv.write_merge(1, 1, 6, 7, "Rucher d'accueil", styleP1T2)
    feuilleMouv.write_merge(1, 1, 8, 11, "Remarques", styleP1T2)

    indiceMouv = 2
    for f in feuillesVisites:
        if f.destinationDeplacee != '' and f.destinationDeplacee != 'None' and f.destinationDeplacee is not None:
            print(f.destinationDeplacee)
            feuilleMouv.write_merge(indiceMouv, indiceMouv, 0, 1, str("{}".format(f.colonie.nom)))
            feuilleMouv.write_merge(indiceMouv, indiceMouv, 2, 3, str("{}".format(f.colonieDeplacee)))
            feuilleMouv.write_merge(indiceMouv, indiceMouv, 4, 5, str("{}".format(rucher.nom)))
            feuilleMouv.write_merge(indiceMouv, indiceMouv, 6, 7, str("{}".format(f.destinationDeplacee)))
            feuilleMouv.write_merge(indiceMouv, indiceMouv, 8, 11, str("{}".format(f.notes)))
            indiceMouv += 1

    feuilleOri = classeur.add_sheet("Manipulations des colonies")
    feuilleOri.portrait = False
    styleT3 = easyxf(
        'font: height 240; alignment: horizontal center, vertical center; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color gray25')
    feuilleOri.col(0).width = 3500
    feuilleOri.col(2).width = 3200
    feuilleOri.col(5).width = 3200
    styleP1T3 = easyxf(
        'font: height 160; alignment: horizontal center, vertical center; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color gray25')

    feuilleOri.write_merge(0, 0, 0, 11, "Origines colonies et manipulations", styleT3)

    feuilleOri.write_merge(1, 2, 0, 0, "Identification colonie", styleP1T3)
    feuilleOri.write_merge(1, 2, 1, 1, "Reine marquée", styleP1T3)
    feuilleOri.write_merge(1, 2, 2, 2, "Essaimage naturel", styleP1T3)

    feuilleOri.write_merge(1, 1, 3, 4, "Remérage", styleP1T3)
    feuilleOri.write_merge(2, 2, 3, 3, "Date", styleP1T3)
    feuilleOri.write_merge(2, 2, 4, 4, "Origine", styleP1T3)

    feuilleOri.write_merge(1, 2, 5, 5, "Division colonie le", styleP1T3)
    feuilleOri.write_merge(1, 2, 6, 6, "Création ruche", styleP1T3)

    feuilleOri.write_merge(1, 1, 7, 8, "Reine", styleP1T3)
    feuilleOri.write_merge(2, 2, 7, 7, "Ruche origine", styleP1T3)
    feuilleOri.write_merge(2, 2, 8, 8, "Ruche crée", styleP1T3)

    feuilleOri.write_merge(1, 1, 9, 10, "Réunion Colonies", styleP1T3)
    feuilleOri.write_merge(2, 2, 9, 9, "Date", styleP1T3)
    feuilleOri.write_merge(2, 2, 10, 10, "Ruche libre", styleP1T3)

    feuilleOri.write_merge(1, 2, 11, 11, "remarques", styleP1T3)

    indiceOri = 3
    for f in feuillesVisites:
        test = False
        if f.reineMarqueeManipulation is not None or f.essaimageNaturel is not None or f.origineRemerage is not None or f.divisionColonie is not None or f.creationRuche is not None or f.liberationRuche is not None:
            if f.reineMarqueeManipulation is not None and f.reineMarqueeManipulation != '':
                feuilleOri.write_merge(indiceOri, indiceOri, 1, 1, str("{}".format(f.reineMarqueeManipulation)))
                test = True
            if f.essaimageNaturel is not None and f.essaimageNaturel != '':
                feuilleOri.write_merge(indiceOri, indiceOri, 2, 2, str("{}".format(f.essaimageNaturel)))
                test = True
            if f.origineRemerage is not None and f.origineRemerage != '':
                feuilleOri.write_merge(indiceOri, indiceOri, 3, 3, str("{}".format(f.remerage)))
                feuilleOri.write_merge(indiceOri, indiceOri, 4, 4, str("{}".format(f.origineRemerage)))
                test = True
            if f.divisionColonie is not None and f.divisionColonie != '':
                feuilleOri.write_merge(indiceOri, indiceOri, 5, 5, str("{}".format(f.divisionColonie)))
                test = True
            if f.creationRuche is not None and f.creationRuche != '':
                feuilleOri.write_merge(indiceOri, indiceOri, 6, 6, str("{}".format(f.creationRuche)))
                test = True
            if f.liberationRuche is not None and f.liberationRuche != '':
                feuilleOri.write_merge(indiceOri, indiceOri, 9, 9, str("{}".format(f.reunionColonie)))
                feuilleOri.write_merge(indiceOri, indiceOri, 10, 10, str("{}".format(f.liberationRuche)))
                test = True
        if (f.reineMarqueeManipulation != '' or f.essaimageNaturel != '' or f.origineRemerage != '' or f.divisionColonie != '' or f.creationRuche != '' or f.liberationRuche != '') and (f.reineMarqueeManipulation is not None or f.essaimageNaturel is not None or f.origineRemerage is not None or f.divisionColonie is not None or f.creationRuche is not None or f.liberationRuche is not None):
            feuilleOri.write_merge(indiceOri, indiceOri, 0, 0, str("{}".format(f.colonie.nom)))
            feuilleOri.write_merge(indiceOri, indiceOri, 7, 7, str(""))
            feuilleOri.write_merge(indiceOri, indiceOri, 8, 8, str(""))
            feuilleOri.write_merge(indiceOri, indiceOri, 11, 11, str("{}".format(f.notes)))
            test = True
        if test is True:
            indiceOri += 1

    feuilleTraitVa = classeur.add_sheet("Traitement varroase")
    feuilleTraitVa.portrait = False

    feuilleTraitVa.col(0).width = 6000
    feuilleTraitVa.col(1).width = 3500
    feuilleTraitVa.col(2).width = 8000
    feuilleTraitVa.col(3).width = 7000
    feuilleTraitVa.col(4).width = 10000

    feuilleTraitVa.write_merge(0, 0, 0, 4, "Traitement Varroase", styleT2)

    feuilleTraitVa.write_merge(1, 1, 0, 0, "Identification colonie", styleP1T2)
    feuilleTraitVa.write_merge(1, 1, 1, 1, "Date", styleP1T2)
    feuilleTraitVa.write_merge(1, 1, 2, 2, "Méthode", styleP1T2)
    feuilleTraitVa.write_merge(1, 1, 3, 3, "Posologie", styleP1T2)
    feuilleTraitVa.write_merge(1, 1, 4, 4, "Remarques", styleP1T2)

    indiceTraitVa = 2
    for f in feuillesVisites:
        if f.maladieTraitement == 'Varroa':
            feuilleTraitVa.write_merge(indiceTraitVa, indiceTraitVa, 0, 0, str("{}".format(f.colonie.nom)))
            feuilleTraitVa.write_merge(indiceTraitVa, indiceTraitVa, 1, 1, str("{}".format(f.date)))
            feuilleTraitVa.write_merge(indiceTraitVa, indiceTraitVa, 2, 2, str("{}".format(f.methodeUtilisee)))
            feuilleTraitVa.write_merge(indiceTraitVa, indiceTraitVa, 3, 3, str(""))
            feuilleTraitVa.write_merge(indiceTraitVa, indiceTraitVa, 3, 3, str("{}").format(f.notes))
        indiceTraitVa += 1

    feuilleMal = classeur.add_sheet("Maladies et traitements")
    feuilleMal.portrait = False

    feuilleMal.col(0).width = 6000
    feuilleMal.col(1).width = 3500
    feuilleMal.col(2).width = 8000
    feuilleMal.col(3).width = 7000
    feuilleMal.col(4).width = 10000

    feuilleMal.write_merge(0, 0, 0, 4, "Maladies et traitements (à l'exception de la varroase)", styleT2)

    feuilleMal.write_merge(1, 1, 0, 0, "Identification colonie", styleP1T2)
    feuilleMal.write_merge(1, 1, 1, 1, "Date", styleP1T2)
    feuilleMal.write_merge(1, 1, 2, 2, "Maladies", styleP1T2)
    feuilleMal.write_merge(1, 1, 3, 3, "Traitements", styleP1T2)
    feuilleMal.write_merge(1, 1, 4, 4, "Remarques", styleP1T2)

    indiceMal = 2
    for f in feuillesVisites:
        if f.maladieTraitement != 'Varroa' and f.maladieTraitement != 'Rien':
            feuilleMal.write_merge(indiceMal, indiceMal, 0, 0, str("{}".format(f.colonie.nom)))
            feuilleMal.write_merge(indiceMal, indiceMal, 1, 1, str("{}".format(f.date)))
            feuilleMal.write_merge(indiceMal, indiceMal, 2, 2, str("{}".format(f.maladieTraitement)))
            feuilleMal.write_merge(indiceMal, indiceMal, 3, 3, str("{}".format(f.methodeUtilisee)))
            feuilleMal.write_merge(indiceMal, indiceMal, 4, 4, str("{}").format(f.notes))
        indiceMal += 1

    feuilleNour = classeur.add_sheet("Nourrissements")
    feuilleNour.portrait = False

    feuilleNour.col(0).width = 6000
    feuilleNour.col(1).width = 3500
    feuilleNour.col(2).width = 8000
    feuilleNour.col(3).width = 7000
    feuilleNour.col(4).width = 10000

    feuilleNour.write_merge(0, 0, 0, 4, "Nourrissements", styleT2)

    feuilleNour.write_merge(1, 1, 0, 0, "Identification colonie", styleP1T2)
    feuilleNour.write_merge(1, 1, 1, 1, "Date", styleP1T2)
    feuilleNour.write_merge(1, 1, 2, 2, "produits", styleP1T2)
    feuilleNour.write_merge(1, 1, 3, 3, "Quantité", styleP1T2)
    feuilleNour.write_merge(1, 1, 4, 4, "Remarques", styleP1T2)

    indiceNour = 2
    for f in feuillesVisites:
        if f.typeAlimentNourrissement != 'Rien':
            feuilleNour.write_merge(indiceNour, indiceNour, 0, 0, str("{}".format(f.colonie.nom)))
            feuilleNour.write_merge(indiceNour, indiceNour, 1, 1, str("{}".format(f.date)))
            feuilleNour.write_merge(indiceNour, indiceNour, 2, 2, str("{}".format(f.typeAlimentNourrissement)))
            feuilleNour.write_merge(indiceNour, indiceNour, 3, 3,
                                    str("{} {}".format(f.quantiteAlimentNourrissement, f.uniteNourrissement)))
            feuilleNour.write_merge(indiceNour, indiceNour, 4, 4, str("{}").format(f.notes))
            indiceNour += 1

    feuilleVis = classeur.add_sheet("Visite agent sanitaire")
    feuilleVis.portrait = False

    feuilleVis.col(0).width = 6000
    feuilleVis.col(1).width = 1000
    feuilleVis.col(3).width = 3500
    feuilleVis.col(4).width = 8000
    feuilleVis.col(5).width = 12000

    feuilleVis.write_merge(0, 0, 0, 5, "VISITE AGENT SANITAIRE", styleT2)

    feuilleVis.write_merge(1, 1, 0, 0, "Identification colonie", styleP1T2)
    feuilleVis.write_merge(1, 1, 1, 2, "Date", styleP1T2)
    feuilleVis.write_merge(1, 1, 3, 4, "Remarques", styleP1T2)
    for i in range(2, 37, 3):
        feuilleVis.write_merge(i, i + 2, 0, 0, "",
                               style=easyxf('borders: left thin, right thin, top thin, bottom thin;'))
        feuilleVis.write_merge(i, i + 2, 1, 2, "",
                               style=easyxf('borders: left thin, right thin, top thin, bottom thin;'))
        feuilleVis.write_merge(i, i + 2, 3, 4, "",
                               style=easyxf('borders: left thin, right thin, top thin, bottom thin;'))

    feuilleVis.write_merge(1, 1, 5, 5, "Remarques générales", styleP1T2)
    feuilleVis.write_merge(2, 8, 5, 5, "Représentant du rucher à la visite le :", style=easyxf(
        'alignment: vertical top; borders: left thin, right thin, top thin, bottom thin;'))
    feuilleVis.write_merge(9, 17, 5, 5, "Nom, date et signature agent sanitaire :", style=easyxf(
        'alignment: vertical top; borders: left thin, right thin, top thin, bottom thin;'))
    feuilleVis.write_merge(18, 37, 5, 5, "Remarques générales :", style=easyxf(
        'alignment: vertical top; borders: left thin, right thin, top thin, bottom thin;'))

    classeur.save(path)

    fs = FileSystemStorage('/tmp')
    with fs.open('mycla.xls') as xls:
        response = HttpResponse(xls, content_type='application/vnd.ms-excel')
        name = str("registre elevage {}-{}.xls".format(rucher.nom, annee))
        print(name)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(name)
        return response

    return response


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


@login_required(login_url='/auth/login/')
def monCompte(request):
    colonies = Colonie.objects.all()

    feuillesObj = FeuilleVisite.objects.all()
    nourrissementsObj = Nourrissement.objects.all()
    peseesObj = Pesee.objects.all()
    recoltesObj = Recolte.objects.all()
    traitementsObj = Traitement.objects.all()

    for f in feuillesObj:
        if f.notes is None:
            f.delete()

    for n in nourrissementsObj:
        if n.typeNourrissement is None:
            n.delete()

    for p in peseesObj:
        if p.poids is None:
            p.delete()

    for r in recoltesObj:
        if r.produitRecolte is None:
            r.delete()

    for t in traitementsObj:
        if t.maladie is None:
            t.delete()

    etatFeuilles = []
    feuilles = []
    for c in colonies:
        feuillesObj = FeuilleVisite.objects.all().filter(colonie=c)
        feuillesObj = sorted(feuillesObj, key=lambda a: a.date, reverse=True)
        for f in feuillesObj:
            feuilles.append(f)
            break

    test = False
    etat = ''
    etat2 = ''
    remarque = ''

    etatReine = []
    remarques = []

    for c in colonies:
        for f in feuilles:

            if f.colonie == c:
                test = True
                etat = f.etatColonie
                etat2 = f.reinePresente
                remarque = f.notes
                break
            else:
                test = False
        if test:
            etatFeuilles.append({'colonie': c, 'etat': etat})
            etatReine.append({'colonie': c, 'etatReine': etat2})
            remarques.append({'colonie': c, 'remarque': remarque})
        else:
            etatFeuilles.append({'colonie': c, 'etat': 'rien'})
            etatReine.append({'colonie': c, 'etatReine': 'none'})
            remarques.append({'colonie': c, 'remarque': ''})

    colonies = sorted(colonies, key=lambda a: a.rucher.nom)

    return render(request, 'registration/myAccount.html',
                  {'colonies': colonies, 'etatColonie': etatFeuilles, 'etatReine': etatReine, 'remarques': remarques})


@login_required(login_url='/auth/login/')
def detailsMonCompte(request, user_id):
    user = User.objects.get(pk=user_id)
    print(user)
    return render(request, 'registration/detailsAccount.html', {'user': user})


@login_required(login_url='/auth/login/')
def modifierMonCompte(request, user_id):
    userObj = User.objects.get(pk=user_id)
    api = Apiculteur.objects.get(user=userObj)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=userObj)
        if user_form.is_valid():
            user_form.save()
            username = user_form.cleaned_data.get('username')
            raw_password = user_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            api_form = ApiForm(request.POST, instance=api)
            if api_form.is_valid():
                api_form.save()
                login(request, user)
                return redirect('detailsMonCompte', user_id)
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
        user_form = UserForm(instance=userObj)
        api_form = ApiForm(instance=api)
        return render(request, 'registration/modifyAccount.html', {'user_form': user_form, 'api_form': api_form})


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
    colonies = Colonie.objects.all()
    etatFeuilles = []
    feuilles = []
    for c in colonies:
        feuillesObj = FeuilleVisite.objects.all().filter(colonie=c)
        feuillesObj = sorted(feuillesObj, key=lambda a: a.date, reverse=True)
        for f in feuillesObj:
            feuilles.append(f)
            break

    test = False
    etat = ''
    etat2 = ''
    remarque = ''

    etatReine = []
    remarques = []

    for c in colonies:
        for f in feuilles:

            if f.colonie == c:
                test = True
                etat = f.etatColonie
                etat2 = f.reinePresente
                remarque = f.notes
                break
            else:
                test = False
        if test:
            etatFeuilles.append({'colonie': c, 'etat': etat})
            etatReine.append({'colonie': c, 'etatReine': etat2})
            remarques.append({'colonie': c, 'remarque': remarque})
        else:
            etatFeuilles.append({'colonie': c, 'etat': 'rien'})
            etatReine.append({'colonie': c, 'etatReine': 'none'})
            remarques.append({'colonie': c, 'remarque': ''})

    colonies = sorted(colonies, key=lambda a: a.rucher.nom)

    return render(request, 'Admin/detailsUserAdmin.html',
                  {'userEdit': userEdit, 'colonies': colonies, 'etatColonie': etatFeuilles, 'etatReine': etatReine,
                   'remarques': remarques})


# partie mail
@login_required(login_url='/auth/login/')
def envoie_mail(request, user_id):
    global user, rucher
    if request.method == 'POST':
        print('post')
        email_form = EmailForm(request.POST)
        if email_form.is_valid():
            demande = email_form.cleaned_data.get('demande')
            admin = email_form.cleaned_data.get('admins')
            rucher = email_form.cleaned_data.get('ruchers')
            message = email_form.cleaned_data.get('message')
            print(demande)
            print(admin)
            print(rucher)
            user = User.objects.get(pk=user_id)
            adminObj = User.objects.get(pk=admin)
            html_content = ""
            if demande == 'transfert dans rucher(s)':
                html_content = "Bonjour,<br>" \
                               "L'apiculteur <strong>{}</strong> souhaite " \
                               "intégrer le(s) rucher(s) : <strong>{}</strong>. <br>" \
                               "Message supplémentaire : <br> {} <br>" \
                               "Cordialement,<br>" \
                               "Le site des Ruches".format(user.username, rucher, message)
            elif demande == 'Autre':
                html_content = "Bonjour,<br>" \
                               "L'apiculteur <strong>{}</strong> vous écrit ceci : <br> " \
                               "{}. <br>" \
                               "Cordialement,<br>" \
                               "Le site des Ruches".format(user.username, message)
            elif demande == 'suppression dans rucher(s)':
                html_content = "Bonjour,<br>" \
                               "L'apiculteur <strong>{}</strong> souhaite " \
                               "ne plus être dans le(s) rucher(s) : <strong>{}</strong>.<br>" \
                               "Message supplémentaire : <br> {} <br>" \
                               "Cordialement,<br>" \
                               "Le site des Ruches".format(user.username, rucher, message)
            else:
                html_content = "Bonjour,<br>" \
                               "L'apiculteur <strong>{}</strong> souhaite " \
                               "supprimer son compte.<br>" \
                               "Message supplémentaire : <br> {} <br>" \
                               "Cordialement,<br>" \
                               "Le site des Ruches".format(user.username, message)
            print(user.email)
            msg = EmailMultiAlternatives(
                demande,
                html_content,
                "projetruches@gmail.com",
                [adminObj.email],
            )
            msg.content_subtype = "html"
            msg.send()
            return redirect('home')
        else:
            print(email_form.errors)
    else:
        print("test error post")
        email_form = EmailForm()
        return render(request, 'Apiculteurs/creation/createMessage.html', {'form': email_form})


def contactAdmin(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            nom = form.cleaned_data.get('nomContact')
            prenom = form.cleaned_data.get('prenomContact')
            adresseMail = form.cleaned_data.get('adresseMailContact')
            message = form.cleaned_data.get('message')
            users = User.objects.all()
            admins = []
            for u in users:
                if u.is_staff:
                    admins.append(u.email)
            html_content = "Bonjour,<br>" \
                           "{} {} vous envoie ce message : <br> {} <br>" \
                           "Vous pouvez lui repondre à cette adrresse : {} <br>" \
                           "Cordialement,<br>" \
                           "Le site des Ruches".format(nom, prenom, message, adresseMail)
            print(admins)
            msg = EmailMultiAlternatives(
                "Demande de renseignements",
                html_content,
                "projetruches@gmail.com",
                admins,
            )
            msg.content_subtype = "html"
            msg.send()
            return redirect('home')
    else:
        form = ContactForm()
    return render(request, 'User/affichageContact.html', {'form': form})
