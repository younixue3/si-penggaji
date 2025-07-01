from django.urls import path
from . import views

app_name = 'penggajiV2'

urlpatterns = [
    # Template Perhitungan Gaji
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.template_create, name='template_create'),
    path('templates/<int:template_id>/', views.template_detail, name='template_detail'),
    path('templates/<int:template_id>/edit/', views.template_edit, name='template_edit'),
    path('templates/<int:template_id>/delete/', views.template_delete, name='template_delete'),
    
    # Variabel Perhitungan
    path('templates/<int:template_id>/variables/create/', views.variable_create, name='variable_create'),
    path('variables/<int:variable_id>/edit/', views.variable_edit, name='variable_edit'),
    path('variables/<int:variable_id>/delete/', views.variable_delete, name='variable_delete'),
    
    # Langkah Perhitungan
    path('templates/<int:template_id>/steps/editor/', views.calculation_step_editor, name='calculation_step_editor'),
    path('templates/<int:template_id>/steps/save/', views.save_calculation_steps, name='save_calculation_steps'),
    
    # Penugasan Template ke Pengguna
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/create/', views.assignment_create, name='assignment_create'),
    path('assignments/<int:assignment_id>/delete/', views.assignment_delete, name='assignment_delete'),
    
    # Perhitungan Gaji
    path('calculate/<int:assignment_id>/', views.calculation_form, name='calculation_form'),
    path('results/<int:result_id>/', views.calculation_result, name='calculation_result'),
    path('history/', views.calculation_history, name='calculation_history'),
    path('history/user/<int:user_id>/', views.calculation_history, name='user_calculation_history'),
]