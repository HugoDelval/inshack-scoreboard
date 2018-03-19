from django.http import HttpRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def home(request: HttpRequest):
    return render(request, 'information/home.html')

