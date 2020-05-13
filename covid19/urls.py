from django.urls import path
from . import views
import django.contrib.staticfiles.urls

urlpatterns = (
    path('', views.index, name='index'),
)

#urlpatterns += django.contrib.staticfiles.urls.staticfiles_urlpatterns()
