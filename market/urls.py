"""shop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [

    path('api/',include('rest.urls')),
    path('', BaseView.as_view(), name='home'),
    path('products/<str:ct_model>/<str:slug>', ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:slug>', CategoryDetailView.as_view(), name='category_detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<str:ct_model>/<str:slug>', AddToCartView.as_view(), name='add_to_cart'),
    path('delete_cartproduct/<str:ct_model>/<str:slug>', DeleteFromCartView.as_view(), name='delete_cartproduct'),
    path('change-qty/<str:ct_model>/<str:slug>', ChangeQTYView.as_view(), name='change_qty'),
    path('del/<str:ct_model>/<str:product_slug>', delete_pr, name='delete_pr'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', OrderView.as_view(), name='order'),
    path('make-order/', MakeOrderView.as_view(), name='make_order')

]
