from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from penggaji.models import TableGaji
from mysite.utils.helpers import dd

@login_required
def pengelolaKaryawan_view(request):
    karyawan_list = User.objects.all()
        
    context = {
        'karyawan_list': karyawan_list,
    }
    
    return render(request, 'page/dashboard/pengelolaKaryawan/read.html', context)

@login_required
def pengelolaKaryawan_create(request):
    if request.method == 'POST':
        # Get form data with validation
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirmation = request.POST.get('password_confirmation', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'
        gaji_pokok = request.POST.get('gaji_pokok', '0')
        
        # Validate password confirmation
        if password != password_confirmation:
            messages.error(request, 'Passwords do not match.')
            return redirect('pengelolaKaryawan_create')

        # Validate required fields
        if not all([username, email, password]):
            messages.error(request, 'Username, email and password are required fields.')
            return redirect('pengelolaKaryawan_create')

        try:
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                return redirect('pengelolaKaryawan_create')

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists.')
                return redirect('pengelolaKaryawan_create')

            # Create user with all fields in one operation for better atomicity
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=is_active,
                is_staff=is_staff,
                is_superuser=is_superuser
            )
            
            # Create TableGaji instance with proper validation
            try:
                gaji_pokok = float(gaji_pokok.replace(',', ''))
                if gaji_pokok < 0:
                    raise ValueError("Salary cannot be negative")
                    
                TableGaji.objects.create(
                    user=user,
                    gaji_pokok=gaji_pokok
                )
            except ValueError as e:
                user.delete()  # Rollback user creation
                messages.error(request, f'Invalid salary value: {str(e)}')
                return redirect('pengelolaKaryawan_create')
            
            messages.success(request, 'Employee successfully created.')
            return redirect('pengelolaKaryawan_read')
            
        except Exception as e:
            messages.error(request, f'Error creating employee: {str(e)}')
            return redirect('pengelolaKaryawan_create')
            
    return render(request, 'page/dashboard/pengelolaKaryawan/create.html')
    

@login_required
def pengelolaKaryawan_update(request, id):
    try:
        user = User.objects.get(id=id)
        gaji = TableGaji.objects.get(user=user)
    except (User.DoesNotExist, TableGaji.DoesNotExist):
        messages.error(request, 'Employee not found.')
        return redirect('pengelolaKaryawan')

    if request.method == 'POST':
        # Get form data with validation
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirmation = request.POST.get('password_confirmation', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'
        gaji_pokok = request.POST.get('gaji_pokok', '0')

        # Validate password confirmation if password is provided
        if password:
            if password != password_confirmation:
                messages.error(request, 'Passwords do not match.')
                return redirect('pengelolaKaryawan_update', id=id)

        # Validate required fields
        if not all([username, email]):
            messages.error(request, 'Username and email are required fields.')
            return redirect('pengelolaKaryawan_update', id=id)

        try:
            # Check if username exists and belongs to different user
            if User.objects.filter(username=username).exclude(id=id).exists():
                messages.error(request, 'Username already exists.')
                return redirect('pengelolaKaryawan_update', id=id)

            # Check if email exists and belongs to different user
            if User.objects.filter(email=email).exclude(id=id).exists():
                messages.error(request, 'Email already exists.')
                return redirect('pengelolaKaryawan_update', id=id)

            # Update user fields
            user.username = username
            user.email = email
            if password:
                user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = is_active
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.save()

            # Update salary with validation
            try:
                # Remove thousand separators and convert to float
                gaji_pokok = float(gaji_pokok.replace(',', ''))
                if gaji_pokok < 0:
                    raise ValueError("Salary cannot be negative")
                
                gaji.gaji_pokok = gaji_pokok
                gaji.save()
            except ValueError as e:
                messages.error(request, f'Invalid salary value: {str(e)}')
                return redirect('pengelolaKaryawan_update', id=id)

            messages.success(request, 'Employee successfully updated.')
            return redirect('pengelolaKaryawan_read')

        except Exception as e:
            messages.error(request, f'Error updating employee: {str(e)}')
            return redirect('pengelolaKaryawan_update', id=id)

    context = {
        'user': user,
        'gaji': gaji,
        'title': 'Edit Employee'
    }
    
    return render(request, 'page/dashboard/pengelolaKaryawan/update.html', context)

@login_required
def pengelolaKaryawan_delete(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        messages.error(request, 'Employee not found.')
        return redirect('pengelolaKaryawan_read')
    
    if request.method == "POST":
        user.delete()
        messages.success(request, 'Employee data has been successfully deleted.')
        return redirect('pengelolaKaryawan_read')
        
    return HttpResponse('Method not allowed', status=405)
