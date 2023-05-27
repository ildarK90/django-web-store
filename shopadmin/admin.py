from django.contrib import admin
from .models import *
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, ModelForm
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportActionModelAdmin
from import_export import resources


class TestmodelResource(resources.ModelResource):
    class Meta:
        model = TestModel


class TestmodelAdmin(ImportExportActionModelAdmin):
    resource_class = TestmodelResource


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category


class CategoryAdmin(ImportExportActionModelAdmin):
    resource_class = CategoryResource



admin.site.register(TestModel, TestmodelAdmin)
admin.site.register(Category, CategoryAdmin)
