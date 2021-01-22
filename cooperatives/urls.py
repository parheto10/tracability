from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static

from .views import (
    coop_dashboard,
    add_section,
    add_sous_section,
    producteurs,
    cooperative,
    prod_update,
    prod_delete,
    parcelles,
    parcelle_delete,
    planting,
    planting_update,
    formation,
    detail_formation,
    localisation,
    # use Ajax and jquery request
    my_section,
    export_producteur_csv,
    export_prod_xls,
    export_parcelle_xls,
    export_plant_xls,
    # load_section
)

app_name='cooperatives'

urlpatterns = [
    # Patient
    path('cooperative/<int:id>', cooperative, name='cooperative'),
    path('producteur/<str:code>/modifier', prod_update, name='modifier'),
    path('producteur/<str:code>/supprimer', prod_delete, name='del_producteur'),
    path('parcelle/<int:id>', parcelle_delete, name='del_parcelle'),
    path('dashboard/', coop_dashboard, name='dashboard'),
    path('sections/', add_section, name='section'),
    path('sous_sections/', add_sous_section, name='sous_sections'),
    path('formation/', formation, name='formations'),
    path('formation/<int:id>', detail_formation, name='formation'),
    path('producteurs/', producteurs, name='producteurs'),
    path('parcelles/', parcelles, name='parcelles'),
    path('plantings/', planting, name='planting'),
    path('localisation/', localisation, name='localisation'),
    path('plantings/<int:id>', planting_update, name='planting_update'),

    #get Ajax Data
    #path('my-section/', my_section, name='my_section'),
    # path('ajax/load-section/', load_section, name='ajax_load_section'),

    #Exportation de Données En Excel
    # path('export/csv/', export_producteur_csv, name='export_producteur_csv'),
    path('producteurs/xls/', export_prod_xls, name='export_prod_xls'),
    path('parcelles/xls/', export_parcelle_xls, name='export_parcelle_xls'),
    path('plants/xls/', export_plant_xls, name='export_plant_xls'),

    # path('settings/', profile_setting, name='settings'),
    # path('add_patient/', add_patient, name="add_patient"),
    # path('rdv/', rdv_patient, name="checkout"),
]