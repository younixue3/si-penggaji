from django.shortcuts import render

def landing_page(request):
    """View function for the landing page."""
    return render(request, 'page/landing_page.html')
