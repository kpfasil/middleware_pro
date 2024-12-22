from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def ip_block(request):
    return HttpResponse("Working! Status 200")