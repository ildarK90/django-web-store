from django.urls import path, include
from .views import *

urlpatterns = [
    path('products', ProductList.as_view()),
    path('notebook_detailed/<int:pk>', NoteBookDetailed.as_view()),
    path('prod_detailed/<str:model>/<int:pk>', ProductDet.as_view()),
    path('prod_category/<str:model>', ProductCategory.as_view()),
    path('prod_delete', DeletefromCart.as_view()),
    path('category_edit/<int:pk>', EditCategory.as_view()),
    path('cart_edit', EditCart.as_view()),
    path('cart_list', CartList.as_view()),
    path('cartprod_list', CartProdList.as_view()),
    path('cartprod/<int:pk>', CartProdDetail.as_view(), name='cartprod-detail'),
    path('addtocart/<int:pk>', AddtoCart.as_view(), name='addtocart'),
]