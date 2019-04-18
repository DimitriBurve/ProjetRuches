from django.urls import path

from . import views

urlpatterns = [
    # vues communes
    path('', views.home, name='home'),
    path('home', views.home, name='homeUser'),
    path('informationsUser', views.informationsUser, name='infosUser'),
    path('detailCapteurUser/<str:nameCapteur>', views.capteurUser, name='detailsUser'),
    path('camerasUser', views.camerasUser, name='camerasUser'),
    path('videoCameraUser/<str:nameCapteur>', views.videoCamerasUser, name='videoCameraUser'),
    # vues apiculteurs
    path('afficherColonies', views.afficherColonies, name='afficherColonies'),
    path('afficherColoniesRucher/<str:rucher>', views.affichercoloniesRucher, name='afficherColoniesRucher'),
    path('afficherRuchers', views.afficherRuchers, name='afficherRuchers'),
    path('afficherNourrissements', views.afficherNourrissement, name='afficherNourrissement'),
    path('ajouterRucher', views.ajouterRucher, name='ajouterRucher'),
    path('ajouterColonie', views.ajouterColonie, name='ajouterColonie'),
    path('ajouterNourrissement/<str:rucher>/<str:colonie>', views.ajouterNourrissement, name='ajouterNourrissement'),
    path('modifierColonies', views.modifierColonies, name='modifierColonies'),
    path('modifierRuchers', views.modifierRuchers, name='modifierRuchers'),
    path('supprimerColonies', views.supprimerColonies, name='supprimerColonies'),
    path('validSupprimerColonie/<str:colonie>/<str:rucher>', views.validSupprimerColonie, name='validSupprimerColonie'),
    path('supprimerRuchers', views.supprimerRuchers, name='supprimerRuchers'),
    path('validSupprimerRucher/<str:rucher>', views.validSupprimerRucher, name='validSupprimerRucher'),
    # vues inscription et mon compte
    path('inscription', views.inscription, name='inscription'),
    path('monCompte', views.monCompte, name='monComte'),
    path('detailsMonCompte/<str:user_id>', views.detailsMonCompte, name="detailsMonCompte"),
    path('modifierMonCompte', views.modifierMonCompte, name='modifierMonCompte'),
    # vues admin
    path('showUsersAdmin', views.showUsersAdmin, name='showUsersAdmin'),
    path('deleteUserAdmin/<str:username>', views.deleteUserAdmin, name='deleteUserAdmin'),
    path('detailsUserAdmin/<str:username>', views.detailsUserAdmin, name='detailsUserAdmin'),
]
