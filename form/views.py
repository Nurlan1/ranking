from django.shortcuts import render, render_to_response, redirect
from .models import Criteria, Indicator, Group, Category, University_Data, University
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.contrib import messages
# Create your views here.
def form_render_view(request, mes=0):
    criterias = Criteria.objects.all()
    university = University.objects.get(Id=1)

    if request.method == 'POST':
        data = request.POST.copy()
        if 'university_name' in data:
            university.Name = data.get('university_name')
            try:
                university.Logo = request.FILES['logo']
            except:
                pass
            university.WebAddress = data.get('website')
            university.save()
        for criteria in criterias:

                #
                # filler
                # position
                # phonenumber

            if f'{criteria.Id}' in data:
                university_data = University_Data.objects.filter(University_id=university, Criteria_id=criteria).first()
                if not university_data:
                    university_data = University_Data.objects.create(Value=1)

                university_data.University_id_id = 1
                university_data.Criteria_id_id = criteria.Id
                university_data.Value = data.get(f'{criteria.Id}') if data.get(f'{criteria.Id}') is not '' else None
                university_data.Checked = False
                university_data.Date = str(datetime.date.today())
                if criteria.File_Need:
                    if f'f{criteria.Id}' in request.FILES:
                        university_data.File = request.FILES[f'f{criteria.Id}']

                university_data.save()
        return redirect(request.build_absolute_uri(),request)
    else:
        university_data = University_Data.objects.filter(University_id_id=university)
        categories = Category.objects.all()
        indicators = Indicator.objects.all()
        groups = Group.objects.all()
        paginator = Paginator(categories, 1)
        page = request.GET.get('page')

        try:
            category = paginator.page(page)
        except PageNotAnInteger:
            category = paginator.page(1)
        except EmptyPage:
            category = paginator.page(paginator.num_pages)

        context = {'criteria': criterias, 'indicators': indicators, 'categories': category, 'groups': groups, 'page': category, 'university_data': university_data, 'university': university}
        return render(request, "criteria.html", context)

def ranking_view(request):
    context = {'seq': [1,2,3,4]}
    return render(request, "ranking.html", context)