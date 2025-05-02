from django.contrib import admin
from .models import Order, Device, Listing, UserShipping
# Register your models here.
admin.site.register([Order, Device, Listing, UserShipping])