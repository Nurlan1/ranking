from django.shortcuts import render, render_to_response, redirect
from .models import Criteria, Indicator, Group, Category, University_Data,UserProfile, User, University
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
import ast
from django.contrib import messages
import re
from py_expression_eval import Parser
from django.db.models import Max, Sum


# Create your views here.
def form_render_view(request, mes=0):
    criterias = Criteria.objects.all()
    university = University.objects.get(Id=request.user.info.University_id.Id)

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

            #
            # filler
            # position
            # phonenumber

            if f'{criteria.Id}' in data:
                university_data = University_Data.objects.filter(University_id=university, Criteria_id=criteria).first()
                if not university_data:
                    university_data = University_Data.objects.create(Value=1)
                university_data.University_id_id = university
                university_data.Criteria_id_id = criteria.Id
                university_data.Value = data.get(f'{criteria.Id}') if data.get(f'{criteria.Id}') is not '' else None
                university_data.Checked = False
                university_data.Date = str(datetime.date.today())
                if criteria.File_Need:
                    if f'f{criteria.Id}' in request.FILES:
                        university_data.File = request.FILES[f'f{criteria.Id}']

                university_data.save()
        return redirect(request.build_absolute_uri(), request)
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

        context = {'criteria': criterias, 'indicators': indicators, 'categories': category, 'groups': groups,
                   'page': category, 'university_data': university_data, 'university': university}
        return render(request, "criteria.html", context)


def ranking_view(request):
    universities = University.objects.all()
    criterias = Criteria.objects.all()
    groups = Group.objects.all()
    categories = Category.objects.all()
    # for group in groups:
    #     print(group.Id,group.Max_value,Criteria.objects.filter(Group_id_id=group.Id).aggregate(Sum('Max_value')))

    variables = []
    for criteria in criterias:
        x = criteria.VariableName
        if x != '' and x is not None:
            variables.append(x.replace(' ', ''))
    # variables += ['ri_max', 'ri']

    variables.sort(reverse=True)
    uarray = []
    parser = Parser()
    k=0
    for university in universities:
        value = 0
        for criteria in criterias:

            if criteria.Formula is not None and criteria.Formula != '':
                formula = criteria.Formula.replace(' ', '')
                try:
                    # print(formula)
                    if re.search('ri_max', formula, re.IGNORECASE):
                        formula =re.sub('ri_max',str(
                            University_Data.objects.filter(Criteria_id_id=criteria).order_by('-Value').first().Value), formula,flags=re.IGNORECASE)
                    if re.search('ri', formula, re.IGNORECASE):
                        formula = re.sub('ri', str(
                            University_Data.objects.get(Criteria_id_id=criteria,University_id=university).Value),
                                         formula, flags=re.IGNORECASE)
                except Exception as e:
                    # print(e)
                    value=0
                    continue
                try:

                    value += parser.parse(formula).evaluate({})/University_Data.objects.filter(Criteria_id_id=criteria).order_by('-Value').first().Value * criteria.Max_value
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
                                f1 = re.sub('ri', str(University_Data.objects.get(Criteria_id_id=cri, University_id=each).Value),formula, flags=re.IGNORECASE)
                            n1 = [
                                node.id for node in ast.walk(ast.parse(f1))
                                if isinstance(node, ast.Name)
                            ]
                            for x in n1:
                                # print(x)
                                cri = Criteria.objects.get(VariableName=str(x))
                                # print(cri)
                                v1 = University_Data.objects.get(Criteria_id_id=cri, University_id=each).Value
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

                    for x in names:
                        # print(crit.VariableName)
                        try:
                            # print(x)
                            crit = Criteria.objects.get(VariableName=str(x))
                            var = University_Data.objects.get(Criteria_id_id=crit, University_id=university).Value



                            if var is not None:
                                formula = formula.replace(x, str(var))

                            # print(formula)
                            # print(parser.parse(formula).evaluate({}) * criteria.Max_value)
                            try:
                                value += parser.parse(formula).evaluate({})/ar[0]*criteria.Max_value
                                print(value,criteria)



                            except Exception as e:
                                # print(formula)
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
        print(k)
        university_info = {
            'Name': university.Name,
            'Value': value
        }
        uarray.append(university_info)

    context = {'seq': [1, 2, 3, 4], 'uarray': uarray,'categories': categories, 'groups': groups,'criterias': criterias}
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
def ranking_by(request, param):

    universities = University.objects.all()
    groups = Group.objects.all()
    categories = Category.objects.all()
    criterias = Criteria.objects.none()
    progress=0
    if param[0]=='l':
        progress=Category.objects.get(Id=param[1:]).Max_value
        gs = Group.objects.filter(Category_id_id=param[1:])
        for g in gs:
            criterias |= Criteria.objects.filter(Group_id_id=g)

    if param[0]=='g':
        progress = Group.objects.get(Id=param[1:]).Max_value
        criterias = Criteria.objects.filter(Group_id_id=param[1:])
    if param[0]=='c':
        progress= Criteria.objects.get(Id=param[1:]).Max_value
        criterias = Criteria.objects.filter(Id=param[1:])
    print(param[1:])
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
                            University_Data.objects.filter(Criteria_id_id=criteria).order_by('-Value').first().Value), formula,flags=re.IGNORECASE)
                    if re.search('ri', formula, re.IGNORECASE):
                        formula = re.sub('ri', str(
                            University_Data.objects.get(Criteria_id_id=criteria,University_id=university).Value),
                                         formula, flags=re.IGNORECASE)
                except Exception as e:
                    value=0
                    continue
                try:
                    value += parser.parse(formula).evaluate({})/University_Data.objects.filter(Criteria_id_id=criteria).order_by('-Value').first().Value * criteria.Max_value
                except Exception as e:
                    try:
                        ar=[]
                        a=University.objects.all()
                        for each in a:
                            f1 = criteria.Formula
                            if re.search('ri', f1, re.IGNORECASE):
                                f1 = re.sub('ri', str(University_Data.objects.get(Criteria_id_id=cri, University_id=each).Value),formula, flags=re.IGNORECASE)
                            n1 = [
                                node.id for node in ast.walk(ast.parse(f1))
                                if isinstance(node, ast.Name)
                            ]
                            for x in n1:
                                cri = Criteria.objects.get(VariableName=str(x))
                                v1 = University_Data.objects.get(Criteria_id_id=cri, University_id=each).Value
                                f1 = f1.replace(x, str(v1))
                            try:
                                v = parser.parse(f1).evaluate({})
                                ar.append(v)
                            except Exception as e:
                                print(e)

                    except Exception as e:
                        print(e)

                    names = [
                        node.id for node in ast.walk(ast.parse(formula))
                        if isinstance(node, ast.Name)
                    ]

                    for x in names:
                        # print(crit.VariableName)
                        try:
                            # print(x)
                            crit = Criteria.objects.get(VariableName=str(x))
                            var = University_Data.objects.get(Criteria_id_id=crit, University_id=university).Value

                            if var is not None:
                                formula = formula.replace(x, str(var))

                            try:
                                value += parser.parse(formula).evaluate({})/ar[0]*criteria.Max_value
                            except Exception as e:
                                k += 1
                        except Exception as e:
                            print(1,e)

        university_info = {
            'Name': university.Name,
            'Value': 100/progress*value
        }
        uarray.append(university_info)
    criterias = Criteria.objects.all()

    context = {'seq': [1, 2, 3, 4], 'uarray': uarray,'categories': categories, 'groups': groups,'criterias': criterias, 'request': request}
    return render(request, "ranking.html", context)