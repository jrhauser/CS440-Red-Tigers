from django.http import HttpResponse
from .models import Hello

def index(request):
    text = Hello.objects.all()
    return HttpResponse(text)