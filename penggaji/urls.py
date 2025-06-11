from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # penggajian
    path('', views.penggajian_read, name='penggajian_read'),
    path('create/', views.penggajian_create, name='penggajian_create'),
    path('update/<int:pk>', views.penggajian_update, name='penggajian_update'),
    # path('delete/<int:pk>', views.penggajian_delete, name='penggajian_delete'),
    # slip gaji
    # path('slip_gaji/', views.slip_gaji_read, name='slip_gaji_read'),
    path('<int:penggajian_id>/slip_gaji/', views.slip_gaji_read, name='slip_gaji_read'),
    # path('slip_gaji/create/', views.slip_gaji_create, name='slip_gaji_create'),
    # path('<int:penggajian_id>/slip_gaji/<int:pk>/update/', views.slip_gaji_update, name='slip_gaji_update'),
    # path('slip_gaji/delete/<int:pk>/', views.slip_gaji_delete, name='slip_gaji_delete'),
    path('<int:penggajian_id>/slip_gaji/<int:slip_gaji_id>/izin_masuk_keluar/', views.izin_read, name='izin_read'),
    path('<int:penggajian_id>/slip_gaji/<int:slip_gaji_id>/izin_masuk_keluar/<int:pk>/update/', views.izin_update, name='izin_update'),
    # path('<int:penggajian_id>/slip_gaji/<int:slip_gaji_id>/izin_masuk_keluar/<int:pk>/delete/', views.izin_delete, name='izin_delete'),
    # path('<int:penggajian_id>/slip_gaji/<int:slip_gaji_id>/izin_masuk_keluar/create/', views.izin_create, name='izin_create'),
]
