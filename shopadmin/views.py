import csv

from django.contrib.admin import ModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.apps import apps
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib import admin
from .forms import MyForm
from .utils import json_to_csv, file_to_csv, normal_json, del_id, download_csv
from .models import TestModel
import simplejson as json

from market.models import Category


class ExportCSView(View):

    def get(self, request):
        form = MyForm(request.POST or None)
        app_models = apps.get_app_config('market').get_models()
        print(app_models)
        # for instance in app_models:
        #     content_type = ContentType.objects.get_for_model(instance.__class__)
        # content_type = ContentType.objects.get(Category)
        model_list = ['Category', 'smartphones', 'notebook', 'Cart', 'CartProduct']
        # content_type = ContentType.objects.get(model='category')
        context = {
            "models": model_list,
            "form": form,
        }
        if request.GET:
            model = request.GET['field']
            json_to_csv(model)
            return HttpResponseRedirect('dumpdata')
        return render(request, 'export_csv.html', context)

    def post(self, request):
        if request.method == 'POST' and request.FILES.get('myfile'):
            myfile = request.FILES['myfile']
            name = request.FILES[u'myfile'].name
            file_to_csv(myfile, name)
            # fs = FileSystemStorage()
            # filename = fs.save(myfile.name, myfile)
            # uploaded_file_url = fs.url(filename)
            # file_to_csv2(src,myfile)
            return HttpResponseRedirect('dumpdata')
        elif request.method == 'POST' and request.FILES.get('json_file'):
            json_file = request.FILES['json_file']
            # del_id(json_file)
            normal_json(json_file,'testmodel_new')
            # json_filename = request.FILES[u'json_file'].name
            # normal_json(json_file, json_filename)
            # fs = FileSystemStorage()
            # filename = fs.save(myfile.name, myfile)
            # uploaded_file_url = fs.url(filename)
            # file_to_csv2(src,myfile)
            return HttpResponseRedirect('dumpdata')


class SendCSView(View):

    def post(self, request, *args, **kwargs):
        form = MyForm(request.POST or None)
        if form.is_valid():
            return HttpResponseRedirect('/checkout')


class DeleteProducts(View):
    def get(self, request):
        TestModel.objects.all().delete()
        return HttpResponseRedirect('dumpdata')


class CSVexport(View):

    def get(self, request):
        data = download_csv(ModelAdmin, request, TestModel.objects.all())
        return HttpResponse(data, content_type='text/csv')