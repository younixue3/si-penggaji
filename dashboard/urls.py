from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard_page'),
    path('penggajian/', include('penggaji.urls')),
    path('pengelola_staff/', include('pengelolaKaryawan.urls')),
]
