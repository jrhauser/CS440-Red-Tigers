from django.db import models
from django.conf import settings

# Create your models here.
class Hello(models.Model):
    id = models.IntegerField(default=0, primary_key=True)
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text

class Order(models.Model):
    orderID = models.SmallAutoField(primary_key=True, unique=True, default= 10)
    timestamp = models.DateTimeField(auto_now_add=True)
    productID = models.ForeignKey('Listing', on_delete=models.RESTRICT, default=1)
    quantity = models.PositiveSmallIntegerField(null=False)

class Device(models.Model):
    deviceID = models.SmallAutoField(primary_key=True, unique=True, null=False, default=11)
    TYPE_CHOICES = (
        ('CPU', 'CPU'),
        ('GPU', 'GPU'),
        ('RAM', 'RAM'),
        ('SSD', 'SSD'),
        ('HDD', 'HDD'),
        ('PSU', 'PSU'),
        ('MOBO', 'MOTHERBOARD'),
        ('CASE', 'CASE'),
        ('COOLER', 'COOLER'),
        ('FAN', 'FAN')
    )
    deviceType = models.CharField(max_length=12, choices=TYPE_CHOICES, null=False)
    brand = models.CharField(max_length=30, null=False)
    model = models.CharField(max_length=30, null=False)
    line = models.CharField(max_length=30)
    platform = models.CharField(max_length=20)
    storage = models.CharField(max_length=20)
    power = models.PositiveSmallIntegerField(null=True)

class Listing(models.Model):
    listingID = models.SmallAutoField(primary_key=True, unique=True,default=12)
    deviceID = models.ForeignKey(Device, on_delete=models.RESTRICT, default=14)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveSmallIntegerField()
    sellerID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, default=2)
