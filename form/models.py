# from cms.models.pluginmodel import models.Model
from django.db import models
from django.contrib.auth.models import User
import datetime


# Create your models here.


class Category(models.Model):
    Id = models.AutoField(primary_key=True)
    Name = models.TextField(null=True)
    Max_value = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.Name

    class Meta:
        ordering = ['pk']


class Group(models.Model):
    Id = models.AutoField(primary_key=True)
    Name = models.TextField(null=True)
    Max_value = models.FloatField(null=True, blank=True)
    Category_id = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.Name

    class Meta:
        ordering = ['pk']


class Indicator(models.Model):
    Id = models.AutoField(primary_key=True)
    Name = models.TextField(null=True)
    Sign = models.CharField(max_length=3)

    def __str__(self):
        return self.Name

    class Meta:
        ordering = ['pk']


class Criteria(models.Model):
    Id = models.AutoField(primary_key=True)
    Name = models.TextField(null=True)
    Max_value = models.FloatField(null=True)
    Indicator_id = models.ForeignKey(Indicator, null=True, on_delete=models.SET_NULL)
    Group_id = models.ForeignKey(Group, null=True, on_delete=models.SET_NULL)
    File_Need = models.BooleanField(default=False)
    Formula = models.TextField(null=True, blank=True)
    VariableName = models.TextField(null=True, blank=True, unique=True)

    def __str__(self):
        return self.Name

    class Meta:
        ordering = ['pk']


class University(models.Model):
    Id = models.AutoField(primary_key=True)
    Name = models.TextField()
    Logo = models.ImageField(null=True, upload_to='logos')
    WebAddress = models.TextField(null=True)
    def __str__(self):
        return self.Name

    class Meta:
        ordering = ['pk']


class University_Data(models.Model):
    Id = models.AutoField(primary_key=True)
    University_id = models.ForeignKey(University, null=True, on_delete=models.SET_NULL)
    Criteria_id = models.ForeignKey(Criteria, null=True, on_delete=models.SET_NULL)
    Value = models.FloatField(null=True)
    File = models.FileField(null=True, upload_to='files')
    Date = models.DateField(default=datetime.date.today)
    Checked = models.BooleanField(default=False)

    class Meta:
        ordering = ['pk']

# class User(models.Model):
#     Id = models.AutoField(primary_key=True)



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name='info')
    University_id = models.ForeignKey(University, null=True, on_delete=models.SET_NULL)
    PhoneNumber = models.TextField(null=True, blank=True)
    Position = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.user.username

