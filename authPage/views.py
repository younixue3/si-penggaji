from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache

@csrf_protect
@never_cache
def login_view(request):
    # Redirect if user is already authenticated
    if request.user.is_authenticated:
        return redirect('landing_page')
        
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if username and password:
            # Attempt to authenticate
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # Get next URL from query parameters or default to home
                    next_url = request.GET.get('next', 'landing_page')
                    messages.success(request, f'Welcome back, {user.username}!')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Your account is disabled.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please fill in both username and password.')
            
    return render(request, 'page/login.html', {
        'title': 'Login',
        'next': request.GET.get('next', 'landing_page')
    })

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login_page')
