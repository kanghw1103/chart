#  Chart/urls.py

from django.contrib import admin
from django.urls import path
from chart import views                                     # !!!

urlpatterns = [
    path('', views.home, name='home'),
    path('ticket-class/2/',
         views.ticket_class_view_2, name='ticket_class_view_2'),
    path('ticket-class/3/',
         views.ticket_class_view_3, name='ticket_class_view_3'),
    path('json-example/', views.json_example, name='json_example'),
    path('json-example/data/', views.chart_data, name='chart_data'),
    path('admin/', admin.site.urls),
]
