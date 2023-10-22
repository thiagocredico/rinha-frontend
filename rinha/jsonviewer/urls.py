from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.display_json_tree, name='display_json_tree'),
]
