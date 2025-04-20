from django.contrib import admin
from .models import Hello, Order
# Register your models here.
admin.site.register([Hello, Order])