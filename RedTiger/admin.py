from django.contrib import admin
from .models import Hello, Order, Device
# Register your models here.
admin.site.register([Hello, Order, Device])