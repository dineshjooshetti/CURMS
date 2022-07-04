from django.urls import path
from . import views


urlpatterns = [
    path('create_program', views.create_program, name='create_program'),
]