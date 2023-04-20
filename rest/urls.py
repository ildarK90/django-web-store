from django.urls import path, include
from .views import *

urlpatterns = [
    path('products_list/<str:slug>', ProductList.as_view(),name='cat_prod'),
    path('products/<str:model>',GeneralViewSet.as_view({'get':'list'}),name='category_product'), # выполнено с помощью динамического сериалайзера
    path('latest_products', LatestProductsList.as_view()), # Выполненно  с помощью библиотеки для нескольких сериалайзеров
    path('prod_detailed/<str:model>/<int:pk>', ProductDet.as_view()), #без сериалайзера
    path('prod_category/<str:model>', ProductCategory.as_view()), # Выполнено без сериалазйера
    path('categories',CategoryView.as_view()),
    # path('categ_product/<str:ct_model>', CategoryProductView.as_view()), #Нужно доделать, динамически менять модель товара
    path('prod_delete', DeletefromCart.as_view()),
    path('cart_edit', EditCart.as_view()),
    path('cartprod_list', CartProdList.as_view()),
    path('cartprod_list/<int:pk>', CartProdList.as_view()),
    path('cartprod/<int:pk>', CartProdDetail.as_view(), name='cartprod-detail'),
    # path('cartprod/<str:ct_model>/<str:product_slug>', CartProdDetail.as_view(), name='cartprod-detail-add'),
    path('cartprod/<int:pk>', CartProdDetail.as_view(), name='cartprod-delete'),
    path('addtocart/<str:ct_model>/<str:product_slug>', AddtoCart.as_view(), name='addtocart'),
    path('change_qty/<int:pk>',ChangeQTY.as_view(),name='changeqty'),
    path('orders',OrderView.as_view(),name='orders')
    
]