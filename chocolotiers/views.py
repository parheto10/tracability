from itertools import product

from django.contrib import messages
from django.contrib.auth import authenticate, login as dj_login, get_user_model, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.http import JsonResponse

from parametres.models import (
    Sous_Prefecture,
    Origine,
    Prime,
    Projet,
    Activite,
    Region,
    Campagne
)

from cooperatives.models import (
    Cooperative,
    Producteur,
    Parcelle,
    Planting,
    Section,
    Sous_Section, Details_planting
)

def client_index(request, id=None):
    cooperatives = Cooperative.objects.all()
    nb_cooperatives = Cooperative.objects.all().count()
    nb_producteurs = Producteur.objects.all().count()
    nb_parcelles = Parcelle.objects.all().count()
    Superficie = Parcelle.objects.aggregate(total=Sum('superficie'))['total']
    Total_plant = Planting.objects.aggregate(total=Sum('nb_plant'))['total']

    context = {
        'cooperatives':cooperatives,
        'nb_cooperatives': nb_cooperatives,
        'nb_producteurs': nb_producteurs,
        'nb_parcelles': nb_parcelles,
        'Superficie': Superficie,
        'Total_plant': Total_plant,
    }
    return render(request, 'chocolatiers/client_index.html', context)

def detail_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    coop_producteurs = Producteur.objects.all().filter(section__cooperative_id=cooperative)
    coop_nb_producteurs = Producteur.objects.all().filter(cooperative_id=cooperative).count()
    coop_parcelles = Parcelle.objects.all().filter(producteur__section__cooperative_id=cooperative)
    coop_nb_parcelles = Parcelle.objects.all().filter(producteur__section__cooperative_id=cooperative).count()
    coop_superficie = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative).aggregate(total=Sum('superficie'))['total']
    plants = Details_planting.objects.all().filter(planting__parcelle__producteur__cooperative_id=cooperative).order_by('-espece')
    coop_plants_total = Planting.objects.all().filter(parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('nb_plant'))['total']

    labels = []
    data = []

    # cooperative = get_object_or_404(Cooperative, id=id)
    # queryset = Planting.objects.filter(parcelle__producteur__cooperative_id=cooperative).order_by('-espece')
    # for plant in coop_plants:
    #     labels.append(plant.espece)
    #     data.append(plant.nb_plant)

    context = {
        'cooperative': cooperative,
        'coop_nb_producteurs': coop_nb_producteurs,
        'coop_nb_parcelles': coop_nb_parcelles,
        'coop_superficie': coop_superficie,
        'plants': plants,
        'coop_plants_total': coop_plants_total,
        # 'labels': labels,
        # 'data': data,
    }
    return render(request, 'chocolatiers/Coop/cooperative.html', context)

def section_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    coop_sections = Section.objects.all().filter(cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_sections': coop_sections,
    }
    return render(request, 'chocolatiers/Coop/coop_sections.html', context)

def sous_section_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    coop_sous_sections = Sous_Section.objects.all().filter(section__cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_sous_sections': coop_sous_sections,
    }
    return render(request, 'chocolatiers/Coop/coop_sous_sections.html', context)

def prod_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    coop_producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    # coop_parcelles = Parcelle.objects.all().filter(producteur__section__cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_producteurs': coop_producteurs,
    }
    return render(request, 'chocolatiers/Coop/coop_producteurs.html', context)

def parcelle_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    # coop_producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    coop_parcelles = Parcelle.objects.all().filter(producteur__section__cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_parcelles' : coop_parcelles,
    }
    return render(request, 'chocolatiers/Coop/coop_parcelle.html', context)

def planting_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    # coop_producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    coop_plants = Planting.objects.all().filter(parcelle__producteur__cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_plants' : coop_plants,
    }
    return render(request, 'chocolatiers/Coop/coop_plantings.html', context)

def chart(request, id=None):
    labels = []
    data = []

    cooperative = get_object_or_404(Cooperative, id=id)
    queryset = Planting.objects.filter(parcelle__producteur__cooperative_id=cooperative).values('espece').annotate(country_population=Sum('nb_plant')).order_by('-espece')
    for city in queryset:
        labels.append(city.name)
        data.append(city.population)
    context = {
        'labels': labels,
        'data': data,
    }
    return render(request, 'Coop/cooperative.html', context)

def projet(request):
    projets = Projet.objects.all()
    context = {
        'projets': projets,
    }
    return render(request, 'projets.html', context)

def detail_proj(request, id=None):
    instance = get_object_or_404(Projet, id=id)
    # producteurs_proj = Parcelle.objects.all().filter(projet_id=instance).count()
    parcelles = Parcelle.objects.all().filter(projet_id=instance)
    parcelles = Parcelle.objects.all().filter(projet_id=instance)
    nb_parcelles_proj = Parcelle.objects.all().filter(projet_id=instance).count()
    plants = Planting.objects.all().filter(parcelle__projet_id=instance)
    nb_plants_proj = Planting.objects.all().filter(parcelle__projet_id = instance).count()
    superficie_proj = Parcelle.objects.all().filter(projet_id=instance).aggregate(total=Sum('superficie'))['total']
    context = {
        'instance': instance,
        'parcelles':parcelles,
        'nb_parcelles_proj':nb_parcelles_proj,
        'nb_plants_proj':nb_plants_proj,
        'plants':plants,
        'superficie_proj':superficie_proj,
        # 'producteurs_proj':producteurs_proj,
    }
    return render(request, 'projet.html', context)

def localisation(request):
    parcelles = Parcelle.objects.all()
    context = {
        'parcelles' : parcelles
    }
    return render(request, 'cooperatives/carte.html', context)

def localisation_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    # coop_producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    points_coop = Parcelle.objects.all().filter(producteur__section__cooperative_id=cooperative)
    context = {
        'points_coop' : points_coop
    }
    return render(request, 'carte1.html', context)


# Create your views here.
