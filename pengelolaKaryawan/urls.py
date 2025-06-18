from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.pengelolaKaryawan_view, name='pengelolaKaryawan_read'),
    path('create/', views.pengelolaKaryawan_create, name='pengelolaKaryawan_create'),
    path('update/<int:id>/', views.pengelolaKaryawan_update, name='pengelolaKaryawan_update'),
    path('delete/<int:id>/', views.pengelolaKaryawan_delete, name='pengelolaKaryawan_delete'),
]
