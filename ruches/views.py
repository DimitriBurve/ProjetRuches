import subprocess
from collections import OrderedDict

import qrcode as qrcode
from PIL import Image
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import render, redirect
import json
import requests
from django.contrib.auth import login, authenticate
# from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas

from .forms import *
from django.contrib.auth.models import User
# from django.core.urlresolvers import reverse
from static.fusioncharts import FusionCharts
from static.fusioncharts import FusionTable
from static.fusioncharts import TimeSeries

from ruches.models import Rucher, Colonie, Capteurs, TypeRuche, TypeAliment, TypeNourrissement, \
    Nourrissement, FeuilleVisite

from io import StringIO, BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from cgi import escape
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string

from weasyprint import HTML

import pyqrcode


# import pypng

# ensemble des vues


# vues communes

def home(request):
    return render(request, 'User/home.html')
    # return HttpResponse("Hello,world")


def header(apikey):
    return {'Authorization': 'Bearer {}'.format(apikey)}


def informationsUser(request):
    #     apikey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE1NTI0ODU5NTAsInN1YiI6IjU5MWIzZWI3NTBlMWZmMDAxYjY1ZTgxNiIsImp0aSI6Ijc1OGY1NzZkZjIyNzQxMjY3MWQyNTQyMDcyNmI4ODk4YTFiMDIyNDkifQ._pIsLsFhMHr7kkXyRRUOhuMdE08sqHuwyDm4JEVsBYY"
    #
    #     res = requests.get(
    #         "https://api.hl2.com/panorama/v1/applications/591b3eb750e1ff001b65e816/5c2e0114bd58d4013e7919d2/devices",
    #         headers=header(apikey)).json()
    #     print(res)
    #

    capteurs = json.load(open("fixtures/capteurs.json"))
    for cap in capteurs:
        print(cap['rucher'])

    localisationsCapteurs = []

    ruchers = Rucher.objects.all()
    for r in ruchers:
        localisationsCapteurs.append(r)

    #     coloniesObj = Colonie.objects.all()
    #
    #     capteurs = []
    #
    #     for rep in res:
    #         nom = rep["name"]
    #         temp = nom.split(" ")
    #         for w in temp:
    #             for c in coloniesObj:
    #                 for l in localisationsCapteurs:
    #                     capteurs.append({'loc': l, 'id': rep['id'], 'name': rep['name']})
    #                     # if w == l and c.rucher == l:
    #                     # print("true, ", l)
    #                 break
    #             break
    #
    #     print(capteurs)
    #
    #     # data_str = json.dumps(data_dict)
    #     # print(data_str)

    return render(request, 'User/informationsUser.html', {'ruchers': localisationsCapteurs, 'capteurs': capteurs})


def capteurUser(request, idCapteur):
    # apikey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE1NTI0ODU5NTAsInN1YiI6IjU5MWIzZWI3NTBlMWZmMDAxYjY1ZTgxNiIsImp0aSI6Ijc1OGY1NzZkZjIyNzQxMjY3MWQyNTQyMDcyNmI4ODk4YTFiMDIyNDkifQ._pIsLsFhMHr7kkXyRRUOhuMdE08sqHuwyDm4JEVsBYY"
    #
    # res = requests.get(
    #     "https://api.hl2.com/panorama/v1/applications/591b3eb750e1ff001b65e816/5c2e0114bd58d4013e7919d2/devices",
    #     headers=header(apikey)).json()
    #
    # url = "https://api.hl2.com/panorama/v1/applications/591b3eb750e1ff001b65e816/5c2e0114bd58d4013e7919d2/hooks/5cc6f3f3619c67001743f7df/deliveries"
    #
    # response = requests.get(url, headers=header(apikey)).json()
    # # payload = ""
    # # headers = {
    # #     'Authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE1NTI0ODU5NTAsInN1YiI6IjU5MWIzZWI3NTBlMWZmMDAxYjY1ZTgxNiIsImp0aSI6Ijc1OGY1NzZkZjIyNzQxMjY3MWQyNTQyMDcyNmI4ODk4YTFiMDIyNDkifQ._pIsLsFhMHr7kkXyRRUOhuMdE08sqHuwyDm4JEVsBYY",
    # #     'cache-control': "no-cache",
    # #     'Postman-Token': "24bd5fd8-7fb6-47b8-9159-c288506650d5"
    # # }
    #
    # # response = requests.request("GET", url, data=payload, headers=headers).json()
    #
    dataCapteur = []
    #
    # for resp in response:
    #     # print(resp['deviceId'])
    #     date = resp['createdAt']
    #     temp = date.split('T')
    #     temp2 = temp[1].split('Z')
    #     temp3 = temp2[0].split('.')
    #     dateTemp = temp3[0].split(':')
    #     hours = (int(dateTemp[0]) + 2) % 24
    #     hourF = str(hours) + ":" + dateTemp[1] + ":" + dateTemp[2]
    #     datef = temp[0] + " " + str(hourF)
    #     if resp['deviceId'] == idCapteur and idCapteur == "591b3f0c50e1ff001b65e817":
    #         dataCapteur.append([datef,
    #                             resp['request']['payload']['record']['data']['vbat'],
    #                             resp['request']['payload']['record']['data']['humidity'],
    #                             resp['request']['payload']['record']['data']['temperature']])
    #     elif resp['deviceId'] == idCapteur:
    #         print("test")
    #         dataCapteur.append([datef,
    #                             resp['request']['payload']['record']['data']['battery_2'],
    #                             resp['request']['payload']['record']['data']['humidite_2'],
    #                             resp['request']['payload']['record']['data']['temperature_2']])
    #

    dataCapteurJson = json.load(open("fixtures/data.json"))

    for d in dataCapteurJson:
        # print(d)
        dataCapteur.append([d['time'],
                            d['bat'],
                            d['hum'],
                            d['temp']])

    # print(dataCapteur)

    data = requests.get(
        'https://s3.eu-central-1.amazonaws.com/fusion.store/ft/data/adding-a-reference-line-data.json').text
    schema = requests.get(
        'https://s3.eu-central-1.amazonaws.com/fusion.store/ft/schema/adding-a-reference-line-schema.json').text

    schema2 = json.load(open("fixtures/schema.json"))

    # pour recuperer derniere temperature

    data2 = requests.get(
        'https://s3.eu-central-1.amazonaws.com/fusion.store/ft/data/adding-a-reference-line-data.json').json()

    derniereTemp = dataCapteurJson[len(dataCapteurJson) - 1]['temp']
    derniereHum = dataCapteurJson[len(dataCapteurJson) - 1]['hum']
    dernierBat = dataCapteurJson[len(dataCapteurJson) - 1]['bat']

    fusionTable = FusionTable(schema2, dataCapteur)

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
                   'batGraph': angulargaugeWidget.render()})


def jsonView(request):
    received_json_data = json.loads(request.body)

    return render(request, 'User/testjson.html', {'test': received_json_data})


def camerasUser(request):
    capteurs = json.load(open("fixtures/capteurs.json"))
    for cap in capteurs:
        print(cap['rucher'])

    localisationsCapteurs = []

    ruchers = Rucher.objects.all()
    for r in ruchers:
        localisationsCapteurs.append(r)

    return render(request, 'User/camerasUser.html', {"capteurs": capteurs, "ruchers": localisationsCapteurs})


def videoCamerasUser(request, c_id):
    return render(request, 'User/videoCamerasUser.html', {'nameCapteur': c_id})


# partie apiculteur


# qrcode
def render_png_to_pdf(request, c_id):
    link_to_post = "127.0.0.1:8000/afficherColonieId/{}".format(c_id)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
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
    p.drawImage(filename, 0, 450)

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response


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

    for f in feuilles:
        if f.colonie == colonie:
            test = True
            etat = f.etatColonie
            break
        else:
            test = False
    if test:
        etatFeuilles.append({'colonie': colonie, 'etat': etat})
    else:
        etatFeuilles.append({'colonie': colonie, 'etat': 'rien'})

    print(etatFeuilles)

    return render(request, 'Apiculteurs/affichage/afficherColonieId.html',
                  {'c': colonie, 'feuilles': feuillesObj, 'nourri': nourrissementsObj,
                   'trait': traitementsObj, 'recoltes': recoltesObj, 'pesees': peseesObj,
                   'etatColonie': etatFeuilles})


def afficherColonies(request):
    colonies = Colonie.objects.all()

    feuillesObj = FeuilleVisite.objects.all()

    for f in feuillesObj:
        if f.notes is None:
            f.delete()

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
    for c in colonies:
        for f in feuilles:

            if f.colonie == c:
                test = True
                etat = f.etatColonie
                break
            else:
                test = False
        if test:
            etatFeuilles.append({'colonie': c, 'etat': etat})
        else:
            etatFeuilles.append({'colonie': c, 'etat': 'rien'})

    colonies = sorted(colonies, key=lambda a: a.rucher.nom)

    return render(request, 'Apiculteurs/affichage/afficherColonies.html',
                  {'colonies': colonies, 'etatColonie': etatFeuilles})


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
    for c in colonies:
        for f in feuilles:

            if f.colonie == c:
                test = True
                etat = f.etatColonie
                break
            else:
                test = False
        if test:
            etatFeuilles.append({'colonie': c, 'etat': etat})
        else:
            etatFeuilles.append({'colonie': c, 'etat': 'rien'})
    print(etatFeuilles)

    return render(request, 'Apiculteurs/affichage/afficherColoniesRucher.html',
                  {'colonies': colonies, 'rucher': rucher, 'etatColonie': etatFeuilles})


def afficherRuchers(request):
    ruchers = Rucher.objects.all()
    colonies = Colonie.objects.all()
    for c in colonies:
        colonieObj = Colonie.objects.get(nom=c, rucher=c.rucher)
        feuillesObj = FeuilleVisite.objects.all().filter(colonie=colonieObj)
        for f in feuillesObj:
            if f.notes is None:
                f.delete()
    return render(request, 'Apiculteurs/affichage/afficherRuchers.html', {'ruchers': ruchers})


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
        user = request.user
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
    return render(request, 'Apiculteurs/creation/createPesee.html', {'form': peseeForm, 'colonie': colonie, 'rucher': rucher})


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
    return render(request, 'Apiculteurs/creation/createRecolte.html', {'form': recolteForm, 'colonie': colonie, 'rucher': rucher})


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
            traitementsObj = Traitement.objects.all()
            for t in traitementsObj:
                if t.maladie is None:
                    t.delete()
            return redirect('afficherColonieId', colonieObj.id)
    else:
        obj = Traitement.objects.create(colonie=colonieObj)
        traitementForm = TraitementForm(instance=obj)
    return render(request, 'Apiculteurs/creation/createTraitement.html', {'form': traitementForm})


def modifierColonies(request):
    colonies = Colonie.objects.all()
    return render(request, 'Apiculteurs/modification/modifierColonies.html', {'colonies': colonies})


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


def modifierRuchers(request):
    ruchers = Rucher.objects.all()
    return render(request, 'Apiculteurs/modification/modifierRuchers.html', {'ruchers': ruchers})


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
                feuillesObj = FeuilleVisite.objects.all().filter(date=dateForm)
                feuilleObj = None
                # indice = 0
                # for f in feuillesObj:
                #     if indice == 0:
                #         feuilleObj = f
                #         indice = 1
                #     else:
                #         f.delete()

                # print(feuilleObj)
                feuille = feuillesObj[len(feuillesObj) - 1]
                print(feuille.conditionClimatique)
                # feuille = FeuilleVisite.objects.get(date=dateForm, rucher=rucherObj, colonie=colonieObj)
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


def afficherFeuilles(request):
    feuilles = FeuilleVisite.objects.all()
    return render(request, 'Apiculteurs/affichage/afficherFeuillesVisite.html', {'feuilles': feuilles})


def feuillePDF(request, f_id):
    fPDF = FeuilleVisite.objects.get(pk=f_id)
    return render(request, 'Apiculteurs/affichage/afficherFeuillePDF.html', {'f': fPDF})


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))


def export_pdf_Feuille(request, f_id):
    fPDF = FeuilleVisite.objects.get(pk=f_id)
    # return render_to_pdf(
    #     'Apiculteurs/affichage/afficherFeuillePDF.html',
    #     {
    #         'f': fPDF,
    #     }
    # )

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
    for c in colonies:
        for f in feuilles:

            if f.colonie == c:
                test = True
                etat = f.etatColonie
                break
            else:
                test = False
        if test:
            etatFeuilles.append({'colonie': c, 'etat': etat})
        else:
            etatFeuilles.append({'colonie': c, 'etat': 'rien'})

    colonies = sorted(colonies, key=lambda a: a.rucher.nom)

    return render(request, 'Admin/detailsUserAdmin.html',
                  {'userEdit': userEdit, 'colonies': colonies, 'etatColonie': etatFeuilles})
