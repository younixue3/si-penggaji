from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Penggajian, SlipGaji, IzinKeluarMasuk, MONTH_CHOICES, STATUS_CHOICES
from django.contrib.auth.models import User

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
                raise ValueError("All fields are required")

            last_penggajian = Penggajian.objects.first()
            last_penggajian.status = 'selesai'
            last_penggajian.save()

            # Create new penggajian record
            penggajian = Penggajian.objects.create(
                days_in_month=days_in_month,
                month=month,
                status=status
            )
            
            return redirect('penggajian_read')
            
        except ValueError as e:
            # Handle validation errors
            return render(request, 'page/dashboard/penggajian/create.html', {
                'month_list': MONTH_CHOICES,
                'status_list': STATUS_CHOICES,
                'error_message': str(e)
            })
        except Exception as e:
            # Handle other errors
            return render(request, 'page/dashboard/penggajian/create.html', {
                'month_list': MONTH_CHOICES,
                'status_list': STATUS_CHOICES,
                'error_message': "An error occurred while creating the record"
            })

    # Handle GET request
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
    # Get existing penggajian record or return 404
    penggajian = get_object_or_404(Penggajian, pk=pk)

    if request.method == "POST":
        try:
            # Get and validate required fields
            update_status = request.POST.get('update_status')
            if update_status:
                # Update the status of the previous penggajian record
                last_penggajian = Penggajian.objects.first()
                last_penggajian.status = request.POST.get('status')
                last_penggajian.save()
                return redirect('penggajian_read')
            days_in_month = request.POST.get('days_in_month')
            month = request.POST.get('month')
            status = request.POST.get('status')

            if not all([days_in_month, month, status]):
                raise ValueError("All fields are required")

            # Update existing penggajian record
            penggajian.days_in_month = days_in_month
            penggajian.month = month
            penggajian.status = status
            penggajian.save()
            
            return redirect('penggajian_read')
            
        except ValueError as e:
            # Handle validation errors
            return render(request, 'page/dashboard/penggajian/update.html', {
                'penggajian': penggajian,
                'month_list': MONTH_CHOICES,
                'status_list': STATUS_CHOICES,
                'error_message': str(e)
            })
        except Exception as e:
            # Handle other errors
            return render(request, 'page/dashboard/penggajian/update.html', {
                'penggajian': penggajian,
                'month_list': MONTH_CHOICES,
                'status_list': STATUS_CHOICES,
                'error_message': "An error occurred while updating the record"
            })

    # Handle GET request
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
        slip_gaji.karyawan = request.POST.get('karyawan')
        slip_gaji.gaji_pokok = request.POST.get('gaji_pokok')
        slip_gaji.tunjangan = request.POST.get('tunjangan')
        slip_gaji.potongan = request.POST.get('potongan')
        slip_gaji.save()
        return redirect('slip_gaji_read', penggajian_id=penggajian_id)
        
    return render(request, 'page/dashboard/slip_gaji/update.html', {
        'slip_gaji': slip_gaji,
        'penggajian': penggajian
    })

@login_required
def slip_gaji_delete(request, pk):
    slip_gaji = get_object_or_404(SlipGaji, pk=pk)
    if request.method == "POST":
        slip_gaji.delete()
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
        return redirect('penggajian_detail', pk=penggajian_pk)
    return render(request, 'page/dashboard/slip_gaji/create.html', {'penggajian': penggajian})

@login_required
def izin_read(request, penggajian_id, slip_gaji_id):
    slip_gaji = get_object_or_404(SlipGaji, pk=slip_gaji_id)
    izin_list = slip_gaji.izin_list.all()
    return render(request, 'page/dashboard/izin_keluar_masuk/read.html', {
        'slip_gaji': slip_gaji,
        'izin_list': izin_list,
        'penggajian_id': penggajian_id
    })

@login_required
def izin_update(request, pk, slip_gaji_pk):
    izin = get_object_or_404(IzinKeluarMasuk, pk=pk)
    slip_gaji = get_object_or_404(SlipGaji, pk=slip_gaji_pk)
    if request.method == "POST":
        izin.tanggal = request.POST.get('tanggal')
        izin.jenis = request.POST.get('jenis')
        izin.keterangan = request.POST.get('keterangan')
        izin.save()
        # Recalculate slip gaji
        slip_gaji.save()
        return redirect('izin_read', slip_gaji_pk=slip_gaji_pk)
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
            # Validate required fields
            tanggal = request.POST.get('tanggal')
            jenis = request.POST.get('jenis')
            keterangan = request.POST.get('keterangan')
            
            if not all([tanggal, jenis, keterangan]):
                raise ValueError("All fields are required")
                
            izin = IzinKeluarMasuk.objects.create(
                slip_gaji=slip_gaji,
                tanggal=tanggal,
                jenis=jenis,
                keterangan=keterangan
            )
            
            # Recalculate slip gaji
            slip_gaji.save()
            
            return redirect('izin_read', 
                          penggajian_id=penggajian_id, 
                          slip_gaji_id=slip_gaji_id)
                          
        except ValueError as e:
            return render(request, 'page/dashboard/izin_keluar_masuk/create.html', {
                'slip_gaji': slip_gaji,
                'error_message': str(e)
            })
        except Exception as e:
            return render(request, 'page/dashboard/izin_keluar_masuk/create.html', {
                'slip_gaji': slip_gaji,
                'error_message': "An error occurred while creating the record"
            })
            
    return render(request, 'page/dashboard/izin_keluar_masuk/create.html', {
        'slip_gaji_id': slip_gaji.id,
        'penggajian_id': penggajian.id
    })

@login_required
def izin_delete(request, pk):
    izin = get_object_or_404(IzinKeluarMasuk, pk=pk)
    if request.method == "POST":
        izin.delete()
        return redirect('slip_gaji_detail', pk=izin.slip_gaji.pk)
    return HttpResponse('Method not allowed', status=405)

