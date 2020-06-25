# hChart.urls.py
from django.contrib import admin
from django.urls import path, include
from chart import views                                     # !!!

urlpatterns = [
    path('', include('chart.urls')),
    path('admin/', admin.site.urls),
]