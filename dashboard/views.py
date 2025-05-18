from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime

@login_required
def dashboard_view(request):
    current_date = datetime.now()

    # Dummy monthly salary data for last 6 months
    monthly_data = [
        {'payment_date__month': 7, 'amount': 150000000},
        {'payment_date__month': 8, 'amount': 155000000},
        {'payment_date__month': 9, 'amount': 153000000},
        {'payment_date__month': 10, 'amount': 158000000},
        {'payment_date__month': 11, 'amount': 160000000},
        {'payment_date__month': 12, 'amount': 162000000},
    ]
    
    # Dummy department distribution data
    department_data = [
        {'name': 'Engineering', 'count': 25},
        {'name': 'Marketing', 'count': 15},
        {'name': 'Finance', 'count': 12},
        {'name': 'HR', 'count': 8},
        {'name': 'Operations', 'count': 20},
    ]
    
    # Dummy top paid departments
    top_paid_departments = [
        {'name': 'Engineering', 'average_salary': 15000000},
        {'name': 'Finance', 'average_salary': 12000000},
        {'name': 'Marketing', 'average_salary': 10000000},
    ]

    # Dummy data for employee statistics
    total_employees = 80
    total_salary_current_month = 938000000
    paid_employees_current_month = 65
    employees_ratio = f"{paid_employees_current_month} / {total_employees}"
    
    context = {
        'title': 'Dashboard',
        'active_menu': 'dashboard',
        'total_employees': total_employees,
        'total_salary': total_salary_current_month,
        'paid_employees_ratio': employees_ratio,
        'monthly_salary_data': monthly_data,
        'department_distribution': department_data,
        'top_paid_departments': top_paid_departments
    }
    
    return render(request, 'page/dashboard/dashboard.html', context)
