from django.shortcuts import render


def view_main_page(request):
    return render(request, "mainpage.html")
