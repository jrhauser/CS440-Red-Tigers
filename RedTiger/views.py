from django.http import HttpResponse
from .models import Hello
from django.template import loader

def index(request):
    text = Hello.objects.raw("SELECT * FROM RedTiger_hello")
    return HttpResponse(text)
def home(request):
    template = loader.get_template("redtiger/index.html")
    return HttpResponse(template.render())