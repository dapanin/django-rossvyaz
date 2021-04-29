from django.urls import path

from . import views

app_name = 'django_rossvyaz'

urlpatterns = [
    path('update/', views.rossvyaz_update, name='update'),
]
