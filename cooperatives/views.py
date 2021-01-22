from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
# from django.contrib.gis.serializers import geojson
from django.core.serializers import serialize
from django.db.models import Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import folium
import json

from parametres.forms import UserForm
from parametres.models import Projet
from .forms import CoopForm, ProdForm, EditProdForm, ParcelleForm, PlantingForm, SectionForm, Sous_SectionForm
from .models import Cooperative, Section, Sous_Section, Producteur, Parcelle, Planting, Formation, Detail_Formation


def is_cooperative(user):
    return user.groups.filter(name='COOPERATIVES').exists()

#@login_required(login_url='connexion')
#@user_passes_test(is_cooperative)
def cooperative(request, id=None):
    coop = get_object_or_404(Cooperative, pk=id)
    producteurs = Producteur.objects.all().filter(section__cooperative_id= coop)
    nb_producteurs = Producteur.objects.all().filter(section__cooperative_id= coop).count()
    parcelles = Parcelle.objects.all().filter(propietaire__section__cooperative_id=coop)
    nb_parcelles = Parcelle.objects.all().filter(propietaire__section__cooperative_id=coop).count()
    context = {
        "coop": coop,
        'cooperative': cooperative,
        'producteurs': producteurs,
        'nb_producteurs': nb_producteurs,
        'parcelles': parcelles,
        'nb_parcelles': nb_parcelles,
    }
    return render(request, "cooperatives/dashboard.html", context)

def coop_dashboard(request):
    cooperative= Cooperative.objects.get(user_id=request.user.id)
    producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    nb_producteurs = Producteur.objects.all().filter(cooperative_id=cooperative).count()
    nb_formations = Formation.objects.all().filter(cooperative_id=cooperative).count()
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    nb_parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative).count()
    Superficie = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative).aggregate(total=Sum('superficie'))['total']
    Plants = Planting.objects.all().filter(parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('nb_plant'))['total']

    context={
    'cooperative':cooperative,
    'producteurs': producteurs,
    'nb_formations': nb_formations,
    'nb_producteurs': nb_producteurs,
    'parcelles': parcelles,
    'nb_parcelles': nb_parcelles,
    'Superficie' : Superficie,
    'Plants': Plants,
    }
    return render(request,'cooperatives/dashboard.html',context=context)

def add_coop(request):
    userForm=UserForm()
    coopForm=CoopForm()
    if request.method=='POST':
        userForm=UserForm(request.POST)
        coopForm=coopForm(request.POST,request.FILES)
        if userForm.is_valid() and coopForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            cooperative=coopForm.save(commit=False)
            cooperative.user=user
            cooperative=cooperative.save()
            print(cooperative)
            cooperative_group = Group.objects.get_or_create(name='COOPERATIVES')
            cooperative_group[0].user_set.add(user)
        messages.success(request, "Utilisateur Ajouté avec succès")
        return HttpResponseRedirect(reverse('accueil'))
    context = {
        'userForm': userForm,
        'coopForm': coopForm
    }
    return render(request,'cooperatives/add_coop.html',context=context)

def add_section(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    sections = Section.objects.all().filter(cooperative_id=cooperative)
    form = SectionForm()
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.cooperative_id = cooperative.id
            section = section.save()
            # print()
        messages.success(request, "Section Ajoutée avec succès")
        return HttpResponseRedirect(reverse('cooperatives:section'))
    context = {
        "cooperative": cooperative,
        "sections": sections,
        'form': form,
    }
    return render(request, "cooperatives/sections.html", context)

def add_sous_section(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    sections = Section.objects.all().filter(cooperative_id=cooperative)
    sous_sections = Sous_Section.objects.all().filter(section__cooperative_id=cooperative)
    form = Sous_SectionForm()
    if request.method == 'POST':
        form = Sous_SectionForm(request.POST)
        if form.is_valid():
            sous_section = form.save(commit=False)
            for section in sections:
                sous_section.section_id = section.id
            sous_section = sous_section.save()
            # print()
        messages.success(request, "Sous Section Ajoutée avec succès")
        return HttpResponseRedirect(reverse('cooperatives:sous_sections'))
    context = {
        "cooperative": cooperative,
        "sous_sections": sous_sections,
        "sections": sections,
        'form': form,
    }
    return render(request, "cooperatives/sous_sections.html", context)

def producteurs(request):
    cooperative = request.user.cooperative #Cooperative.objects.get(user_id=request.user.id)
    producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    sections = Section.objects.filter(cooperative_id=cooperative)
    # parcelles = Parcelle.objects.all().filter(propietaire__cooperative_id=cooperative)

    prodForm = ProdForm()
    if request.method == 'POST':
        prodForm = ProdForm(request.POST, request.FILES)
        if prodForm.is_valid():
            producteur = prodForm.save(commit=False)
            producteur.cooperative_id = cooperative.id
            for section in sections:
                producteur.section_id = section.id
            producteur = producteur.save()
            print(producteur)   
        messages.success(request, "Producteur Ajouté avec succès")
        return HttpResponseRedirect(reverse('cooperatives:producteurs'))

    context = {
        "cooperative":cooperative,
        "producteurs": producteurs,
        'prodForm': prodForm,
        'sections':sections
    }
    return render(request, "cooperatives/producteurs.html", context)

def my_section(request):
    cooperative = request.GET.get("user_id")#Cooperative.objects.get(user_id=request.user.id)
    coop_sections = Section.objects.filter(cooperative_id=cooperative)
    context = {'coop_sections': coop_sections}
    return render(request, 'cooperatives/section.html', context)

def prod_update(request, code=None):
	instance = get_object_or_404(Producteur, code=code)
	form = EditProdForm(request.POST or None, request.FILES or None, instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "Producteur Modifié Avec Succès", extra_tags='html_safe')
		return HttpResponseRedirect(reverse('cooperatives:producteurs'))

	context = {
		"instance": instance,
		"form":form,
	}
	return render(request, "cooperatives/prod_edt.html", context)

def prod_delete(request, code=None):
    item = get_object_or_404(Producteur, code=code)
    if request.method == "POST":
        item.delete()
        messages.error(request, "Producteur Supprimer Avec Succès")
        return redirect('cooperatives:producteurs')
    context = {
        'item': item,
    }
    return render(request, 'cooperatives/prod_delete.html', context)

def parcelles(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    prods = Producteur.objects.filter(cooperative_id=cooperative)
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    parcelleForm = ParcelleForm(request.POST or None)
    if request.method == 'POST':
        parcelleForm = ParcelleForm(request.POST, request.FILES)
        if parcelleForm.is_valid():
            parcelle = parcelleForm.save(commit=False)

            # parcelle.producteur_id = prods
            # for prod in prods:
            #     parcelle.producteur_id = prod.
            parcelle = parcelle.save()
            print(parcelle)
        messages.success(request, "Parcelle Ajoutés avec succès")
        return HttpResponseRedirect(reverse('cooperatives:parcelles'))

    context = {
        "cooperative":cooperative,
        "parcelles": parcelles,
        'parcelleForm': parcelleForm,
        'producteurs': prods
    }
    return render(request, "cooperatives/parcelles.html", context)

def parcelle_delete(request, id=None):
    parcelle = get_object_or_404(Parcelle, id=id)
    parcelle.delete()
    messages.success(request, "Parcelle Supprimer avec Succès")
    return HttpResponseRedirect(reverse('cooperatives:parcelles'))

def planting(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    #producteurs = Producteur.objects.all().filter(cooperative=cooperative)
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    plantings = Planting.objects.all().filter(parcelle__producteur__cooperative_id=cooperative)
    plantingForm = PlantingForm()
    if request.method == 'POST':
        plantingForm = PlantingForm(request.POST, request.FILES)
        if plantingForm.is_valid():
            planting = plantingForm.save(commit=False)
            planting = planting.save()
            print(planting)
        messages.success(request, "Parcelle Ajoutés avec succès")
        return HttpResponseRedirect(reverse('cooperatives:planting'))

    context = {
        "cooperative":cooperative,
        "plantings": plantings,
        'plantingForm': plantingForm,
    }
    return render(request, "cooperatives/plantings.html", context)

def planting_update(request, id=None):
	instance = get_object_or_404(Planting, id=id)
	form = PlantingForm(request.POST or None, request.FILES or None, instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "Modification effectuée avec succès")
		return HttpResponseRedirect(reverse('cooperatives:planting'))

	context = {
		"instance": instance,
		"form":form,
	}
	return render(request, "cooperatives/planting_edit.html", context)

#-------------------------------------------------------------------------
## Export to Excel
#-------------------------------------------------------------------------

import csv

from django.http import HttpResponse
from django.contrib.auth.models import User

def export_producteur_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="producteurs.csv"'

    writer = csv.writer(response)
    writer.writerow(['CODE', 'TYPE', 'SECTION', 'GENRE', 'NOM', 'PRENOMS', 'CONTACTS'])
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    # producteurs = Producteur.objects.all().filter(cooperative=cooperative)

    producteurs = Producteur.objects.all().filter(cooperative_id=cooperative.id).values_list(
        'code',
        'type_producteur',
        'section__libelle',
        'genre',
        'nom',
        'prenoms',
        'contacts',
    )
    for p in producteurs:
        writer.writerow(p)

    return response


import xlwt

from django.http import HttpResponse
from django.contrib.auth.models import User

def export_prod_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="producteurs.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Producteurs')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['COOPERATIVE', 'CODE', 'TYPE', 'SECTION', 'GENRE', 'NOM', 'PRENOMS', 'CONTACTS']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    rows = Producteur.objects.all().filter(cooperative_id=cooperative.id).values_list(
        'cooperative__sigle',
        'code',
        'type_producteur',
        'section__libelle',
        'genre',
        'nom',
        'prenoms',
        'contacts',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

def export_parcelle_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Parcelles.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Parcelles')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['CODE', 'P.NOM', 'P.PRENOMS', 'CERTIFI', 'CULTURE', 'SUPER', 'LONG', 'LAT', 'SECTION']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    rows = Parcelle.objects.all().filter(propietaire__cooperative_id=cooperative.id).values_list(
        'code',
        'propietaire__nom',
        'propietaire__prenoms',
        'certification',
        'culture',
        'superficie',
        'longitude',
        'latitude',
        'section__libelle',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

def export_plant_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Planting.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Plants')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['P.CODE', 'P.NOM', 'P.PRENOMS', 'PARCELLE', 'ESPECE', 'NOMBRE', 'DATE']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    rows = Planting.objects.all().filter(parcelle__propietaire__cooperative_id=cooperative.id).values_list(
        'parcelle__propietaire__code',
        'parcelle__propietaire__nom',
        'parcelle__propietaire__prenoms',
        'parcelle__code',
        'espece',
        'nb_plant',
        'date',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

from io import BytesIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse

def export_prod_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Producteurs.pdf"'

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Start writing the PDF here
    p.drawString(100, 100, 'Hello world.')
    # End writing

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response

from django.shortcuts import render
from django.core.serializers import serialize
from django.http import HttpResponse

# def localisation(request):
#     cooperative = Cooperative.objects.get(user_id=request.user.id)
#     parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative).values('latitude', 'longitude')
#     json_res = []
#     for parcelle in parcelles:
#         json_obj = dict(
#             myproperty=parcelle
#         )
#         json_res.append(json_obj)
#     # map = folium.Map(location=[5.349390, -4.017050], zoom_start=8)
#     # for p in [parcelles]:
#     #     print(parcelles)
#     #     print(p)
#     #     # marker de depart
#     #     folium.Marker(parcelles[p],
#     #     icon=folium.Icon(color='darkblue',
#     #     icon_color='white',
#     #     icon='male',
#     #     angle=0,
#     #     prefix='fa')).add_to(map)  # icon=folium.Icon(color='purple'))
#     #     # map.add_child(coordonnees)
#     #     map = map._repr_html_()
#     context = {
#         'parcelles': parcelles
#     }
#     return render(request, 'cooperatives/map.html', context)
#     cooperative = Cooperative.objects.get(user_id=request.user.id)
#     parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
#     dict = list(parcelles.values())
#     for point, latitude, longitude in dict:
#         print(dict)
#         # if point:
#         latlon = [(latitude, longitude)]
#         map = folium.Map(location=[5.349390, -4.017050], zoom_start=8)
#         for p in range(len([latlon])):
#             # latlon +=p
#             # print(p)
#         # marker de depart
#             folium.Marker(latlon[p],
#                 popup=point.producteur,
#                 tooltip=point.projet.titre,
#                 icon=folium.Icon(color='darkblue',
#                 icon_color='white',
#                 icon='male',
#                 angle=0,
#                 prefix='fa')).add_to(map)#icon=folium.Icon(color='purple'))
#            # map.add_child(coordonnees)
#         map = map._repr_html_()
#         context = {
#             'carte': map,
#             'point':point,
#             'latlon' :latlon
#         }
#         return render(request, 'cooperatives/calcul_dstce.html', context)
#             # folium.Marker(location=[coord[0], coord[1]], fill_color='#43d9de', radius=8).add_to(map)
#         # map.save('cooperatives/map.html')
#     # return render(request, 'carte3.html')
#     cooperative = Cooperative.objects.get(user_id=request.user.id)
#     parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
#     for parcelle in parcelles.values('latitude', 'longitude'):
#         print(parcelle)
#         # print(parcelle['latitude'], parcelle['longitude'])
#         latitude = (parcelle.latitude)
#         longitude = (parcelle.longitude)
#         # lon = parcelle.longitude
#         coordonne = [latitude,longitude]
#         map = folium.Map(location=[5.349390, -4.017050], zoom_start=12)
#         for point in coordonne:
#             # print(len(lat, lon))
#             folium.Marker(coordonne[point]).add_to(map)
#             context = {
#                 'map':map,
#                 'parcelle': parcelle,
#             }
#             return render(request, 'cooperatives/calcul_dstce.html', context)

# def localisation(request):
#     cooperative = Cooperative.objects.get(user_id=request.user.id)
#     parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
#     # data = serializers.serialize('json', parcelles)#json.dumps(parcelles)
#     data = serializers.serialize('json', Parcelle.objects.all().filter(producteur__cooperative_id=cooperative), fields=('latitude', 'longitude'))
#     # data = serializers.serialize('json', parcelles)#json.dumps(parcelles)
#     coordonnees = json.loads(data)
#     # print('point :', coordonnees)
#     # for p in coordonnees:
#     for latitude in list(parcelles.values()):
#         print('lat: ', latitude)
#         lat = coordonnees([latitude])
#         # long = coordonnees([longitude])
#         print(lat)
#         coordonne = [(lat)]
#         map = folium.Map(location=[5.349390, -4.017050], zoom_start=8)
#         for point in range(0, len([coordonne])):
#             folium.Marker(coordonne[point],
#               popup=point,
#               tooltip=point,
#               icon=folium.Icon(color='darkblue',
#                icon_color='white',
#                icon='male',
#                angle=0,
#                prefix='fa'
#             )).add_to(map)
#     # return render(request, 'carte3.html')
#      # map.add_child(coordonnees)
#         map = map._repr_html_()
#         context = {
#             'carte': map,
#             # 'parcelle':parcelle,
#             # 'latlon' :latlon
#         }
#         return render(request, 'cooperatives/calcul_dstce.html', context)
#             # folium.Marker([lat], long)






def localisation(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    # parcelles = Planting.objects.filter(parcelle__producteur__cooperative_id=cooperative).all()
    context = {
        'parcelles' : parcelles
    }
    return render(request, 'cooperatives/carte.html', context)
    # places = serialize('geojson', parcelles)
    # print("parcelles :", parcelles)
    # print("places :", places)
    # return HttpResponse(places, content_type='json')

# def load_section(request):
#     cooperative = Cooperative.objects.get(user_id=request.user.id)
#     cooperative_id = request.GET.get('cooperative')
#     # section_id = Section.objects.filter(cooperative_id = cooperative_id)
#     sections = Section.objects.filter(cooperative_id = cooperative_id)
#     producteurs = Producteur.objects.filter(cooperative_id=cooperative)
#     # parcelle_id = Parcelle.objects.filter(producteur_id=producteur_id)
#     # parcelle_id = Parcelle.objects.filter(producteur_id=producteur_id)
#     # cities = City.objects.filter(country_id=country_id).order_by('name')
#     context = {
#         'sections':sections,
#         'producteurs':producteurs,
#     }
#     return render(request, 'cooperatives/producteur_dropdown.html', context)

def formation(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    formations = Formation.objects.all().filter(cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'formations': formations,
    }
    return render(request, 'cooperatives/formations.html', context)

def detail_formation(request, id=None):
    instance = get_object_or_404(Formation, id=id)
    detail = Detail_Formation.objects.all().filter(formation_id=instance)
    # participants = Producteur.objects.all().filter(formation_id=formation)
    context = {
        'instance':instance,
        'detail':detail,
        # 'participants': participants,
    }
    return render(request, 'cooperatives/detail_formation.html', context)