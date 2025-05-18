from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Penggajian, SlipGaji, IzinKeluarMasuk

@login_required
def penggajian_read(request):
    penggajians = Penggajian.objects.all().order_by('-created_at')
    return render(request, 'page/dashboard/penggajian/read.html', {'penggajians': penggajians})

@login_required
def penggajian_create(request):
    if request.method == "POST":
        penggajian = Penggajian.objects.create(
            nama=request.POST.get('nama'),
            tanggal=request.POST.get('tanggal'),
            keterangan=request.POST.get('keterangan')
        )
        return redirect('penggajian_detail', pk=penggajian.pk)
    return render(request, 'page/dashboard/penggajian/create.html')

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
    penggajian = get_object_or_404(Penggajian, pk=pk)
    if request.method == "POST":
        penggajian.nama = request.POST.get('nama')
        penggajian.tanggal = request.POST.get('tanggal')
        penggajian.keterangan = request.POST.get('keterangan')
        penggajian.save()
        return redirect('penggajian_detail', pk=penggajian.pk)
    return render(request, 'page/dashboard/penggajian/update.html', {'penggajian': penggajian})

@login_required
def penggajian_delete(request, pk):
    penggajian = get_object_or_404(Penggajian, pk=pk)
    if request.method == "POST":
        penggajian.delete()
        return redirect('penggajian_list')
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
def izin_create(request, slip_gaji_pk):
    slip_gaji = get_object_or_404(SlipGaji, pk=slip_gaji_pk)
    if request.method == "POST":
        izin = IzinKeluarMasuk.objects.create(
            slip_gaji=slip_gaji,
            tanggal=request.POST.get('tanggal'),
            jenis=request.POST.get('jenis'),
            keterangan=request.POST.get('keterangan')
        )
        # Recalculate slip gaji
        slip_gaji.save()
        return redirect('slip_gaji_detail', pk=slip_gaji_pk)
    return render(request, 'page/dashboard/izin/create.html', {'slip_gaji': slip_gaji})
