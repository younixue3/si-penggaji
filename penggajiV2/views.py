from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import (
    PayrollTemplate, 
    PayrollVariable, 
    PayrollCalculationStep, 
    PayrollAssignment,
    PayrollCalculationResult,
    OPERATOR_CHOICES,
    INPUT_TYPE_CHOICES
)
import json
from decimal import Decimal
import logging
from mysite.utils.helpers import dd

logger = logging.getLogger(__name__)

# Views untuk Template Perhitungan Gaji

@login_required
def template_list(request):
    """Menampilkan daftar template perhitungan gaji"""
    templates = PayrollTemplate.objects.all().order_by('-created_at')
    return render(request, 'page/dashboard/penggajiV2/template_list.html', {
        'templates': templates
    })

@login_required
def template_detail(request, template_id):
    """Menampilkan detail template perhitungan gaji"""
    template = get_object_or_404(PayrollTemplate, id=template_id)
    variables = template.variables.all().order_by('order')
    calculation_steps = template.calculation_steps.all().order_by('order')
    
    return render(request, 'page/dashboard/penggajiV2/template_detail.html', {
        'template': template,
        'variables': variables,
        'calculation_steps': calculation_steps
    })

@login_required
def template_create(request):
    """Membuat template perhitungan gaji baru"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if not name:
            messages.error(request, 'Nama template harus diisi')
            return redirect('penggajiV2:template_create')
        
        template = PayrollTemplate.objects.create(
            name=name,
            description=description
        )
        
        messages.success(request, f'Template {name} berhasil dibuat')
        return redirect('penggajiV2:template_detail', template_id=template.id)
    
    return render(request, 'page/dashboard/penggajiV2/template_form.html')

@login_required
def template_edit(request, template_id):
    """Mengedit template perhitungan gaji"""
    template = get_object_or_404(PayrollTemplate, id=template_id)
    
    if request.method == 'POST':
        template.name = request.POST.get('name')
        template.description = request.POST.get('description')
        template.is_active = request.POST.get('is_active') == 'on'
        template.save()
        
        messages.success(request, f'Template {template.name} berhasil diperbarui')
        return redirect('penggajiV2:template_detail', template_id=template.id)
    
    return render(request, 'page/dashboard/penggajiV2/template_form.html', {
        'template': template
    })

@login_required
def template_delete(request, template_id):
    """Menghapus template perhitungan gaji"""
    template = get_object_or_404(PayrollTemplate, id=template_id)
    
    if request.method == 'POST':
        template_name = template.name
        template.delete()
        messages.success(request, f'Template {template_name} berhasil dihapus')
        return redirect('penggajiV2:template_list')
    
    return render(request, 'page/dashboard/penggajiV2/template_confirm_delete.html', {
        'template': template
    })

# Views untuk Variabel Perhitungan

@login_required
def variable_create(request, template_id):
    """Membuat variabel baru untuk template"""
    template = get_object_or_404(PayrollTemplate, id=template_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        display_name = request.POST.get('display_name')
        input_type = request.POST.get('input_type')
        is_required = request.POST.get('is_required') == 'on'
        default_value = request.POST.get('default_value', '')
        options = request.POST.get('options', '')
        order = request.POST.get('order', 0)
        
        try:
            variable = PayrollVariable.objects.create(
                template=template,
                name=name,
                display_name=display_name,
                input_type=input_type,
                is_required=is_required,
                default_value=default_value,
                options=options,
                order=order
            )
            variable.full_clean()
            messages.success(request, f'Variabel {display_name} berhasil dibuat')
            return redirect('penggajiV2:template_detail', template_id=template.id)
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    input_types = dict(INPUT_TYPE_CHOICES)
    return render(request, 'page/dashboard/penggajiV2/variable_form.html', {
        'template': template,
        'input_types': input_types
    })

@login_required
def variable_edit(request, variable_id):
    """Mengedit variabel perhitungan"""
    variable = get_object_or_404(PayrollVariable, id=variable_id)
    template = variable.template
    
    if request.method == 'POST':
        variable.name = request.POST.get('name')
        variable.display_name = request.POST.get('display_name')
        variable.input_type = request.POST.get('input_type')
        variable.is_required = request.POST.get('is_required') == 'on'
        variable.default_value = request.POST.get('default_value', '')
        variable.options = request.POST.get('options', '')
        variable.order = request.POST.get('order', 0)
        
        try:
            variable.full_clean()
            variable.save()
            messages.success(request, f'Variabel {variable.display_name} berhasil diperbarui')
            return redirect('penggajiV2:template_detail', template_id=template.id)
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    input_types = dict(INPUT_TYPE_CHOICES)
    return render(request, 'page/dashboard/penggajiV2/variable_form.html', {
        'template': template,
        'variable': variable,
        'input_types': input_types
    })

@login_required
def variable_delete(request, variable_id):
    """Menghapus variabel perhitungan"""
    variable = get_object_or_404(PayrollVariable, id=variable_id)
    template_id = variable.template.id
    
    if request.method == 'POST':
        variable_name = variable.display_name
        variable.delete()
        messages.success(request, f'Variabel {variable_name} berhasil dihapus')
        return redirect('penggajiV2:template_detail', template_id=template_id)
    
    return render(request, 'page/dashboard/penggajiV2/variable_confirm_delete.html', {
        'variable': variable
    })

# Views untuk Langkah Perhitungan

@login_required
def calculation_step_editor(request, template_id):
    """Visual editor for calculation steps"""
    template = get_object_or_404(PayrollTemplate, id=template_id)
    
    # Get variables and calculation steps ordered by order field
    variables = template.variables.all().order_by('order')
    calculation_steps = template.calculation_steps.all().order_by('order')
    
    # Convert variables to JSON format for visual editor
    variables_json = [{
        'id': var.id,
        'name': var.name,
        'display_name': var.display_name,
        'input_type': var.input_type
    } for var in variables]
    
    # Convert calculation steps to JSON format for visual editor
    steps_json = [{
        'id': step.id,
        'step_id': step.step_id,
        'name': step.name,
        'operator': step.operator,
        'input1_type': step.input1_type,
        'input1_value': step.input1_value,
        'input2_type': step.input2_type,
        'input2_value': step.input2_value,
        'result_variable': step.result_variable,
        'order': step.order,
        'condition_true_step': step.condition_true_step,
        'condition_false_step': step.condition_false_step
    } for step in calculation_steps]
    
    # Get operator choices dictionary
    operators = dict(OPERATOR_CHOICES)
    
    # Render template with required data
    return render(request, 'page/dashboard/penggajiV2/calculation_step_editor.html', {
        'template': template,
        'variables': variables_json,
        'variables_json': json.dumps(variables_json),
        'steps_json': json.dumps(steps_json), 
        'operators': operators
    })

@login_required
@require_POST
def save_calculation_steps(request, template_id):
    """Menyimpan langkah-langkah perhitungan dari editor visual"""
    template = get_object_or_404(PayrollTemplate, id=template_id)
    
    try:
        steps_data = json.loads(request.body)
        
        with transaction.atomic():
            # Hapus langkah-langkah yang ada
            template.calculation_steps.all().delete()
            
            # Buat langkah-langkah baru
            for i, step_data in enumerate(steps_data):
                PayrollCalculationStep.objects.create(
                    template=template,
                    step_id=step_data.get('step_id'),
                    name=step_data.get('name'),
                    operator=step_data.get('operator'),
                    input1_type=step_data.get('input1_type'),
                    input1_value=step_data.get('input1_value'),
                    input2_type=step_data.get('input2_type', ''),
                    input2_value=step_data.get('input2_value', ''),
                    result_variable=step_data.get('result_variable'),
                    order=i,
                    condition_true_step=step_data.get('condition_true_step', ''),
                    condition_false_step=step_data.get('condition_false_step', '')
                )
        
        return JsonResponse({'status': 'success', 'message': 'Langkah perhitungan berhasil disimpan'})
    except Exception as e:
        logger.error(f"Error saving calculation steps: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# Views untuk Penugasan Template ke Pengguna

@login_required
def assignment_list(request):
    """Menampilkan daftar penugasan template ke pengguna"""
    assignments = PayrollAssignment.objects.all().select_related('template', 'user')
    return render(request, 'page/dashboard/penggajiV2/assignment_list.html', {
        'assignments': assignments
    })

@login_required
def assignment_create(request):
    """Membuat penugasan template ke pengguna"""
    templates = PayrollTemplate.objects.filter(is_active=True)
    users = User.objects.filter(is_active=True)
    
    if request.method == 'POST':
        template_id = request.POST.get('template')
        user_id = request.POST.get('user')
        
        template = get_object_or_404(PayrollTemplate, id=template_id)
        user = get_object_or_404(User, id=user_id)
        
        # Cek apakah penugasan sudah ada
        if PayrollAssignment.objects.filter(template=template, user=user).exists():
            messages.error(request, f'Penugasan untuk {user.username} dengan template {template.name} sudah ada')
            return redirect('penggajiV2:assignment_list')
        
        PayrollAssignment.objects.create(
            template=template,
            user=user
        )
        
        messages.success(request, f'Penugasan untuk {user.username} dengan template {template.name} berhasil dibuat')
        return redirect('penggajiV2:assignment_list')
    
    return render(request, 'page/dashboard/penggajiV2/assignment_form.html', {
        'templates': templates,
        'users': users
    })

@login_required
def assignment_delete(request, assignment_id):
    """Menghapus penugasan template"""
    assignment = get_object_or_404(PayrollAssignment, id=assignment_id)
    
    if request.method == 'POST':
        user_name = assignment.user.username
        template_name = assignment.template.name
        assignment.delete()
        messages.success(request, f'Penugasan untuk {user_name} dengan template {template_name} berhasil dihapus')
        return redirect('penggajiV2:assignment_list')
    
    return render(request, 'page/dashboard/penggajiV2/assignment_confirm_delete.html', {
        'assignment': assignment
    })

# Views untuk Perhitungan Gaji

@login_required
def calculation_form(request, assignment_id):
    """Form untuk memasukkan nilai variabel dan melakukan perhitungan gaji"""
    assignment = get_object_or_404(PayrollAssignment, id=assignment_id)
    template = assignment.template
    variables = template.variables.all().order_by('order')
    
    if request.method == 'POST':
        input_values = {}
        for var in variables:
            value = request.POST.get(f'var_{var.name}')
            if var.is_required and not value:
                messages.error(request, f'Variabel {var.display_name} harus diisi')
                return redirect('penggajiV2:calculation_form', assignment_id=assignment_id)
            
            # Convert empty string to None
            input_values[var.name] = value if value != '' else None
        
        try:
            # Validate required numeric fields
            for var in variables:
                if var.input_type in ['number', 'decimal'] and var.name in input_values:
                    value = input_values[var.name]
                    if value is not None:
                        try:
                            input_values[var.name] = Decimal(str(value))
                        except:
                            messages.error(request, f'Variabel {var.display_name} harus berupa angka')
                            return redirect('penggajiV2:calculation_form', assignment_id=assignment_id)
            
            # Run calculation
            result = calculate_payroll(template, input_values)
            # Convert Decimal objects to strings before JSON serialization
            steps_dict = {k: str(v) if isinstance(v, Decimal) else v for k, v in result['steps'].items()}
            # return dd(steps_dict)
            
            # Save calculation result
            calculation_date = request.POST.get('calculation_date')
            # return dd('test')
            # Convert input values Decimal objects to strings for JSON serialization
            json_safe_input_values = {}
            for key, value in input_values.items():
                if isinstance(value, Decimal):
                    json_safe_input_values[key] = str(value)
                else:
                    json_safe_input_values[key] = value

            calculation_result = PayrollCalculationResult.objects.create(
                assignment=assignment,
                calculation_date=calculation_date,
                input_values=json_safe_input_values,
                calculation_results=steps_dict,
                final_result=str(result['final_result'])
            )
            
            messages.success(request, 'Perhitungan gaji berhasil dilakukan')
            return redirect('penggajiV2:calculation_result', result_id=calculation_result.id)
        except Exception as e:
            return dd(e)
            logger.error(f"Error calculating payroll: {str(e)}")
            messages.error(request, f'Terjadi kesalahan dalam perhitungan: {str(e)}')
            return redirect('penggajiV2:calculation_form', assignment_id=assignment_id)
    
    return render(request, 'page/dashboard/penggajiV2/calculation_form.html', {
        'assignment': assignment,
        'template': template,
        'variables': variables
    })

@login_required
def calculation_result(request, result_id):
    """Menampilkan hasil perhitungan gaji"""
    result = get_object_or_404(PayrollCalculationResult, id=result_id)
    assignment = result.assignment
    template = assignment.template
    
    return render(request, 'page/dashboard/penggajiV2/calculation_result.html', {
        'result': result,
        'assignment': assignment,
        'template': template
    })

@login_required
def calculation_history(request, user_id=None):
    """Menampilkan riwayat perhitungan gaji"""
    if user_id:
        user = get_object_or_404(User, id=user_id)
        results = PayrollCalculationResult.objects.filter(
            assignment__user=user
        ).select_related('assignment', 'assignment__template', 'assignment__user')
    else:
        results = PayrollCalculationResult.objects.all().select_related(
            'assignment', 'assignment__template', 'assignment__user'
        )
    
    return render(request, 'page/dashboard/penggajiV2/calculation_history.html', {
        'results': results
    })

# Fungsi Utilitas

def calculate_payroll(template, input_values):
    """Menjalankan perhitungan gaji berdasarkan template dan nilai input"""
    steps = template.calculation_steps.all().order_by('order')
    
    if not steps.exists():
        raise ValueError("Tidak ada langkah perhitungan yang didefinisikan")
    
    # Inisialisasi variabel hasil
    result_variables = {}
    for key, value in input_values.items():
        result_variables[key] = value
    
    # Simpan hasil setiap langkah
    step_results = {}
    
    # Jalankan perhitungan untuk setiap langkah
    i = 0
    while i < len(steps):
        step = steps[i]
        
        # Ambil nilai input 1
        if step.input1_type == 'variable':
            if step.input1_value not in result_variables:
                raise ValueError(f"Variabel {step.input1_value} tidak ditemukan")
            input1 = result_variables[step.input1_value]
        elif step.input1_type == 'value':
            input1 = step.input1_value
        elif step.input1_type == 'step':
            if step.input1_value not in step_results:
                raise ValueError(f"Hasil langkah {step.input1_value} tidak ditemukan")
            input1 = step_results[step.input1_value]
        
        # Konversi input1 ke tipe yang sesuai
        try:
            if step.operator in ['add', 'subtract', 'multiply', 'divide', 'percentage', 'greater_than', 'less_than']:
                input1 = Decimal(str(input1))
        except:
            raise ValueError(f"Tidak dapat mengkonversi {input1} ke angka")
        
        # Untuk operator yang membutuhkan input kedua
        if step.operator in ['add', 'subtract', 'multiply', 'divide', 'percentage', 'greater_than', 'less_than', 'equal', 'not_equal']:
            # Ambil nilai input 2
            if step.input2_type == 'variable':
                if step.input2_value not in result_variables:
                    raise ValueError(f"Variabel {step.input2_value} tidak ditemukan")
                input2 = result_variables[step.input2_value]
            elif step.input2_type == 'value':
                input2 = step.input2_value
            elif step.input2_type == 'step':
                if step.input2_value not in step_results:
                    raise ValueError(f"Hasil langkah {step.input2_value} tidak ditemukan")
                input2 = step_results[step.input2_value]
            
            # Konversi input2 ke tipe yang sesuai
            try:
                if step.operator in ['add', 'subtract', 'multiply', 'divide', 'percentage', 'greater_than', 'less_than']:
                    input2 = Decimal(str(input2))
            except:
                raise ValueError(f"Tidak dapat mengkonversi {input2} ke angka")
        
        # Lakukan perhitungan berdasarkan operator
        result = None
        next_step_index = i + 1
        
        if step.operator == 'add':
            result = round(input1 + input2)
        elif step.operator == 'subtract':
            result = round(input1 - input2)
        elif step.operator == 'multiply':
            result = round(input1 * input2)
        elif step.operator == 'divide':
            if input2 == 0:
                raise ValueError("Pembagian dengan nol")
            result = round(input1 / input2)
        elif step.operator == 'percentage':
            result = round(input1 * (input2 / Decimal('100')))
        elif step.operator == 'if_condition':
            # Input1 adalah kondisi boolean
            condition_result = bool(input1)
            if condition_result and step.condition_true_step:
                # Cari indeks langkah berikutnya berdasarkan step_id
                for idx, s in enumerate(steps):
                    if s.step_id == step.condition_true_step:
                        next_step_index = idx
                        break
            elif not condition_result and step.condition_false_step:
                # Cari indeks langkah berikutnya berdasarkan step_id
                for idx, s in enumerate(steps):
                    if s.step_id == step.condition_false_step:
                        next_step_index = idx
                        break
            result = "true" if condition_result else "false"
        elif step.operator == 'greater_than':
            result = "true" if input1 > input2 else "false"
        elif step.operator == 'less_than':
            result = "true" if input1 < input2 else "false"
        elif step.operator == 'equal':
            result = input1 == input2
        elif step.operator == 'not_equal':
            result = input1 != input2
        
        # Simpan hasil
        step_results[step.step_id] = result
        result_variables[step.result_variable] = result
        
        # Lanjut ke langkah berikutnya
        i = next_step_index
    
    # Ambil hasil akhir (variabel terakhir yang dihitung)
    final_result = Decimal('0')
    for step in steps:
        if step.result_variable == 'final_salary' and step.step_id in step_results:
            final_result = step_results[step.step_id]
            break
    
    return {
        'steps': step_results,
        'variables': result_variables,
        'final_result': final_result
    }
