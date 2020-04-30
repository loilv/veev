from django.urls import path
from . import views


urlpatterns = [
    path(r'', views.index, name='tool'),
    path('create/', views.create_video, name='create')
]