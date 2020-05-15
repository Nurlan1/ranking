from django.contrib import admin
from .models import Category, Group, Criteria, Indicator, University, University_Data, UserProfile


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('Id', 'Name', 'Max_value')


class GroupAdmin(admin.ModelAdmin):
    list_display = ('Id', 'Name', 'Max_value', 'Category_id')


class CriteriaAdmin(admin.ModelAdmin):
    list_display = ('Id', 'Name', 'Max_value', 'Indicator_id', 'Group_id', 'File_Need', 'Formula', 'VariableName')


class IndicatorAdmin(admin.ModelAdmin):
    list_display = ('Id', 'Name', 'Sign')


class UniversityAdmin(admin.ModelAdmin):
    list_display = ('Id', 'Name', 'Logo', 'WebAddress')


class University_DataAdmin(admin.ModelAdmin):
    list_display = ('University_id', 'Criteria_id', 'Value', 'File', 'Date', 'Checked')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Criteria, CriteriaAdmin)
admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(University, UniversityAdmin)
admin.site.register(University_Data, University_DataAdmin)
admin.site.register(UserProfile)

# Register your models here.
