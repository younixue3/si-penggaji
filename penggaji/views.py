from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Penggajian, SlipGaji, IzinKeluarMasuk, MONTH_CHOICES, STATUS_CHOICES
from django.contrib.auth.models import User
from datetime import datetime
from mysite.utils.helpers import dd

@login_required
def penggajian_read(request):
    penggajians = Penggajian.objects.all().order_by('-created_at')
    return render(request, 'page/dashboard/penggajian/read.html', {'penggajians': penggajians})

@login_required
def penggajian_create(request):
    """
    Create a new Penggajian (payroll) record.
    Validates input data and handles both GET and POST requests.
    """
    if request.method == "POST":
        try:
            # Get and validate required fields
            days_in_month = request.POST.get('days_in_month')
            month = request.POST.get('month')
            status = request.POST.get('status')

            if not all([days_in_month, month, status]):
                messages.error(request, "All fields are required")
                return render(request, 'page/dashboard/penggajian/create.html', {
                    'month_list': MONTH_CHOICES,
                    'status_list': STATUS_CHOICES
                })
            
            try:
                last_penggajian = Penggajian.objects.latest('created_at')
                last_penggajian.status = 'done'
                last_penggajian.save()
            except Penggajian.DoesNotExist:
                pass

            # Create new penggajian record
            penggajian = Penggajian.objects.create(
                days_in_month=int(days_in_month),
                month=month,
                status=status
            )
            
            messages.success(request, 'Penggajian created successfully')
            return redirect('penggajian_read')
            
        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'page/dashboard/penggajian/create.html', {
                'month_list': MONTH_CHOICES,
                'status_list': STATUS_CHOICES
            })
        except Exception as e:
            messages.error(request, "An error occurred while creating the record")
            return render(request, 'page/dashboard/penggajian/create.html', {
                'month_list': MONTH_CHOICES,
                'status_list': STATUS_CHOICES
            })

    return render(request, 'page/dashboard/penggajian/create.html', {
        'month_list': MONTH_CHOICES,
        'status_list': STATUS_CHOICES
    })

@login_required
def penggajian_detail(request, pk):
    penggajian = get_object_or_404(Penggajian, pk=pk)
    slip_gaji_list = penggajian.slip_gaji.all()
    return render(request, 'page/dashboard/penggajian/detail.html', {
        'penggajian': penggajian,
        'slip_gaji_list': slip_gaji_list
    })

@login_required
def penggajian_update(request, pk):
    """
    Update an existing Penggajian (payroll) record.
    Validates input data and handles both GET and POST requests.
    """
    penggajian = get_object_or_404(Penggajian, pk=pk)

    if request.method == "POST":
        try:
            update_status = request.POST.get('update_status')
            if update_status:
                last_penggajian = Penggajian.objects.first()
                last_penggajian.status = request.POST.get('status')
                last_penggajian.save()
                messages.success(request, 'Status updated successfully')
                return redirect('penggajian_read')

            days_in_month = request.POST.get('days_in_month')
            month = request.POST.get('month')
            status = request.POST.get('status')

            if not all([days_in_month, month, status]):
                messages.error(request, "All fields are required")
                return render(request, 'page/dashboard/penggajian/update.html', {
                    'penggajian': penggajian,
                    'month_list': MONTH_CHOICES,
                    'status_list': STATUS_CHOICES
                })

            penggajian.days_in_month = days_in_month
            penggajian.month = month
            penggajian.status = status
            penggajian.save()
            
            messages.success(request, 'Penggajian updated successfully')
            return redirect('penggajian_read')
            
        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'page/dashboard/penggajian/update.html', {
                'penggajian': penggajian,
                'month_list': MONTH_CHOICES,
                'status_list': STATUS_CHOICES
            })
        except Exception as e:
            messages.error(request, "An error occurred while updating the record")
            return render(request, 'page/dashboard/penggajian/update.html', {
                'penggajian': penggajian,
                'month_list': MONTH_CHOICES,
                'status_list': STATUS_CHOICES
            })

    return render(request, 'page/dashboard/penggajian/update.html', {
        'penggajian': penggajian,
        'month_list': MONTH_CHOICES,
        'status_list': STATUS_CHOICES
    })

@login_required
def penggajian_delete(request, pk):
    penggajian = get_object_or_404(Penggajian, pk=pk)
    if request.method == "POST":
        penggajian.delete()
        messages.success(request, 'Penggajian deleted successfully')
        return redirect('penggajian_read')
    return HttpResponse('Method not allowed', status=405)

@login_required
def slip_gaji_read(request, penggajian_id):
    slip_gaji_list = SlipGaji.objects.filter(penggajian_id=penggajian_id).order_by('-created_at')
    return render(request, 'page/dashboard/slip_gaji/read.html', {'slip_gaji_list': slip_gaji_list})

@login_required
def slip_gaji_update(request, pk, penggajian_id):
    slip_gaji = get_object_or_404(SlipGaji, pk=pk)
    penggajian = get_object_or_404(Penggajian, pk=penggajian_id)
    
    if request.method == "POST":
        try:
            slip_gaji.gaji_pokok = int(request.POST.get('gaji_pokok'))
            slip_gaji.save()
            messages.success(request, 'Slip gaji updated successfully')
            return redirect('slip_gaji_read', penggajian_id=penggajian_id)
        except (ValueError, TypeError):
            messages.error(request, 'Please enter valid numeric values for monetary fields')
            return render(request, 'page/dashboard/slip_gaji/update.html', {
                'slip_gaji': slip_gaji,
                'penggajian': penggajian
            })
        
    return render(request, 'page/dashboard/slip_gaji/update.html', {
        'slip_gaji': slip_gaji,
        'penggajian': penggajian
    })

@login_required
def slip_gaji_delete(request, pk):
    slip_gaji = get_object_or_404(SlipGaji, pk=pk)
    if request.method == "POST":
        slip_gaji.delete()
        messages.success(request, 'Slip gaji deleted successfully')
        return redirect('slip_gaji_read')
    return HttpResponse('Method not allowed', status=405)

@login_required
def slip_gaji_create(request, penggajian_pk):
    penggajian = get_object_or_404(Penggajian, pk=penggajian_pk)
    if request.method == "POST":
        slip_gaji = SlipGaji.objects.create(
            penggajian=penggajian,
            karyawan=request.POST.get('karyawan'),
            gaji_pokok=request.POST.get('gaji_pokok'),
            tunjangan=request.POST.get('tunjangan'),
            potongan=request.POST.get('potongan')
        )
        messages.success(request, 'Slip gaji created successfully')
        return redirect('penggajian_detail', pk=penggajian_pk)
    return render(request, 'page/dashboard/slip_gaji/create.html', {'penggajian': penggajian})

@login_required
def izin_read(request, penggajian_id, slip_gaji_id):
    slip_gaji = get_object_or_404(SlipGaji, pk=slip_gaji_id)
    izin_list = slip_gaji.izin_list.all()
    total_nilai_izin = sum(izin.nilai_izin for izin in izin_list)
    
    return render(request, 'page/dashboard/izin_keluar_masuk/read.html', {
        'slip_gaji': slip_gaji,
        'izin_list': izin_list,
        'penggajian_id': penggajian_id,
        'total_nilai_izin': total_nilai_izin
    })

@login_required
def izin_update(request, pk, slip_gaji_id, penggajian_id):
    izin = get_object_or_404(IzinKeluarMasuk, pk=pk)
    slip_gaji = get_object_or_404(SlipGaji, pk=slip_gaji_id)
    
    if request.method == "POST":
        try:
            date = request.POST.get('date')
            time_out = request.POST.get('time_out')
            time_in = request.POST.get('time_in')
            time_work = request.POST.get('time_work')
            potongan = True if request.POST.get('potongan') == 'on' else False

            if not all([date, time_out, time_in, time_work]):
                messages.error(request, "All fields are required")
                return render(request, 'page/dashboard/izin_keluar_masuk/update.html', {
                    'izin': izin,
                    'slip_gaji': slip_gaji
                })

            try:
                time_out_obj = datetime.strptime(time_out, '%H:%M')
                time_in_obj = datetime.strptime(time_in, '%H:%M')
                time_work_obj = datetime.strptime(time_work, '%H:%M')
            except ValueError:
                messages.error(request, "Invalid time format. Please use HH:MM format")
                return render(request, 'page/dashboard/izin_keluar_masuk/update.html', {
                    'izin': izin,
                    'slip_gaji': slip_gaji
                })

            if time_in_obj <= time_out_obj:
                messages.error(request, "Time in must be after time out")
                return render(request, 'page/dashboard/izin_keluar_masuk/update.html', {
                    'izin': izin,
                    'slip_gaji': slip_gaji
                })

            time_diff = time_in_obj - time_out_obj
            nilai_izin = time_diff.total_seconds() / 60

            izin.date = date
            izin.time_out = datetime.strptime(time_out, '%H:%M').time()
            izin.time_in = datetime.strptime(time_in, '%H:%M').time() 
            izin.time_work = datetime.strptime(time_work, '%H:%M').time()
            izin.nilai_izin = nilai_izin
            izin.potongan = potongan
            izin.save()

            slip_gaji.save()
            
            messages.success(request, 'Izin updated successfully')
            return redirect('izin_read', penggajian_id=penggajian_id, slip_gaji_id=slip_gaji_id)

        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'page/dashboard/izin_keluar_masuk/update.html', {
                'izin': izin,
                'slip_gaji': slip_gaji
            })
        except Exception as e:
            messages.error(request, "An error occurred while updating the record")
            return render(request, 'page/dashboard/izin_keluar_masuk/update.html', {
                'izin': izin,
                'slip_gaji': slip_gaji
            })

    return render(request, 'page/dashboard/izin_keluar_masuk/update.html', {
        'izin': izin,
        'slip_gaji': slip_gaji
    })

@login_required
def izin_create(request, slip_gaji_id, penggajian_id):
    slip_gaji = get_object_or_404(SlipGaji, pk=slip_gaji_id)
    penggajian = get_object_or_404(Penggajian, pk=penggajian_id)
    
    if request.method == "POST":
        try:
            date = request.POST.get('date')
            time_out = request.POST.get('time_out') 
            time_in = request.POST.get('time_in')
            
            if not all([date, time_out, time_in]):
                messages.error(request, "All fields are required")
                return render(request, 'page/dashboard/izin_keluar_masuk/create.html', {
                    'slip_gaji_id': slip_gaji.id,
                    'penggajian_id': penggajian.id
                })
                
            izin = IzinKeluarMasuk.objects.create(
                slip_gaji=slip_gaji,
                date=date,
                time_out=time_out,
                time_in=time_in
            )
            
            slip_gaji.save()
            
            messages.success(request, 'Izin created successfully')
            return redirect('izin_read', penggajian_id=penggajian_id, slip_gaji_id=slip_gaji.id)
                          
        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'page/dashboard/izin_keluar_masuk/create.html', {
                'slip_gaji_id': slip_gaji.id,
                'penggajian_id': penggajian.id
            })
        except Exception as e:
            messages.error(request, "An error occurred while creating the record")
            return render(request, 'page/dashboard/izin_keluar_masuk/create.html', {
                'slip_gaji_id': slip_gaji.id,
                'penggajian_id': penggajian.id
            })
            
    return render(request, 'page/dashboard/izin_keluar_masuk/create.html', {
        'slip_gaji_id': slip_gaji.id,
        'penggajian_id': penggajian.id
    })

@login_required
def izin_delete(request, pk, penggajian_id, slip_gaji_id):
    izin = get_object_or_404(IzinKeluarMasuk, pk=pk)
    slip_gaji = get_object_or_404(SlipGaji, pk=slip_gaji_id)
    
    if request.method == "POST":
        izin.delete()
        slip_gaji.save()
        messages.success(request, 'Izin deleted successfully')
        return redirect('izin_read', penggajian_id=penggajian_id, slip_gaji_id=slip_gaji_id)
    return HttpResponse('Method not allowed', status=405)
