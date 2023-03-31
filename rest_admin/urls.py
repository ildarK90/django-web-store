from django.urls import path, include
from .views import *

urlpatterns = [
    path('products', ProductList.as_view()),
    path('latest_products', LatestProductsList.as_view()),
    path('notebook_detailed/<int:pk>', NoteBookDetailed.as_view()),
    path('smartphone_update/<int:pk>', SmartphoneEdit.as_view()),
    path('smartphone_update', SmartphoneEdit.as_view()),
    path('smart_update', SmartUpdate.as_view()),
    path('smart_update/<int:pk>', SmartUpdate.as_view()),
    path('prod_detailed/<str:model>/<int:pk>', ProductDet.as_view()),
    path('prod_category/<str:model>', ProductCategory.as_view()),
    path('prod_delete', DeletefromCart.as_view()),
    path('category_edit', EditCategory.as_view()),
    path('category_edit/<int:pk>', EditCategory.as_view()),
    path('cart_edit', EditCart.as_view()),
    path('cart_list', CartList.as_view()),
    path('cartprod_list', CartProdList.as_view()),
    path('cartprod_list/<int:pk>', CartProdList.as_view()),
    path('cartprod/<int:pk>', CartProdDetail.as_view(), name='cartprod-detail'),
    path('cartprod/<str:ct_model>/<str:product_slug>', CartProdDetail.as_view(), name='cartprod-detail-add'),
    path('cartprod/<int:pk>', CartProdDetail.as_view(), name='cartprod-delete'),
    path('addtocart/<str:ct_model>/<str:product_slug>', AddtoCart.as_view(), name='addtocart'),
]