from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Penggajian, SlipGaji, IzinKeluarMasuk, Kasbon, TableGaji, MONTH_CHOICES, STATUS_CHOICES
from django.contrib.auth.models import User
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, portrait
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
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
            date_form = request.POST.get('date_from')
            date_to = request.POST.get('date_to')
            description = request.POST.get('description')

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
                
                # Update all accepted kasbons to completed status
                accepted_kasbons = Kasbon.objects.filter(status__in=['diterima'])
                for kasbon in accepted_kasbons:
                    user = kasbon.user
                    slip_gaji = SlipGaji.objects.filter(penggajian=last_penggajian, user=user).first()
                    if kasbon.status == 'diterima':
                        kasbon.status = 'selesai'
                        kasbon.slip_gaji = slip_gaji
                        kasbon.save()
                accepted_kasbons.update(status='selesai', slip_gaji=last_penggajian)

            except Penggajian.DoesNotExist:
                pass



            # Create new penggajian record
            penggajian = Penggajian.objects.create(
                days_in_month=int(days_in_month),
                month=month,
                status=status,
                date_from=datetime.strptime(date_form, '%Y-%m-%d').date(),
                date_to=datetime.strptime(date_to, '%Y-%m-%d').date(),
                description=description
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
            return dd(e)
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
    penggajian = get_object_or_404(Penggajian, pk=penggajian_id)
    izin_list = slip_gaji.izin_list.all()
    total_nilai_izin = sum(izin.nilai_izin for izin in izin_list)
    
    return render(request, 'page/dashboard/izin_keluar_masuk/read.html', {
        'slip_gaji': slip_gaji,
        'izin_list': izin_list,
        'penggajian_id': penggajian_id,
        'penggajian': penggajian,
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
            jam_selesai = request.POST.get('jam_selesai')
            potongan = True if request.POST.get('potongan') == 'on' else False
            status_off = True if request.POST.get('status_off') == 'true' else False

            if status_off:
                izin.status_off = status_off

            else:
                # Only validate all fields if more than 2 attributes are present
                if len(request.POST) > 2 and not all([time_out, time_in, time_work, jam_selesai]):
                    messages.error(request, "All fields are required")
                    return render(request, 'page/dashboard/izin_keluar_masuk/update.html', {
                        'izin': izin,
                        'slip_gaji': slip_gaji
                    })

                # # Ensure time fields are not None before parsing
                # if not all([time_out, time_in, time_work, jam_selesai]):
                #     messages.error(request, "Time fields cannot be empty")
                #     return render(request, 'page/dashboard/izin_keluar_masuk/update.html', {
                #         'izin': izin,
                #         'slip_gaji': slip_gaji
                #     })

                try:
                    time_out_obj = datetime.strptime(time_out, '%H:%M')
                    time_in_obj = datetime.strptime(time_in, '%H:%M')
                    time_work_obj = datetime.strptime(time_work, '%H:%M')
                    jam_selesai_obj = datetime.strptime(jam_selesai, '%H:%M')
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
                izin.time_out = time_out_obj.time()
                izin.time_in = time_in_obj.time()
                izin.jam_selesai = jam_selesai_obj.time()
                izin.time_work = time_work_obj.time()
                izin.nilai_izin = nilai_izin
                izin.potongan = potongan

            izin.save()
            
            messages.success(request, 'Izin updated successfully')
            return redirect('izin_read', penggajian_id=penggajian_id, slip_gaji_id=slip_gaji_id)

        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'page/dashboard/izin_keluar_masuk/update.html', {
                'izin': izin,
                'slip_gaji': slip_gaji
            })
        except Exception as e:
            print(e)
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

@login_required
def kasbon_read(request, user_id):
    """
    View to display kasbon (cash advance) records for a specific user.
    Orders records by creation date.
    """
    user = get_object_or_404(User, pk=user_id)
    kasbons = Kasbon.objects.filter(user=user).order_by('-created_at')
    return render(request, 'page/dashboard/kasbon/read.html', {
        'kasbons': kasbons,
        'user': user
    })

@login_required
def kasbon_create(request, user_id):
    """
    Create a new kasbon (cash advance) record for a user.
    Validates input data and handles both GET and POST requests.
    """
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == "POST":
        try:
            nilai_kasbon = request.POST.get('nilai_kasbon')
            keterangan = request.POST.get('keterangan')
            date = request.POST.get('date')

            if not all([nilai_kasbon, keterangan, date]):
                messages.error(request, "All fields are required")
                return render(request, 'page/dashboard/kasbon/create.html', {'user': user})

            kasbon = Kasbon.objects.create(
                user=user,
                nilai_kasbon=float(nilai_kasbon.replace(',', '')),
                keterangan=keterangan,
                date=date,
                status='pending'
            )
            
            messages.success(request, 'Kasbon created successfully')
            return redirect('kasbon_read', user_id=user_id)
            
        except ValueError as e:
            messages.error(request, "Please enter valid numeric values for nilai kasbon")
        except Exception as e:
            messages.error(request, "An error occurred while creating the record")
            
    return render(request, 'page/dashboard/kasbon/create.html', {'user': user})

@login_required
def kasbon_update(request, pk, user_id):
    """
    Update an existing kasbon (cash advance) record.
    Validates input data and handles both GET and POST requests.
    """
    kasbon = get_object_or_404(Kasbon, pk=pk)
    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        try:
            nilai_kasbon = request.POST.get('nilai_kasbon')
            keterangan = request.POST.get('keterangan')
            date = request.POST.get('date')
            status = request.POST.get('status')
            approval = request.POST.get('approval')

            if approval != 'true':
                if not all([nilai_kasbon, keterangan, date, status]):
                    messages.error(request, "All fields are required")
                    return render(request, 'page/dashboard/kasbon/update.html', {
                        'kasbon': kasbon,
                        'user': user
                    })

                kasbon.nilai_kasbon = float(nilai_kasbon.replace(',', ''))
                kasbon.keterangan = keterangan
                kasbon.date = date
                kasbon.status = status
                kasbon.save()
                
                messages.success(request, 'Kasbon updated successfully')
                return redirect('kasbon_read', user_id=user_id)
            else:
                if not all([approval]):
                    messages.error(request, "All fields are required")
                    return render(request, 'page/dashboard/kasbon/update.html', {
                        'kasbon': kasbon,
                        'user': user
                    })
                kasbon.status = status
                kasbon.save()
                messages.success(request, 'Kasbon updated successfully')
                return redirect('kasbon_read', user_id=user_id)

        except ValueError as e:
            messages.error(request, "Please enter valid numeric values for nilai kasbon")
        except Exception as e:
            messages.error(request, "An error occurred while updating the record")

    return render(request, 'page/dashboard/kasbon/update.html', {
        'kasbon': kasbon,
        'user': user
    })

@login_required
def kasbon_delete(request, pk, user_id):
    """
    Delete a kasbon (cash advance) record.
    Only allows POST method for deletion.
    """
    kasbon = get_object_or_404(Kasbon, pk=pk)
    if request.method == "POST":
        kasbon.delete()
        messages.success(request, 'Kasbon deleted successfully')
        return redirect('kasbon_read', user_id=user_id)
    return HttpResponse('Method not allowed', status=405)


@login_required
def generate_slip_gaji_pdf(request, penggajian_id, slip_gaji_id):
    # Ambil data yang diperlukan
    slip_gaji = get_object_or_404(SlipGaji, pk=slip_gaji_id)
    penggajian = get_object_or_404(Penggajian, pk=penggajian_id)
    izin_list = slip_gaji.izin_list.all()
    kasbon_list = Kasbon.objects.filter(slip_gaji=slip_gaji, status='selesai')

    total_nilai_izin = sum(izin.nilai_izin for izin in izin_list)
    total_upah_harian = sum(izin.upah_harian for izin in izin_list)
    total_kasbon = sum(kasbon.nilai_kasbon for kasbon in kasbon_list)
    
    # Buat response dengan content type PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="slip_gaji_{slip_gaji.user.username}_{penggajian.month}.pdf"'
    
    # Buat buffer untuk PDF
    buffer = BytesIO()
    
    # Create PDF document with improved margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=portrait(letter),
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=50
    )
    
    elements = []
    
    # Enhanced text styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=15,
        spaceAfter=30,
        textColor=colors.HexColor('#1a237e')
    ))
    styles.add(ParagraphStyle(
        name='Subtitle',
        parent=styles['Heading2'],
        alignment=TA_CENTER,
        fontSize=16,
        spaceAfter=20,
        textColor=colors.HexColor('#283593')
    ))
    styles.add(ParagraphStyle(
        name='EmployeeInfo',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6,
        textColor=colors.HexColor('#37474f')
    ))
    styles.add(ParagraphStyle(
        name='Right',
        parent=styles['Normal'],
        alignment=TA_RIGHT,
        fontSize=12,
        textColor=colors.HexColor('#37474f')
    ))

    # Header with company logo placeholder
    elements.append(Paragraph("SLIP GAJI", styles['CustomTitle']))
    elements.append(Paragraph(f"Periode: {penggajian.month}", styles['Subtitle']))

    gaji = TableGaji.objects.get(user=slip_gaji.user)
    
    # Employee information in a more structured format
    elements.append(Paragraph(f"Nama: {slip_gaji.user.get_full_name() or slip_gaji.user.username}", styles['EmployeeInfo']))
    elements.append(Paragraph(f"Gaji: Rp {gaji.gaji_pokok:,.0f}", styles['EmployeeInfo']))
    elements.append(Paragraph(f"Tanggal Cetak: {datetime.now().strftime('%d/%m/%Y')}", styles['EmployeeInfo']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Table data with improved formatting for izin
    elements.append(Paragraph("Data Izin Keluar Masuk", styles['Subtitle']))
    data = [
        ['No', 'Tanggal', 'Jam Izin Keluar', 'Jam Izin Masuk', 'Jam Masuk Kerja', 'Upah Harian', 'Potongan']
    ]
    
    # Initialize table style commands
    table_style_commands = [
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Content styling
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#37474f')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        
        # Total row styling
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e3f2fd')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (4, -1), (5, -1), 'RIGHT'),
        
        # Grid styling
        ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#90a4ae')),
        ('BOX', (0, -1), (-1, -1), 1, colors.HexColor('#1a237e')),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#1a237e')),
        ('ALIGN', (5, 1), (5, -1), 'RIGHT'),
    ]
    
    for i, izin in enumerate(izin_list, 1):
        potongan_text = "5%" if izin.potongan else "-"
        
        row_data = [
            i,
            izin.date.strftime('%d/%m/%Y') if izin.date else "-",
            izin.time_out.strftime('%H:%M') if izin.time_out else "-",
            izin.time_in.strftime('%H:%M') if izin.time_in else "-",
            izin.time_work.strftime('%H:%M') if izin.time_work else "-",
            f"Rp {izin.upah_harian:,.0f}",
            potongan_text
        ]
        data.append(row_data)
        
        if izin.status_off:
            table_style_commands.append(
                ('BACKGROUND', (0, len(data)-1), (-1, len(data)-1), colors.pink)
            )
    
    data.append(['', '', '', '', 'Total Upah Harian', f"Rp {total_upah_harian:,.0f}", ''])
    
    # Enhanced table styling for izin
    table = Table(data, colWidths=[0.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.5*inch, 0.8*inch])
    table.setStyle(TableStyle(table_style_commands))
    
    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))

    # Table data for kasbon
    elements.append(Paragraph("Data Kasbon", styles['Subtitle']))
    kasbon_data = [
        ['No', 'Tanggal', 'Nilai Kasbon', 'Keterangan', 'Status']
    ]
    
    for i, kasbon in enumerate(kasbon_list, 1):
        kasbon_data.append([
            i,
            kasbon.date.strftime('%d/%m/%Y') if kasbon.date else "-",
            f"Rp {kasbon.nilai_kasbon:,.0f}",
            kasbon.keterangan,
            kasbon.status
        ])
    
    kasbon_data.append(['', '', f"Total Kasbon: Rp {total_kasbon:,.0f}", '', ''])
    
    # Enhanced table styling for kasbon
    kasbon_table = Table(kasbon_data, colWidths=[0.5*inch, 1.2*inch, 1.5*inch, 3*inch, 1*inch])
    kasbon_table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Content styling
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#37474f')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        
        # Total row styling
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e3f2fd')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('SPAN', (2, -1), (4, -1)),
        ('ALIGN', (2, -1), (2, -1), 'CENTER'),
        
        # Grid styling
        ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#90a4ae')),
        ('BOX', (0, -1), (-1, -1), 1, colors.HexColor('#1a237e')),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#1a237e')),
    ]))
    
    elements.append(kasbon_table)
    
    # Summary section with improved styling
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(f"Total Gaji Bersih: Rp {slip_gaji.gaji_bersih:,.0f}", 
                            ParagraphStyle('GajiBersih', 
                                         parent=styles['Right'],
                                         fontSize=14,
                                         textColor=colors.HexColor('#1a237e'),
                                         fontName='Helvetica-Bold')))
    
    # Signature section with improved layout
    elements.append(Spacer(1, 1*inch))
    elements.append(Paragraph("Mengetahui,", styles['Right']))
    elements.append(Spacer(1, 0.7*inch))
    elements.append(Paragraph("_________________", styles['Right']))
    elements.append(Paragraph("Manager", 
                            ParagraphStyle('SignatureTitle',
                                         parent=styles['Right'],
                                         fontSize=10,
                                         textColor=colors.HexColor('#37474f'))))
    
    # Generate PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response
