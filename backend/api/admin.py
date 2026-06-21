from django.contrib import admin
from .models import (
    Profil, Site, Formation, Lecon,
    Inscription, Session, Note, Certificat, Parametres
)

@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'telephone']
    list_filter  = ['role']

@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display  = ['nom', 'niveau', 'duree', 'places', 'formateur']
    list_filter   = ['niveau']
    search_fields = ['nom']

@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display  = ['utilisateur', 'niveau', 'statut', 'date_inscription']
    list_filter   = ['statut', 'niveau']
    search_fields = ['utilisateur__email', 'utilisateur__first_name']

@admin.register(Lecon)
class LeconAdmin(admin.ModelAdmin):
    list_display = ['titre', 'formation', 'ordre']
    list_filter  = ['formation']

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['apprenant', 'formation', 'valeur', 'date']

@admin.register(Certificat)
class CertificatAdmin(admin.ModelAdmin):
    list_display = ['numero', 'apprenant', 'formation', 'date_delivrance']

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['nom', 'adresse', 'actif']

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['formation', 'site', 'date_debut', 'date_fin']

@admin.register(Parametres)
class ParametresAdmin(admin.ModelAdmin):
    list_display = ['nom', 'email', 'telephone']