from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
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
    deviceID = models.SmallAutoField(primary_key=True, unique=True, null=False)
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
    line = models.CharField(max_length=30, null=True, blank=True)
    platform = models.CharField(max_length=20)
    storage = models.CharField(max_length=20, null=True, blank=True)
    power = models.PositiveSmallIntegerField(null=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    def __str__(self):
        return self.deviceType + " " + self.brand + " " + self.model

class Listing(models.Model):
    listingID = models.SmallAutoField(primary_key=True, unique=True )
    deviceID = models.ForeignKey(Device, on_delete=models.RESTRICT, default=14)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveSmallIntegerField()
    CONDITION_CHOICES = (
        ('Brand New', 'Brand New'),
        ('Like New', 'Like New'),
        ('Very Good', 'Very Good'),
        ('Good', 'Good'),
        ('Acceptable', 'Acceptable'),
        ('Refurbished', 'Refurbished'),
        ('Used', 'Used')
    )
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, null=False, default='Brand New')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, default=2)

class Cart(models.Model):
    id = models.AutoField(primary_key=True)  # Add a single primary key
    userID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listingID = models.ForeignKey(Listing, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(null=False)

    class Meta:
        unique_together = ('userID', 'listingID')  # Add a unique constraint

    def __str__(self):
        return str(self.userID) + " " + str(self.listingID) + " " + str(self.quantity)

class UserShipping(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shipping_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    CONDITION_CHOICES = [
            ("AL", "AL"), ("AK", "AK"), ("AZ", "AZ"), ("AR", "AR"), ("CA", "CA"), 
    ("CO", "CO"), ("CT", "CT"), ("DE", "DE"), ("FL", "FL"), ("GA", "GA"), 
    ("HI", "HI"), ("ID", "ID"), ("IL", "IL"), ("IN", "IN"), ("IA", "IA"), 
    ("KS", "KS"), ("KY", "KY"), ("LA", "LA"), ("ME", "ME"), ("MD", "MD"), 
    ("MA", "MA"), ("MI", "MI"), ("MN", "MN"), ("MS", "MS"), ("MO", "MO"), 
    ("MT", "MT"), ("NE", "NE"), ("NV", "NV"), ("NH", "NH"), ("NJ", "NJ"), 
    ("NM", "NM"), ("NY", "NY"), ("NC", "NC"), ("ND", "ND"), ("OH", "OH"), 
    ("OK", "OK"), ("OR", "OR"), ("PA", "PA"), ("RI", "RI"), ("SC", "SC"), 
    ("SD", "SD"), ("TN", "TN"), ("TX", "TX"), ("UT", "UT"), ("VT", "VT"), 
    ("VA", "VA"), ("WA", "WA"), ("WV", "WV"), ("WI", "WI"), ("WY", "WY")
    ]
    state = models.CharField(max_length=2, choices=CONDITION_CHOICES)