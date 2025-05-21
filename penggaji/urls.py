from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # penggajian
    path('', views.penggajian_read, name='penggajian_read'),
    path('create/', views.penggajian_create, name='penggajian_create'),
    path('update/<int:pk>', views.penggajian_update, name='penggajian_update'),
    path('delete/<int:pk>', views.penggajian_delete, name='penggajian_delete'),
    # slip gaji
    path('slip_gaji/', views.slip_gaji_read, name='slip_gaji_read'),
    # path('slip_gaji/create/', views.slip_gaji_create, name='slip_gaji_create'),
    path('slip_gaji/update/<int:pk>', views.slip_gaji_update, name='slip_gaji_update'),
    path('slip_gaji/delete/<int:pk>', views.slip_gaji_delete, name='slip_gaji_delete'),
]
