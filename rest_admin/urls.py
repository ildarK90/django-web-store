from django.urls import path, include
from .views import *

urlpatterns = [
    path('notebook_detailed/<int:pk>', NoteBookDetailed.as_view()),
    path('notebook_detailed', NoteBookDetailed.as_view()),
    path('smartphone_update/<int:pk>', SmartphoneEdit.as_view()),
    path('smartphone_update', SmartphoneEdit.as_view()),
    path('smart_update', SmartUpdate.as_view()),
    path('smart_update/<int:pk>', SmartUpdate.as_view()),
    path('category_edit', EditCategory.as_view()),
    path('category_edit/<int:pk>', EditCategory.as_view()),
]