#  Chart/urls.py

from django.contrib import admin
from django.urls import path
from chart import views

from .views import *# !!!

urlpatterns = [
    path('', views.home, name='home'),
    path('covid19/',
         covid19_view, name='covid19'),
    path('ticket-class/3/',
         views.ticket_class_view_3, name='ticket_class_view_3'),
    path('json-example/', views.json_example, name='json_example'),
    path('json-example/data/', views.chart_data, name='chart_data'),
    path('admin/', admin.site.urls),
    # path('covid19new/', covid19_view_new, name='covid19new'),
]
