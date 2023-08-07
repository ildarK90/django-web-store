import os

from django.contrib.admin import ModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views import View
from django.apps import apps
from django.contrib import messages
from django.views.generic import ListView

from .forms import MyForm
from .utils import getjson_to_csv, post_to_csv, normal_json, download_csv
from .models import TestModel

from market.models import Category

class JsonToCsv(View):

    def post(self, request):
        if request.FILES.get('myfile'):
            file = request.FILES['myfile']
            name, _ = os.path.splitext(request.FILES[u'myfile'].name)
            post_to_csv(file, name)
            return HttpResponseRedirect('dumpdata')
        else:
            messages.add_message(request, messages.INFO, 'Спасибо за заказ! Hui')
            return HttpResponseRedirect('dumpdata')


class ExportCSView(View):
    template_name = 'export_csv.html'

    def get(self, request):
        print(mod)
        form = MyForm(request.GET or None)
        app_models = apps.get_app_config('market').get_models()
        # print(app_models)
        # for instance in app_models:
        #     content_type = ContentType.objects.get_for_model(instance.__class__)
        # content_type = ContentType.objects.get(Category)
        model_list = ['Category', 'smartphones', 'notebook', 'Cart', 'CartProduct']
        # content_type = ContentType.objects.get(model='category')
        context = {
            "models": model_list,
            "form": form,
        }

        if request.GET and "json_to_csv" in request.GET:
            model = request.GET['field']
            getjson_to_csv(model)

            return HttpResponseRedirect('dumpdata')

        if request.GET and "save_csv" in request.GET:
            model = request.GET['field']
            data = download_csv(ModelAdmin, request, model)

            return HttpResponse(data, content_type='text/csv')

        return render(request, 'export_csv.html', context)

    def post(self, request):
        if request.method == 'POST' and request.FILES.get('json_file'):
            json_file = request.FILES['json_file']
            name = request.FILES[u'json_file'].name
            normal_json(json_file, name, 200)
            # json_filename = request.FILES[u'json_file'].name
            # normal_json(json_file, json_filename)
            # fs = FileSystemStorage()
            # filename = fs.save(myfile.name, myfile)
            # uploaded_file_url = fs.url(filename)
            # file_to_csv2(src,myfile)
            return HttpResponseRedirect('dumpdata')


class CSVexport(View):
    def get(self, request):
        data = download_csv(ModelAdmin, request, TestModel)
        return HttpResponse(data, content_type='text/csv')


class CategoryDetailView(ListView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'listprod.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        return context