# from cms.models.pluginmodel import models.Model
from django.db import models
from django.contrib.auth.models import User
import datetime



class Year(models.Model):
    Id = models.AutoField(primary_key=True)
    Year = models.CharField(verbose_name='Год', max_length=4)

    def __str__(self):
        return self.Year

    class Meta:
        ordering = ['pk']
        verbose_name = 'Год'
        verbose_name_plural = 'Годы'


class Category(models.Model):
    Id = models.AutoField(primary_key=True)
    Name = models.TextField(null=True, blank=False, verbose_name='Название⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀')
    Max_value = models.FloatField(null=True, blank=True, verbose_name='Максимальное значение')
    Year_id = models.ForeignKey(Year, null=True, on_delete=models.SET_NULL, verbose_name='Год')

    def __str__(self):
        return self.Name

    class Meta:
        ordering = ['pk']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Group(models.Model):
    Id = models.AutoField(primary_key=True)
    Name = models.TextField(null=True, blank=False, verbose_name='Название⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀')
    Max_value = models.FloatField(null=True, blank=True, verbose_name='Максимальное значение')
    Category_id = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, verbose_name='Категория')
    Year_id = models.ForeignKey(Year, null=True, on_delete=models.SET_NULL, verbose_name='Год')

    def __str__(self):
        return self.Name

    class Meta:
        ordering = ['pk']
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Indicator(models.Model):
    Id = models.AutoField(primary_key=True)
    Name = models.TextField(null=True, verbose_name='Название')
    Sign = models.CharField(max_length=3, verbose_name='Знак')

    def __str__(self):
        return self.Name

    class Meta:
        ordering = ['pk']
        verbose_name = 'Индикатор'
        verbose_name_plural = 'Индикаторы'


class Criteria(models.Model):
    Id = models.AutoField(primary_key=True)
    Name = models.TextField(null=True, blank=False, verbose_name='Название⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀')
    Max_value = models.FloatField(null=True, blank=True, verbose_name='Макс знач')
    Indicator_id = models.ForeignKey(Indicator, null=True, on_delete=models.SET_NULL, verbose_name='Индикатор')
    Group_id = models.ForeignKey(Group, null=True, on_delete=models.SET_NULL, verbose_name='Группа')
    File_Need = models.BooleanField(default=False, verbose_name='Файл')
    Formula = models.TextField(null=True, blank=True, verbose_name='⠀⠀⠀⠀⠀Формула⠀⠀⠀⠀⠀')
    VariableName = models.TextField(null=True, blank=True, verbose_name='Название переменной')
    Year_id = models.ForeignKey(Year, null=True, on_delete=models.SET_NULL, verbose_name='Год')

    def __str__(self):
        return self.Name

    class Meta:
        ordering = ['pk']
        verbose_name = 'Критерий'
        verbose_name_plural = 'Критерии'


class University(models.Model):
    Id = models.AutoField(primary_key=True)
    Name = models.TextField(verbose_name='Название')
    Logo = models.ImageField(null=True, upload_to='logos', verbose_name='Логотип')
    WebAddress = models.TextField(null=True, verbose_name='Адрес сайта')

    def __str__(self):
        return self.Name

    class Meta:
        ordering = ['pk']
        verbose_name = 'Университет'
        verbose_name_plural = 'Университеты'




class University_Data(models.Model):
    Id = models.AutoField(primary_key=True)
    University_id = models.ForeignKey(University, null=True, on_delete=models.SET_NULL, verbose_name='Университет')
    Criteria_id = models.ForeignKey(Criteria, null=True, on_delete=models.SET_NULL, verbose_name='Критерий')
    Value = models.FloatField(null=True, verbose_name='Значение')
    File = models.FileField(null=True, upload_to='files', verbose_name='Файл')
    Date = models.DateField(default=datetime.date.today, verbose_name='Дата')
    Checked = models.BooleanField(default=False, verbose_name='Проверка')
    Year_id = models.ForeignKey(Year, null=True, on_delete=models.SET_NULL, verbose_name='Год')
    # Comment = models.TextField(null=True, verbose_name='Комментарий')

    class Meta:
        ordering = ['pk']
        verbose_name = 'Данные университета'
        verbose_name_plural = 'Данные университетов'



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='info')
    University_id = models.ForeignKey(University, null=True, on_delete=models.SET_NULL, verbose_name='Университет')
    PhoneNumber = models.TextField(null=True, blank=True, verbose_name='Номер телефона')
    Position = models.TextField(null=True, blank=True, verbose_name='Должность')

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ['pk']
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'


class Sub_Criteria(models.Model):
    Id = models.AutoField(primary_key=True)
    Criteria_id = models.ForeignKey(Criteria, null=True, on_delete=models.SET_NULL, verbose_name='Критерий', related_name='sub_crits')
    Name = models.TextField(verbose_name='Название')
    Max_value = models.FloatField(null=True, verbose_name='Значение')


    class Meta:
        db_table='sub_crits'


class Sub_Data(models.Model):
    Id = models.AutoField(primary_key=True)
    Sub_criteria_id = models.ForeignKey(Sub_Criteria, null=True, on_delete=models.SET_NULL, verbose_name='Под Критерий', related_name='sub_data')
    University_id = models.ForeignKey(University, null=True, on_delete=models.SET_NULL, verbose_name='Университет')
    Value = models.BooleanField(null=True, verbose_name='Значение')
    Year_id=models.ForeignKey(Year, null=True, on_delete=models.SET_NULL, verbose_name='Год')

class Major(models.Model):
    Id = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=150, verbose_name='Название')
    class Meta:
        ordering = ['pk']
        verbose_name = 'Специальность'
        verbose_name_plural = 'Специальности'


class Student_form(models.Model):
    Id = models.AutoField(primary_key=True)
    University_id = models.ForeignKey(University, null=True, on_delete=models.SET_NULL, verbose_name='Университет')
    Year_id = models.ForeignKey(Year, null=True, on_delete=models.SET_NULL, verbose_name='Год')
    Major_id = models.ForeignKey(Major, null=True, on_delete=models.SET_NULL, verbose_name='Специальность', default=None)
    major = models.TextField()
    fio = models.TextField()
    age = models.IntegerField()
    gender = models.TextField()
    raddate = models.TextField()
    job = models.TextField()
    position = models.TextField()
    salary = models.TextField()
    name_university = models.TextField()
    level_of_education = models.IntegerField()
    study_terms = models.TextField()
    army_terms = models.TextField()
    maternity_leave_term = models.TextField()
    teachers_knowledge = models.IntegerField()
    teachers_explaining = models.IntegerField()
    masters_knowledge = models.IntegerField()
    masters_explaining = models.IntegerField()
    curators_work = models.IntegerField()
    ready = models.IntegerField()
    rating = models.IntegerField()
    skills = models.IntegerField()
    connection = models.IntegerField()
    oriented = models.IntegerField()
    help = models.IntegerField()
    professional_skills = models.IntegerField()
    ability_improve = models.IntegerField()
    easy_adaptation = models.IntegerField()
    organization = models.IntegerField()
    talking_skills = models.IntegerField()
    responsibility = models.IntegerField()
    solving = models.IntegerField()
    theory_using = models.IntegerField()
    networking = models.IntegerField()
    repeat_study  = models.CharField(max_length=10)
    same_major = models.CharField(max_length=10)
    satisfaction = models.CharField(max_length=10)
    start_working = models.IntegerField()
    matching = models.IntegerField()
    lack = models.IntegerField()
    vacancy_lack = models.IntegerField()
    low_salary = models.IntegerField()
    no_money = models.IntegerField()
    work_search = models.IntegerField()
    success_search = models.IntegerField()
    own_skills = models.IntegerField()
    new_idea = models.IntegerField()
    adapt = models.IntegerField()
    time_man = models.IntegerField()
    talking_skills_1 = models.IntegerField()
    responsibility_1 = models.IntegerField()
    solving_1 = models.IntegerField()
    using_1 = models.IntegerField()
    skills_using_1 = models.IntegerField()
    own_spec = models.IntegerField()
    why_1 = models.IntegerField()
    after_1 = models.IntegerField()
    where_1 = models.IntegerField()

class Emp_form(models.Model):
    Id = models.AutoField(primary_key=True)
    University_id = models.ForeignKey(University, null=True, on_delete=models.SET_NULL, verbose_name='Университет')
    Year_id = models.ForeignKey(Year, null=True, on_delete=models.SET_NULL, verbose_name='Год')
    Major_id = models.ForeignKey(Major, null=True, on_delete=models.SET_NULL, verbose_name='Специальность', default=None)
    org_name = models.TextField()
    e_number = models.IntegerField()
    position = models.TextField()
    salary = models.TextField()
    synthesis = models.IntegerField()
    using = models.IntegerField()
    time_management = models.IntegerField()
    base_knowledge = models.IntegerField()
    preparing = models.IntegerField()
    communication = models.IntegerField()
    lang_knowledge = models.IntegerField()
    comp_work = models.IntegerField()
    exploring = models.IntegerField()
    studying = models.IntegerField()
    inf_work = models.IntegerField()
    criticism = models.IntegerField()
    adapt = models.IntegerField()
    new_ideas = models.IntegerField()
    solving = models.IntegerField()
    decision = models.IntegerField()
    team_work = models.IntegerField()
    personal = models.IntegerField()
    leadership = models.IntegerField()
    team_disc_work = models.IntegerField()
    nospec_work = models.IntegerField()
    internat_work = models.IntegerField()
    indep_work = models.IntegerField()
    development  = models.IntegerField()
    initiate = models.IntegerField()
    ethics = models.IntegerField()
    caring = models.IntegerField()
    ambition = models.IntegerField()

class Dig_form(models.Model):
    University_id = models.ForeignKey(University, null=True, on_delete=models.SET_NULL, verbose_name='Университет')
    Year_id = models.ForeignKey(Year, null=True, on_delete=models.SET_NULL, verbose_name='Год')
    printer = models.IntegerField()
    office = models.IntegerField()
    sm = models.IntegerField()
    internet = models.IntegerField()
    trust = models.IntegerField()
    portal = models.IntegerField()
    card = models.IntegerField()
    purchase = models.IntegerField()
    online = models.IntegerField()
    promotion = models.IntegerField()
    rid = models.IntegerField()
    encapsulation = models.IntegerField()
    language = models.IntegerField()
    program_lang = models.IntegerField()
    telemedicine = models.IntegerField()
