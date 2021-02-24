from django.shortcuts import render, render_to_response, redirect
from .models import Criteria, Indicator, Group, Category, University_Data,UserProfile, User, University, Year, Sub_Criteria, Sub_Data, Student_form, Emp_form, Dig_form,Major
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
import ast
from django.contrib import messages
import re
from py_expression_eval import Parser
from django.db.models import Max, Sum


def form_render_view(request, mes=0):
    criterias = Criteria.objects.filter(Year_id=Year.objects.filter().order_by().first())
    university = University.objects.get(Id=request.user.info.University_id.Id)
    sub_criterias = Sub_Criteria.objects.all()
    if request.method == 'POST':
        data = request.POST.copy()
        if 'university_name' in data:
            user = User.objects.get(username=request.user.username)
            info = UserProfile.objects.get(user=user)
            user.first_name = data.get('filler')
            info.Position = data.get('position')
            info.PhoneNumber = data.get('phonenumber')
            user.save()
            info.save()
            university.Name = data.get('university_name')
            try:
                university.Logo = request.FILES['logo']
            except:
                pass
            university.WebAddress = data.get('website')
            university.save()

        for criteria in criterias:
            if f'{criteria.Id}' in data:
                university_data = University_Data.objects.filter(University_id=university, Criteria_id=criteria, Year_id=Year.objects.filter().order_by().first()).first()
                if not university_data:
                    university_data = University_Data.objects.create(Year_id=Year.objects.filter().order_by().first())
                university_data.University_id_id = university

                university_data.Criteria_id_id = criteria.Id
                university_data.Value = data.get(f'{criteria.Id}') if data.get(f'{criteria.Id}') is not '' else None
                s = criteria.sub_crits
                if s.count():
                    s_sum=0
                    for subs in s.all():
                        sub_data= Sub_Data.objects.filter(University_id=university, Sub_criteria_id=subs, Year_id=Year.objects.filter().order_by().first()).first()
                        if not sub_data:
                            sub_data = Sub_Data.objects.create(University_id=university,Sub_criteria_id=subs,Year_id=Year.objects.filter().order_by().first())
                        f=data.get(f's{subs.Id}')
                        if f == '' or f is True:
                            s_sum += subs.Max_value
                            sub_data.Value = True
                        else:
                            sub_data.Value = False
                        sub_data.save()
                    university_data.Value = s_sum

                university_data.Checked = False
                university_data.Date = str(datetime.date.today())
                if criteria.File_Need:
                    if f'f{criteria.Id}' in request.FILES:
                        university_data.File = request.FILES[f'f{criteria.Id}']
                university_data.save()

        return redirect(request.build_absolute_uri(), request)
    else:
        university_data = University_Data.objects.filter(University_id_id=university, Year_id=Year.objects.filter().order_by().first())
        indicators = Indicator.objects.all()



        context = {'criteria': criterias, 'indicators': indicators,  'university_data': university_data, 'university': university, 'sub_criterias': sub_criterias}
        return render(request, "criteria.html", context)


def ranking_view(request):
    try:
        year = '2021'#str(datetime.datetime.now().year)
        if not year == str(Year.objects.filter().order_by('-Year').first()):
            y=Year(Year=year)
            y.save()
            y=Year.objects.latest('Id')
            categories = Category.objects.all().order_by('Id')
            for category in categories:
                id=category.pk
                category.pk = None
                category.Year_id = y
                category.save()
                c = Category.objects.latest('Id')
                groups = Group.objects.filter(Category_id_id=id).order_by('Id')
                print(groups.count())
                for group in groups:
                    id = group.pk
                    print('Nurlan')
                    group.pk = None
                    group.Year_id = y
                    group.Category_id = c
                    group.save()
                    g = Group.objects.latest('Id')
                    for criteria in Criteria.objects.filter(Group_id_id=id).order_by('Id'):

                        criteria.pk = None
                        criteria.Year_id = y
                        criteria.Group_id = g
                        criteria.save()
            # category = Category.objects.all()
            # criteria = Criteria.objects.all()
            # groups.update(Year=year)
            # groups.save()
        else:
            print('bye')

    except Exception as e:
        print(e)
    universities = University.objects.all()
    year = Year.objects.all().reverse()[1] #
    criterias = Criteria.objects.filter(Year_id=year)
    # print('sum'+ str(criterias.aggregate(Sum('Max_value'))))
    groups = Group.objects.filter(Year_id=year)
    categories = Category.objects.filter(Year_id=year)
    variables = []
    for criteria in criterias:
        x = criteria.VariableName
        if x != '' and x is not None:
            variables.append(x.replace(' ', ''))

    variables.sort(reverse=True)
    uarray = []
    parser = Parser()
    k=0
    v1=0
    for university in universities:
        value = 0
        for criteria in criterias:

            if criteria.Formula is not None and criteria.Formula != '':
                formula = criteria.Formula.replace(' ', '')
                try:
                    # print(formula)
                    if re.search('ri_max', formula, re.IGNORECASE):
                        formula =re.sub('ri_max',str(
                            University_Data.objects.filter(Criteria_id_id=criteria, Year_id=year).order_by('-Value').first().Value), formula,flags=re.IGNORECASE)
                    if re.search('ri', formula, re.IGNORECASE):
                        formula = re.sub('ri', str(
                            University_Data.objects.get(Criteria_id_id=criteria,University_id=university, Year_id=year).Value),
                                         formula, flags=re.IGNORECASE )
                except Exception as e:
                    # print(e)
                    value=0
                    continue
                year_id = 1
                try:
                    if criteria.Name == "Оценка ВУЗа выпускниками определяется опросником, требуется количество респондентов минимум  30% от количества  выпускников прошлого года":
                        #Подсчет анкеты для студента когда айди этого критерия = 10

                        a1=Student_form.objects.filter(Year_id = year_id,teachers_knowledge=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,teachers_knowledge=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,teachers_knowledge=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,teachers_knowledge=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,teachers_explaining=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,teachers_explaining=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,teachers_explaining=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,teachers_explaining=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,masters_knowledge=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,masters_knowledge=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,masters_knowledge=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,masters_knowledge=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,masters_explaining=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,masters_explaining=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,masters_explaining=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,masters_explaining=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,curators_work=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,curators_work=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,curators_work=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,curators_work=5, University_id=university.Id).count()*1
                        a2=Student_form.objects.filter(Year_id = year_id,ready=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,ready=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,ready=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,ready=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,rating=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,rating=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,rating=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,rating=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,skills=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,skills=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,skills=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,skills=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,connection=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,connection=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,connection=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,connection=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,oriented=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,oriented=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,oriented=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,oriented=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,help=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,help=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,help=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,help=5, University_id=university.Id).count()*1
                        b1=Student_form.objects.filter(Year_id = year_id,professional_skills=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,professional_skills=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,professional_skills=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,professional_skills=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,ability_improve=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,ability_improve=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,ability_improve=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,ability_improve=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,easy_adaptation=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,easy_adaptation=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,easy_adaptation=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,easy_adaptation=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,organization=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,organization=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,organization=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,organization=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,talking_skills=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,talking_skills=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,talking_skills=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,talking_skills=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,responsibility=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,responsibility=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,responsibility=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,responsibility=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,solving=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,solving=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,solving=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,solving=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,theory_using=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,theory_using=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,theory_using=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,theory_using=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,networking=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,networking=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,networking=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,networking=5, University_id=university.Id).count()*1
                        b2=Student_form.objects.filter(Year_id =year_id, same_major = "Doubt", University_id=university.Id).count()*0.5 + Student_form.objects.filter(Year_id =year_id, same_major = "Yes", University_id=university.Id).count()*1
                        b3=Student_form.objects.filter(Year_id =year_id, repeat_study = "Doubt", University_id=university.Id).count()*0.5 + Student_form.objects.filter(Year_id =year_id, repeat_study = "Yes", University_id=university.Id).count()*1
                        b4=Student_form.objects.filter(Year_id =year_id, satisfaction = "Doubt", University_id=university.Id).count()*0.5 + Student_form.objects.filter(Year_id =year_id, satisfaction = "Yes", University_id=university.Id).count()*1
                        v2=Student_form.objects.filter(Year_id = year_id,matching=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,matching=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,matching=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,matching=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,ability_improve=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,ability_improve=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,ability_improve=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,ability_improve=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,vacancy_lack=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,vacancy_lack=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,vacancy_lack=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,vacancy_lack=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,low_salary=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,low_salary=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,low_salary=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,low_salary=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,no_money=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,no_money=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,no_money=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,no_money=5, University_id=university.Id).count()*1
                        g1=Student_form.objects.filter(Year_id = year_id,own_skills=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,own_skills=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,own_skills=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,own_skills=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,new_idea=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,new_idea=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,new_idea=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,new_idea=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,adapt=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,adapt=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,adapt=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,adapt=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,time_man=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,time_man=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,time_man=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,time_man=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,talking_skills=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,talking_skills=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,talking_skills=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,talking_skills=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,responsibility_1=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,responsibility_1=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,responsibility_1=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,responsibility_1=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,solving_1=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,solving_1=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,solving_1=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,solving_1=5, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,using_1=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,using_1=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,using_1=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,using_1=5, University_id=university.Id).count()*1
                        d1=Student_form.objects.filter(Year_id = year_id,skills_using_1=2, University_id=university.Id).count()*0.25+Student_form.objects.filter(Year_id = year_id,skills_using_1=3, University_id=university.Id).count()*.5+Student_form.objects.filter(Year_id = year_id,skills_using_1=4, University_id=university.Id).count()*.75+Student_form.objects.filter(Year_id = year_id,skills_using_1=5, University_id=university.Id).count()*1
                        d2=Student_form.objects.filter(Year_id =year_id, own_spec = 3, University_id=university.Id).count()*0.5 + Student_form.objects.filter(Year_id =year_id, own_spec = 1, University_id=university.Id).count()*1
                        j1=(Student_form.objects.filter(Year_id =year_id, after_1 = 1, University_id=university.Id).count() + Student_form.objects.filter(Year_id =year_id, after_1 = 2, University_id=university.Id).count()+Student_form.objects.filter(Year_id =year_id, after_1 = 3, University_id=university.Id).count()+Student_form.objects.filter(Year_id =year_id, after_1 = 4, University_id=university.Id).count())*1
                        ind = a1 * 0.15+a2*0.15+b1*.1+b2*.1+b3*0.05+b4*0.05+v2*0.2+g1*0.05+d1*0.05+d2*0.05+j1*0.05
                        print('form students counted-',ind/100*5)

                        value += ind/100*5
                    elif criteria.Name =="Оценка работодателями сотрудничества вуза с работодателями (Опросник, не менне 100 респондентов)" and Student_form.objects.filter(Year_id = year_id, University_id=university.Id).count() >= 100:

                        a1=Student_form.objects.filter(Year_id = year_id,synthesis=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,synthesis=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,synthesis=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,using=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,using=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,using=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,time_management=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,time_management=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,time_management=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,base_knowledge=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,base_knowledge=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,base_knowledge=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,preparing=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,preparing=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,preparing=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,communication=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,communication=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,communication=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,lang_knowledge=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,lang_knowledge=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,lang_knowledge=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,comp_work=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,comp_work=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,comp_work=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,exploring=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,exploring=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,exploring=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,studying=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,studying=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,studying=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,inf_work=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,inf_work=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,inf_work=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,criticism=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,criticism=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,criticism=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,adapt=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,adapt=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,adapt=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,new_ideas=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,new_ideas=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,new_ideas=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,solving=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,solving=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,solving=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,decision=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,decision=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,decision=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,team_work=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,team_work=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,team_work=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,personal=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,personal=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,personal=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,leadership=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,leadership=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,leadership=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,team_disc_work=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,team_disc_work=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,team_disc_work=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,nospec_work=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,nospec_work=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,nospec_work=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,internat_work=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,internat_work=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,internat_work=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,indep_work=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,indep_work=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,indep_work=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,development=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,development=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,development=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,initiate=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,initiate=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,initiate=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,ethics=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,ethics=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,ethics=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,caring=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,caring=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,caring=4, University_id=university.Id).count()*1+\
                           Student_form.objects.filter(Year_id = year_id,ambition=2, University_id=university.Id).count()*.33+Student_form.objects.filter(Year_id = year_id,ambition=3, University_id=university.Id).count()*.66+Student_form.objects.filter(Year_id = year_id,ambition=4, University_id=university.Id).count()*1
                        value += a1/100*8
                        print("form emp counted-",a1/100*8)
                    elif criteria.Name == "Индекс цифровых навыков студентов (определяется из опросника для студентов)":
                        ds1=Dig_form.objects.filter(Year_id = year_id,printer=2, University_id=university.Id).count()*.3+\
                            Dig_form.objects.filter(Year_id = year_id,office=2, University_id=university.Id).count()*.30+\
                            Dig_form.objects.filter(Year_id = year_id,sm=2, University_id=university.Id).count()*.20+\
                            Dig_form.objects.filter(Year_id = year_id,internet=2, University_id=university.Id).count()*.10+\
                            Dig_form.objects.filter(Year_id = year_id,trust=2, University_id=university.Id).count()*.10

                        ds2=Dig_form.objects.filter(Year_id = year_id,portal=2, University_id=university.Id).count()*.25+\
                            Dig_form.objects.filter(Year_id = year_id,card=2, University_id=university.Id).count()*.2+\
                            Dig_form.objects.filter(Year_id = year_id,purchase=2, University_id=university.Id).count()*.2+\
                            Dig_form.objects.filter(Year_id = year_id,online=2, University_id=university.Id).count()*.1+\
                            Dig_form.objects.filter(Year_id = year_id,promotion=2, University_id=university.Id).count()*.25

                        ds3=Dig_form.objects.filter(Year_id = year_id,rid=2, University_id=university.Id).count()*.2+\
                            Dig_form.objects.filter(Year_id = year_id,encapsulation=2, University_id=university.Id).count()*.3+\
                            Dig_form.objects.filter(Year_id = year_id,language=2, University_id=university.Id).count()*.2+\
                            Dig_form.objects.filter(Year_id = year_id,program_lang=2, University_id=university.Id).count()*.2+\
                            Dig_form.objects.filter(Year_id = year_id,telemedicine=2, University_id=university.Id).count()*.1
                        dsdi=ds1*0.4+ds2*0.4+ds3*0.2
                        value+=dsdi/100*2.5
                        print("form dig counted-",dsdi/100*2.5)
                    else:
                        value += parser.parse(formula).evaluate({})/University_Data.objects.filter(Criteria_id_id=criteria, Year_id=year).order_by('-Value').first().Value * criteria.Max_value
                except Exception as e:
                    print(e)
                    try:
                        ar=[]
                        a=University.objects.all()
                        for each in a:
                            f1 = criteria.Formula
                            if re.search('ri', f1, re.IGNORECASE):
                                f1 = re.sub('ri', str(University_Data.objects.get(Criteria_id_id=criteria, University_id=each, Year_id=year).Value),f1, flags=re.IGNORECASE)
                            n1 = [
                                node.id for node in ast.walk(ast.parse(f1))
                                if isinstance(node, ast.Name)
                            ]
                            for x in n1:
                                # print(x)
                                cri = Criteria.objects.get(VariableName=str(x), Year_id=year)
                                # print(cri)
                                v1 = University_Data.objects.get(Criteria_id_id=cri, University_id=each, Year_id=year).Value
                                f1 = f1.replace(x, str(v1))


                            try:
                                # print(f1,'go')
                                v = parser.parse(f1).evaluate({})
                                # print(f1,'done')
                                ar.append(v)
                            except Exception as e:
                                print(e)
                        # ar=reversed(ar.sort())
                        # print(ar[0])
                    except Exception as e:
                        print(e)

                    names = [
                        node.id for node in ast.walk(ast.parse(formula))
                        if isinstance(node, ast.Name)
                    ]
                    ar.sort(reverse=True)
                    for x in names:
                        # print(crit.VariableName)
                        try:
                            # print(x)
                            crit = Criteria.objects.get(VariableName=str(x), Year_id=year)
                            var = University_Data.objects.get(Criteria_id_id=crit, University_id=university, Year_id=year).Value
                            if var is not None:
                                formula = formula.replace(x, str(var))

                            # print(formula)
                            # print(parser.parse(formula).evaluate({}) * criteria.Max_value)
                            try:
                                v1=value
                                value += parser.parse(formula).evaluate({})/ar[0]*criteria.Max_value
                                if criteria.Id== 5:
                                    print('crt', parser.parse(formula).evaluate({})/ar[0]*criteria.Max_value)
                            except Exception as e:
                                # print(formula)
                                v1 = value
                                k += 1
                                # print(formula)
                                # print('eval',parser.parse(formula).evaluate({}))
                                # print('ar',ar[0])

                            # print(value)
                            # print(ar[0])
                            # print(parser.parse(formula).evaluate({}))


                        except Exception as e:
                            print(1,e)
                # print(re.sub("ri", '1', re.sub("ri_max", '1', re.sub("\s", "", ))))

                # print(criteria.Max_value)

        # print(k)
        university_info = {
            'Name': university.Name,
            'Value': value,
            'Webaddress': university.WebAddress,
            'Logo': university.Logo
        }
        uarray.append(university_info)
        uarray= sorted(uarray, key=lambda k: k['Value'], reverse=True)
    u = uarray[:]
    p = []

    for arr in uarray:
        try:
            val = round(100 / float(u[0]['Value']) * float(arr['Value']), 2)
        except:
            val= 0
        university_info = {
            'Name': arr['Name'],
            'Value': val,
            'Webaddress': arr['Webaddress'],
            'Logo': arr['Logo']
        }
        p.append(university_info)
    context = {'year':year.Id, 'y': str(datetime.datetime.now().year), 'uarray': p,'categories': categories, 'groups': groups,'criterias': criterias, 'years': Year.objects.all().reverse()}
    return render(request, "ranking.html", context)


from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('/')

def login_view(request):
    if request.user.is_superuser:
        return redirect('/')
    elif request.user.groups.filter(name='comission').count():
        return redirect('/admin/form/university_data')
    elif request.user.groups.filter(name='university_rep').count():
        return redirect('/anketa')
    else:
        return redirect('/')
from django.http import HttpResponse


def ranking_by(request):
    year = request.GET.get('q', None)
    param = request.GET.get('c', None)

    if not param and not year :
        return ranking_view(request)
    criterias = Criteria.objects.none()
    if not year:
        year = Year.objects.filter(Year=str(datetime.datetime.now().year)).first()
    else:
        year = Year.objects.get(Id=year[1:])
        criterias = Criteria.objects.filter(Year_id=year)
    universities = University.objects.all()
    groups = Group.objects.filter(Year_id=year)
    categories = Category.objects.filter(Year_id=year)
    progress=0

    if param:
        if param[0]=='l':
            criterias = Criteria.objects.none()
            gs = Group.objects.filter(Category_id_id=param[1:], Year_id=year)
            for g in gs:
                criterias |= Criteria.objects.filter(Group_id_id=g, Year_id=year)
            ranking = f'Рейтинг за {year} год по уровню "{Category.objects.get(Id=param[1:]).Name}"'
        if param[0]=='g':
            progress = Group.objects.get(Id=param[1:]).Max_value
            criterias = Criteria.objects.filter(Group_id_id=param[1:], Year_id=year)
            ranking = f'Рейтинг за {year} год по группе "{Group.objects.get(Id=param[1:]).Name}"'
        if param[0]=='c':
            ranking = f'Рейтинг за {year} год по критерию "{Criteria.objects.get(Id=param[1:]).Name}"'
            progress= Criteria.objects.get(Id=param[1:]).Max_value
            criterias = Criteria.objects.filter(Id=param[1:], Year_id=year)
    else:
        ranking = f'Основной рейтинг за {year} год '
    if not criterias.count():
        return HttpResponse("Wrong request!")
    uarray = []
    parser = Parser()
    k=0
    for university in universities:
        value = 0
        for criteria in criterias:
            if criteria.Formula is not None and criteria.Formula != '':
                formula = criteria.Formula.replace(' ', '')
                try:
                    if re.search('ri_max', formula, re.IGNORECASE):
                        formula =re.sub('ri_max',str(
                            University_Data.objects.filter(Criteria_id_id=criteria, Year_id=year).order_by('-Value').first().Value), formula,flags=re.IGNORECASE)
                    if re.search('ri', formula, re.IGNORECASE):
                        formula = re.sub('ri', str(
                            University_Data.objects.get(Criteria_id_id=criteria,University_id=university, Year_id=year).Value),
                                         formula, flags=re.IGNORECASE)
                except Exception as e:
                    value=0
                    continue
                try:
                    value += parser.parse(formula).evaluate({})/University_Data.objects.filter(Criteria_id_id=criteria, Year_id=year).order_by('-Value').first().Value * criteria.Max_value
                except Exception as e:
                    try:
                        a=University.objects.all()
                        ar=[]
                        for each in a:
                            print(each.Name)
                            f1 = str(criteria.Formula)
                            if re.search('ri', f1, re.IGNORECASE):
                                f1 = re.sub('ri', str(University_Data.objects.get(Criteria_id_id=criteria, University_id=each, Year_id=year).Value),f1, flags=re.IGNORECASE)

                            n1 = [
                                node.id for node in ast.walk(ast.parse(f1))
                                if isinstance(node, ast.Name)
                            ]
                            for x in n1:
                                cri = Criteria.objects.get(VariableName=str(x), Year_id=year)

                                v1 = University_Data.objects.get(Criteria_id_id=cri, University_id=each, Year_id=year).Value
                                f1 = f1.replace(x, str(v1))
                            try:
                                v = parser.parse(f1).evaluate({})
                                print(f1)
                                ar.append(v)
                            except Exception as e:
                                print(e)
                            print(ar)

                    except Exception as e:
                        print(e)

                    names = [
                        node.id for node in ast.walk(ast.parse(formula))
                        if isinstance(node, ast.Name)
                    ]
                    ar.sort(reverse=True)
                    for x in names:
                        # print(crit.VariableName)
                        try:
                            # print(x)
                            crit = Criteria.objects.get(VariableName=str(x), Year_id=year)
                            var = University_Data.objects.get(Criteria_id_id=crit, University_id=university, Year_id=year).Value

                            if var is not None:
                                formula = formula.replace(x, str(var))

                            try:
                                print(formula,'/',ar[0],'*',criteria.Max_value,' = ', parser.parse(formula).evaluate({})/ar[0]*criteria.Max_value)
                                value += parser.parse(formula).evaluate({})/ar[0]*criteria.Max_value
                                print(ar[0])
                            except Exception as e:
                                k += 1
                        except Exception as e:
                            print(1,e)

        university_info = {
            'Name': university.Name,
            'Value': value,
            'Webaddress': university.WebAddress,
            'Logo': university.Logo
        }
        uarray.append(university_info)
    uarray= sorted(uarray, key=lambda k: k['Value'], reverse=True)
    u=uarray[:]
    p=[]
    for arr in uarray:
        try:
            val = round(100 / float(u[0]['Value']) * float(arr['Value']), 2)
        except:
            val= 0
        university_info = {
            'Name': arr['Name'],
            'Value': val,
            'Webaddress': arr['Webaddress'],
            'Logo': arr['Logo']
        }
        p.append(university_info)

    criterias = Criteria.objects.filter(Year_id=year)

    context = {'year':year.Id,'ranking':ranking,'y': year, 'uarray': p,'categories': categories, 'groups': groups,'criterias': criterias, 'request': request, 'years': Year.objects.all().reverse()}
    return render(request, "ranking.html", context)


def form_students(request):
    universities = University.objects.all()
    majors = Major.objects.all()
    if request.method == 'POST':
        data = request.POST.copy()
        names = [
            'teachers_knowledge', 'teachers_explaining', 'masters_knowledge', 'masters_explaining', 'curators_work',
            'ready','rating', 'skills', 'connection', 'oriented',
            'help', 'professional_skills', 'ability_improve', 'easy_adaptation', 'organization', 'talking_skills',
            'responsibility', 'solving','theory_using', 'theory_using', 'repeat_study', 'same_major', 'satisfaction',
            'start_working',
            'matching', 'lack', 'vacancy_lack', 'low_salary', 'no_money', 'work_search', 'success_search', 'new_idea',
            'adapt', 'time_man', 'talking_skills_', 'responsibility_', 'solving_', 'using_', 'skills_using_', 'why_',
            'after_', 'where_']
        for i in names:
            if data.get(i)== None:
                print('Not rated!',i)
                return render(request, "form_students.html", {'universities': universities, 'majors': majors, 'message1': "Не сохранено, заполните все поля!"})
        try:
            Student_form.objects.create(
                Year_id= Year.objects.get(Year='2020'),
                University_id = University.objects.get(Id=data.get('university_id')),
                fio= data.get('fio'),
                age = data.get('age'),
                gender = data.get('gender'),
                raddate = data.get('graddate'),
                Major_id = Major.objects.get(Id=data.get('major')),
                major = data.get('major1'),
                job = data.get('job'),
                position = data.get('position'),
                salary = data.get('salary'),
                name_university = data.get('level_of_education'),
                level_of_education = data.get('level_of_education'),
                study_terms = data.get('study_terms'),
                army_terms = data.get('army_terms'),
                maternity_leave_term = data.get('maternity_leave_term'),
                teachers_knowledge = data.get('teachers_knowledge'),
                teachers_explaining = data.get('teachers_explaining'),
                masters_knowledge = data.get('masters_knowledge'),
                masters_explaining = data.get('masters_explaining'),
                curators_work = data.get('curators_work'),
                ready = data.get('ready'),
                rating = data.get('rating'),
                skills = data.get('skills'),
                connection = data.get('connection'),
                oriented = data.get('oriented'),
                help = data.get('help'),
                professional_skills = data.get('professional_skills'),
                ability_improve = data.get('ability_improve'),
                easy_adaptation = data.get('easy_adaptation'),
                organization = data.get('organization'),
                talking_skills = data.get('talking_skills'),
                responsibility = data.get('responsibility'),
                solving = data.get('solving'),
                theory_using = data.get('theory_using'),
                networking = data.get('networking'),
                repeat_study = data.get('repeat_study'),
                same_major = data.get('same_major'),
                satisfaction = data.get('satisfaction'),
                start_working = data.get('start_working'),
                matching = data.get('matching'),
                lack = data.get('lack'),
                vacancy_lack = data.get('vacancy_lack'),
                low_salary = data.get('low_salary'),
                no_money = data.get('no_money'),
                work_search = data.get('work_search'),
                success_search = data.get('success_search'),
                own_skills = data.get('own_skills'),
                new_idea = data.get('new_idea'),
                adapt = data.get('adapt'),
                time_man = data.get('time_man'),
                talking_skills_1 = data.get('talking_skills_'),
                responsibility_1 = data.get('responsibility_'),
                solving_1 = data.get('solving_'),
                using_1 = data.get('using_'),
                skills_using_1 = data.get('skills_using_'),
                own_spec = data.get('own_spec'),
                why_1 = data.get('why_'),
                after_1 = data.get('after_'),
                where_1 = data.get('where_')
            )
        except Exception as e:
            print(e,'hello')
            universities = University.objects.all()
            return render(request, "form_students.html", {'universities': universities, 'majors': majors, 'message1': "Не сохранено, заполните правильно!"})

        return render(request, "form_students.html", {'universities': universities, 'majors': majors,'message1': 'Успешно сохранено!'})
    else:
        universities = University.objects.all()
        return render(request,"form_students.html", { 'universities': universities, 'majors': majors })

def form_employers(request):
    universities = University.objects.all()
    majors = Major.objects.all()
    if request.method == 'POST':
        data = request.POST.copy()
        names = [
            'synthesis', 'using', 'time_management', 'base_knowledge', 'preparing',
            'communication','lang_knowledge', 'comp_work', 'exploring', 'studying',
            'inf_work', 'criticism', 'adapt', 'new_ideas', 'solving', 'decision',
            'team_work', 'personal', 'leadership', 'team_disc_work', 'nospec_work',
            'internat_work','indep_work', 'development', 'initiate', 'ethics',
            'caring', 'ambition']
        for i in names:
            if data.get(i)== None:
                return render(request, "form_employers.html", {'universities': universities, 'majors': majors, 'message1': "Не сохранено, заполните правильно!"})
        try:
            Emp_form.objects.create(
                Year_id= Year.objects.get(Year='2020'),
                University_id = University.objects.get(Id=data.get('university_id')),
                org_name= data.get('org_name'),
                e_number = data.get('e_number'),
                Major_id = Major.objects.get(Id=data.get('major')),
                position = data.get('position'),
                synthesis = data.get('synthesis'),
                using = data.get('using'),
                time_management = data.get('time_management'),
                base_knowledge = data.get('base_knowledge'),
                preparing = data.get('preparing'),
                communication = data.get('communication'),
                lang_knowledge = data.get('lang_knowledge'),
                comp_work = data.get('comp_work'),
                exploring = data.get('exploring'),
                studying = data.get('studying'),
                inf_work = data.get('inf_work'),
                criticism = data.get('criticism'),
                adapt = data.get('adapt'),
                new_ideas = data.get('new_ideas'),
                solving = data.get('solving'),
                decision = data.get('decision'),
                team_work = data.get('team_work'),
                personal = data.get('personal'),
                leadership = data.get('leadership'),
                team_disc_work = data.get('team_disc_work'),
                nospec_work = data.get('nospec_work'),
                internat_work = data.get('internat_work'),
                indep_work = data.get('indep_work'),
                development = data.get('development'),
                initiate = data.get('initiate'),
                ethics = data.get('ethics'),
                caring = data.get('caring'),
                ambition = data.get('ambition'))
        except Exception as e:
            print(e)
            universities = University.objects.all()
            return render(request, "form_employers.html", {'universities': universities, 'majors': majors})

        return render(request, "form_employers.html", {'universities': universities,'majors': majors,'message1': 'Успешно сохранено!'})
    else:
        universities = University.objects.all()
        return render(request,"form_employers.html", { 'universities': universities, 'majors': majors})

def form_digital_knowledge(request):
    universities = University.objects.all()
    if request.method == 'POST':
        data = request.POST.copy()
        names = [
            'printer', 'office', 'sm', 'internet', 'trust',
            'portal','card', 'purchase', 'online', 'promotion',
            'rid', 'encapsulation', 'language', 'program_lang', 'telemedicine']
        for i in names:
            if data.get(i)== None:
                return render(request, "form_digital_knowledge.html", {'universities': universities, 'message1': "Не сохранено, заполните правильно!"})
        try:
            Dig_form.objects.create(
                Year_id= Year.objects.get(Year='2020'),
                University_id = University.objects.get(Id=data.get('university_id')),
                printer= data.get('printer'),
                office = data.get('office'),
                sm = data.get('sm'),
                internet = data.get('internet'),
                trust = data.get('trust'),
                portal = data.get('portal'),
                card = data.get('card'),
                purchase = data.get('purchase'),
                online = data.get('online'),
                promotion = data.get('promotion'),
                rid = data.get('rid'),
                encapsulation = data.get('encapsulation'),
                language = data.get('language'),
                program_lang = data.get('program_lang'),
                telemedicine = data.get('telemedicine')
            )
        except Exception as e:
            print(e)
            universities = University.objects.all()
            return render(request, "form_digital_knowledge.html", {'universities': universities})

        return render(request, "form_digital_knowledge.html", {'universities': universities,'message1': 'Успешно сохранено!'})
    else:
        universities = University.objects.all()
        return render(request,"form_digital_knowledge.html", { 'universities': universities, })
