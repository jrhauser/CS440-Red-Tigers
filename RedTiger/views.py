from django.http import HttpResponse
from .models import Hello

def index(request):
    text = Hello.objects.raw("SELECT * FROM RedTiger_hello")
    return HttpResponse(text)
def home(request):
    return HttpResponse("This is t")