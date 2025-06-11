from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.pengelolaKaryawan_view, name='pengelolaKaryawan_read'),
    # path('penggajian/', include('penggaji.urls')),
    # path('pengelola_staff/', include('pengelola_staff.urls')),
]
