from django.urls import path, include
from .views import *

urlpatterns = [

    path('dumpdata', ExportCSView.as_view(), name='exportcsv'),
    path('deletetest', DeleteProducts.as_view(), name='delete'),
    path('exportcsv', CSVexport.as_view(), name='csv'),

]
