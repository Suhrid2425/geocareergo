from django.shortcuts import render


def home(request):

    return render(request, 'core/home.html')

def mentorship(request):
    return render(
        request,
        "core/mentorship.html"
    )