from django.urls import path

from .views import (
    index,
    connexion,
    loggout,
    projet,
    # formation,
    detail_proj,
    localisation,
    detail_coop,
    chart,
    prod_coop,
    parcelle_coop,
    localisation_coop,
    section_coop,
    sous_section_coop,
    planting_coop,
    # detail_formation,
)

urlpatterns = [
    path('', connexion, name='connexion'),
    path('logout', loggout, name='logout'),
    path('index/', index, name='accueil'),
    path('projets/', projet, name='projets'),
    # path('formations/', formation, name='formations'),
    path('producteurs/<int:id>', prod_coop, name='prod_coop'),
    path('parcelles/<int:id>', parcelle_coop, name='parcelle_coop'),
    path('sections/<int:id>', section_coop, name='section_coop'),
    path('sous_sections/<int:id>', sous_section_coop, name='sous_section_coop'),
    path('planting/<int:id>', planting_coop, name='planting_coop'),
    path('coordonnes/<int:id>', localisation_coop, name='localisation_coop'),
    path('localisation/', localisation, name='localisation'),
    path('detail_proj/<int:id>', detail_proj, name='detail_proj'),
    # path('formation/<int:id>', detail_formation, name='formation'),
    path('detail_coop/<int:id>', detail_coop, name='detail_coop'),
    # path('chart/<int:id>', chart, name='chart'),
]
