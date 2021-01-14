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

from .models import (
    Sous_Prefecture,
    Origine,
    Prime,
    Projet,
    Activite,
    Region,
    Campagne,
    # Formations,
)

from cooperatives.models import (
    Cooperative,
    Producteur,
    Parcelle,
    Planting,
    Details_planting,
    Section,
    Sous_Section,
)

from .forms import UserForm, LoginForm

def connexion(request):
    login_form = LoginForm(request.POST or None)
    if login_form.is_valid():
        username = login_form.cleaned_data.get("username")
        password = login_form.cleaned_data.get("password")
        user = authenticate(request, username=username, password=password)
        if user != None:
            #utilisateur valide et actif(is_active=True)
            #"request.user == user"
            dj_login(request, user)
            group = request.user.groups.filter(user=request.user)[0]
            if group.name == "COOPERATIVES":
                messages.success(request, "Bienvenus : {}".format(username))
                return HttpResponseRedirect(reverse('cooperatives:dashboard'))
            elif group.name == "ADMIN":
                messages.success(request, "Bienvenus : {}".format(username))
                return HttpResponseRedirect(reverse('accueil'))
            elif group.name == "CLIENTS":
                messages.success(request, "Bienvenus : {}".format(username))
                return HttpResponseRedirect(reverse('clients:dashboard'))
            else:
                messages.error(request, "Désolé vous n'estes pas encore enregistrer dans notre Sytème")
                return HttpResponseRedirect(reverse('connexion'))
        else:
            request.session['invalid_user'] = 1 # 1 == True
            messages.error(request, "Echec de Connexion, Assurez-vous d'avoir entrer le bon login et le bon Mot de Passe SVP !")
            return HttpResponseRedirect(reverse('connexion'))
    return render(request, 'parametres/login.html', {'login_form': login_form})

def loggout(request):
    logout(request)
    return HttpResponseRedirect(reverse('connexion'))

def index(request, id=None):
    cooperatives = Cooperative.objects.all()
    nb_cooperatives = Cooperative.objects.all().count()
    nb_producteurs = Producteur.objects.all().count()
    nb_parcelles = Parcelle.objects.all().count()
    Superficie = Parcelle.objects.aggregate(total=Sum('superficie'))['total']
    Total_plant = Planting.objects.aggregate(total=Sum('nb_plant'))['total']
    # cooperative = get_object_or_404(Cooperative, id=id)
    # coop_nb_producteurs = Producteur.objects.all().filter(cooperative_id=cooperative).count()
    # coop_parcelles = Parcelle.objects.all().filter(producteur__section__cooperative_id=cooperative)
    # coop_nb_parcelles = Parcelle.objects.all().filter(producteur__section__cooperative_id=cooperative).count()
    # coop_superficie = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative).aggregate(total=Sum('superficie'))['total']
    # plants = Details_planting.objects.all().filter(planting__parcelle__producteur__cooperative_id=cooperative).order_by('-espece')
    # coop_plants_total = Planting.objects.all().filter(parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('nb_plant'))['total']


    context = {
        'cooperatives':cooperatives,
        'nb_cooperatives': nb_cooperatives,
        'nb_producteurs': nb_producteurs,
        'nb_parcelles': nb_parcelles,
        'Superficie': Superficie,
        'Total_plant': Total_plant,
        # 'coop_nb_producteurs': coop_nb_producteurs,
        # 'coop_nb_parcelles': coop_nb_parcelles,
        # 'coop_superficie': coop_superficie,
        # 'plants': plants,
        # 'coop_plants_total': coop_plants_total,
    }
    return render(request, 'index.html', context)

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
    return render(request, 'Coop/cooperative.html', context)

def section_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    coop_sections = Section.objects.all().filter(cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_sections': coop_sections,
    }
    return render(request, 'Coop/coop_sections.html', context)

def sous_section_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    coop_sous_sections = Sous_Section.objects.all().filter(section__cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_sous_sections': coop_sous_sections,
    }
    return render(request, 'Coop/coop_sous_sections.html', context)

def prod_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    coop_producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    # coop_parcelles = Parcelle.objects.all().filter(producteur__section__cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_producteurs' : coop_producteurs,
    }
    return render(request, 'Coop/coop_producteurs.html', context)

def parcelle_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    # coop_producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    coop_parcelles = Parcelle.objects.all().filter(producteur__section__cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_parcelles' : coop_parcelles,
    }
    return render(request, 'Coop/coop_parcelle.html', context)

def planting_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    # coop_producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    coop_plants = Planting.objects.all().filter(parcelle__producteur__cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_plants' : coop_plants,
    }
    return render(request, 'Coop/coop_plantings.html', context)


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
    parcelles = Planting.objects.all().filter(projet_id=instance)
    parcelles = Planting.objects.all().filter(projet_id=instance)
    nb_parcelles_proj = Planting.objects.all().filter(projet_id=instance).count()
    plants = Planting.objects.all().filter(projet_id=instance)
    nb_plants_proj = Planting.objects.all().filter(projet_id = instance).count()
    # superficie_proj = Planting.objects.all(parcelle).filter().aggregate(total=Sum('superficie'))['total']
    context = {
        'instance': instance,
        'parcelles':parcelles,
        'nb_parcelles_proj':nb_parcelles_proj,
        'nb_plants_proj':nb_plants_proj,
        'plants':plants,
        # 'superficie_proj':superficie_proj,
        # 'producteurs_proj':producteurs_proj,
    }
    return render(request, 'projet.html', context)


# def formation(request):
#     formations = Formations.objects.all()
#     context = {
#         'formations': formations,
#     }
#     return render(request, 'formations.html', context)
#
# def detail_formation(request, id=None):
#     instance = get_object_or_404(Formations, id=id)
#     cooperative = get_object_or_404(Cooperative, id=id)
#     # producteurs_proj = Parcelle.objects.all().filter(projet_id=instance).count()
#     # parcelles = Parcelle.objects.all().filter(projet_id=instance)
#     # parcelles = Parcelle.objects.all().filter(projet_id=instance)
#     # nb_parcelles_proj = Parcelle.objects.all().filter(projet_id=instance).count()
#     # plants = Planting.objects.all().filter(parcelle__projet_id=instance)
#     # nb_plants_proj = Planting.objects.all().filter(parcelle__projet_id = instance).count()
#     # superficie_proj = Parcelle.objects.all().filter(projet_id=instance).aggregate(total=Sum('superficie'))['total']
#     context = {
#         'instance': instance,
#         'cooperative':cooperative,
#         # 'parcelles':parcelles,
#         # 'nb_parcelles_proj':nb_parcelles_proj,
#         # 'nb_plants_proj':nb_plants_proj,
#         # 'plants':plants,
#         # 'superficie_proj':superficie_proj,
#         # 'producteurs_proj':producteurs_proj,
#     }
#     return render(request, 'detail_formation.html', context)

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
