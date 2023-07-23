from django.urls import path, include
from .views import *

urlpatterns = [

    path('dumpdata', ExportCSView.as_view(), name='exportcsv'),
    path('deletetest', DeleteProducts.as_view(), name='delete-all'),
    path('exportcsv', CSVexport.as_view(), name='csv'),
    path('categories', CategoryDetailView.as_view(), name='category_list'),

]
