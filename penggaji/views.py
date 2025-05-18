from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Penggaji
from .forms import PenggajiForm

def penggaji_read(request):
    penggajis = Penggaji.objects.all()
    return render(request, 'page/dashboard/penggaji/read.html', {'penggajis': penggajis})

def penggaji_create(request):
    if request.method == "POST":
        form = PenggajiForm(request.POST)
        if form.is_valid():
            penggaji = form.save()
            return redirect('penggaji_read', pk=penggaji.pk)
    else:
        form = PenggajiForm()
    return render(request, 'page/dashboard/penggaji/create.html', {'form': form})

def penggaji_update(request, pk):
    penggaji = get_object_or_404(Penggaji, pk=pk)
    if request.method == "POST":
        form = PenggajiForm(request.POST, instance=penggaji)
        if form.is_valid():
            penggaji = form.save()
            return redirect('penggaji_read', pk=penggaji.pk)
    else:
        form = PenggajiForm(instance=penggaji)
    return render(request, 'page/dashboard/penggaji/update.html', {'form': form})

def penggaji_delete(request, pk):
    penggaji = get_object_or_404(Penggaji, pk=pk)
    if request.method == "POST":
        penggaji.delete()
        return redirect('penggaji_list')
    return HttpResponse('Method not allowed', status=405)
