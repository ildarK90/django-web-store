from django.urls import path, include
from .views import *

urlpatterns = [

    path('dumpdata', ExportCSView.as_view(), name='exportcsv'),
    path('exportcsv', CSVexport.as_view(), name='csv'),
    path('categories', CategoryDetailView.as_view(), name='category_list'),
    path('hui', JsonToCsv.as_view(), name='hui'),

]
