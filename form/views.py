from django.shortcuts import render, render_to_response, redirect
from .models import Criteria, Indicator, Group, Category, University_Data,UserProfile, User, University, Year, Sub_Criteria, Sub_Data
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
                try:

                    value += parser.parse(formula).evaluate({})/University_Data.objects.filter(Criteria_id_id=criteria, Year_id=year).order_by('-Value').first().Value * criteria.Max_value
                    # print(criteria, formula)
                    # print(value, criteria, formula)
                    # k += 1
                except Exception as e:
                    # print(e)
                    # print(formula)

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

# def calculating(formula, value):
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
    if request.method == 'POST':
        data = request.POST.copy()
    else:
        return render(request,"form_students.html")