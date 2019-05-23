from django.urls import path

from . import views

urlpatterns = [
    # vues communes
    path('', views.home, name='home'),
    path('home', views.home, name='homeUser'),
    path('informationsUser', views.informationsUser, name='infosUser'),
    path('detailCapteurUser/<str:idCapteur>', views.capteurUser, name='detailsUser'),
    path('json', views.jsonView, name="json"),
    path('camerasUser', views.camerasUser, name='camerasUser'),
    path('videoCameraUser/<int:c_id>', views.videoCamerasUser, name='videoCameraUser'),
    # vues apiculteurs
    path('afficherColonieId/<int:c_id>', views.afficherColonieId, name='afficherColonieId'),
    path('afficherColonies', views.afficherColonies, name='afficherColonies'),
    path('afficherColoniesRucher/<str:rucher>', views.affichercoloniesRucher, name='afficherColoniesRucher'),
    path('afficherRuchers', views.afficherRuchers, name='afficherRuchers'),
    path('ajouterColonie', views.ajouterColonie, name='ajouterColonie'),
    path('ajouterColonieRucher/<str:rucher>', views.ajouterColonieRucher, name='ajouterColonieRucher'),
    path('ajouterNourrissement/<str:rucher>/<str:colonie>', views.ajouterNourrissement, name='ajouterNourrissement'),
    path('ajouterPesee/<str:rucher>/<str:colonie>', views.ajouterPesee, name='ajouterPesee'),
    path('ajouterRecolte/<str:rucher>/<str:colonie>', views.ajouterRecolte, name='ajouterRecolte'),
    path('ajouterRucher', views.ajouterRucher, name='ajouterRucher'),
    path('ajouterTraitement/<str:rucher>/<str:colonie>', views.ajouterTraitement, name='ajouterTraitement'),
    path('modifierColonies', views.modifierColonies, name='modifierColonies'),
    path('modifierColonieId/<int:c_id>', views.modifierColonieId, name='modifierColonieId'),
    path('modifierRucherId/<int:r_id>', views.modifierRucherId, name='modifierRucherId'),
    path('supprimerColonies', views.supprimerColonies, name='supprimerColonies'),
    path('supprimerRuchers', views.supprimerRuchers, name='supprimerRuchers'),
    path('validSupprimerColonie/<str:colonie>/<str:rucher>', views.validSupprimerColonie, name='validSupprimerColonie'),
    path('validSupprimerNourrissement/<int:n_id>', views.validSupprimerNourrissement, name='validSupprimerNourrissement'),
    path('validSupprimerPesee/<int:p_id>', views.validSupprimerPesee, name="validSupprimerPesee"),
    path('validSupprimerRecolte/<int:r_id>', views.validSupprimerRecolte, name='validSupprimerRecolte'),
    path('validSupprimerRucher/<str:rucher>', views.validSupprimerRucher, name='validSupprimerRucher'),
    # vues feuille de visite
    path('createFeuilleVisite/<str:rucher>/<str:colonie>/<int:etape>', views.createFeuillevisite, name='createFeuilleVisite'),
    path('afficherFeuilles', views.afficherFeuilles, name='afficherFeuilles'),
    path('afficherPDF/<int:f_id>', views.export_pdf_Feuille, name='afficherPDF'),
    #qr
    path('afficherQR/<int:c_id>', views.render_png_to_pdf, name='afficherQR'),
    # vues inscription et mon compte
    path('inscription', views.inscription, name='inscription'),
    path('monCompte', views.monCompte, name='monComte'),
    path('detailsMonCompte/<str:user_id>', views.detailsMonCompte, name="detailsMonCompte"),
    path('modifierMonCompte/<str:user_id>', views.modifierMonCompte, name='modifierMonCompte'),
    # vues admin
    path('showUsersAdmin', views.showUsersAdmin, name='showUsersAdmin'),
    path('deleteUserAdmin/<str:username>', views.deleteUserAdmin, name='deleteUserAdmin'),
    path('detailsUserAdmin/<str:username>', views.detailsUserAdmin, name='detailsUserAdmin'),
    path('sendMail/<str:user_id>', views.envoie_mail, name='sendMail'),
    path('registreXLS/<int:r_id>/<str:annee>/<str:user_id>', views.registreXLS, name='registreXLS'),
    path('afficherRegistreColonieId/<int:r_id>', views.afficherRegistreColonieId, name='afficherRegistreColonieId'),
    path('contactAdmin', views.contactAdmin, name='contactAdmin')
]


