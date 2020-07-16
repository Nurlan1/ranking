from django.contrib import admin
from .models import Category, Group, Criteria, Indicator, University, University_Data, UserProfile, Year
from django.forms import TextInput, Textarea
from django.db import models


class YearAdmin(admin.ModelAdmin):
    list_display = ('Id', 'Year')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('Id', 'Name', 'Max_value', 'Year_id')
    list_filter = ['Year_id']


class GroupAdmin(admin.ModelAdmin):
    list_display = ('Id', 'Name', 'Max_value', 'Category_id', 'Year_id')
    list_filter = ['Year_id']


class CriteriaAdmin(admin.ModelAdmin):
    list_display = (
    'Id', 'Name', 'Max_value', 'Indicator_id', 'Group_id', 'Formula', 'Year_id', 'File_Need', 'VariableName')
    list_editable = ('Name', 'Max_value', 'Indicator_id', 'Group_id', 'Formula', 'Year_id', 'File_Need', 'VariableName')
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '200'})},
        models.TextField: {'widget': Textarea(
            attrs={'rows': 1,
                   'cols': 40,
                   'style': 'width: 100em;'})},
    }
    search_fields = ('Id', 'Name')
    list_filter = ['Year_id']



class IndicatorAdmin(admin.ModelAdmin):
    list_display = ('Id', 'Name', 'Sign')
    list_editable = ('Name', 'Sign')
    search_fields = ('Id', 'Name')


class UniversityAdmin(admin.ModelAdmin):
    list_display = ('Id', 'Name', 'Logo', 'WebAddress')
    list_editable = ('Name', 'Logo', 'WebAddress')
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '200'})},
        models.TextField: {'widget': Textarea(
            attrs={'rows': 1,
                   'cols': 40,
                   'style': 'width: 100em;'})},
    }
    search_fields = ('Id', 'Name')


class University_DataAdmin(admin.ModelAdmin):
    list_display = ('Id', 'University_id', 'Criteria_id', 'Value', 'File', 'Date', 'Checked', 'Year_id')
    list_editable = ('Criteria_id', 'Value', 'Checked')
    search_fields = ('Id', 'Name')
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '200'})},
        models.TextField: {'widget': Textarea(
            attrs={'rows': 1,
                   'cols': 40,
                   'style': 'width: 100em;'})},
    }
    list_filter = ['Year_id']


admin.site.register(Year, YearAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Criteria, CriteriaAdmin)
admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(University, UniversityAdmin)
admin.site.register(University_Data, University_DataAdmin)
admin.site.register(UserProfile)

# Register your models here.
