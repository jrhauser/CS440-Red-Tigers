from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
# Create your models here.

'''
DDL for users table:

CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) AUTO_INCREMENT=3
'''





'''
DDL for orders table:

CREATE TABLE `RedTiger_order` (
  `orderID` smallint NOT NULL AUTO_INCREMENT,
  `timestamp` datetime(6) NOT NULL,
  `quantity` smallint unsigned NOT NULL,
  `productID_id` smallint NOT NULL,
  PRIMARY KEY (`orderID`),
  KEY `RedTiger_order_productID_id_774363ed_fk_RedTiger_` (`productID_id`),
  CONSTRAINT `RedTiger_order_productID_id_774363ed_fk_RedTiger_` FOREIGN KEY (`productID_id`) REFERENCES `RedTiger_listing` (`listingID`),
  CONSTRAINT `RedTiger_order_chk_1` CHECK ((`quantity` >= 0))
)
'''
class Order(models.Model):
    orderID = models.SmallAutoField(primary_key=True, unique=True, default= 10)
    timestamp = models.DateTimeField(auto_now_add=True)
    productID = models.ForeignKey('Listing', on_delete=models.RESTRICT, default=1)
    quantity = models.PositiveSmallIntegerField(null=False)
    userID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, default=2)

'''
DDL for device table:
CREATE TABLE `RedTiger_device` (
  `deviceID` smallint NOT NULL AUTO_INCREMENT,
  `deviceType` varchar(12) NOT NULL,
  `brand` varchar(30) NOT NULL,
  `model` varchar(30) NOT NULL,
  `line` varchar(30) DEFAULT NULL,
  `platform` varchar(20) NOT NULL,
  `storage` varchar(20) DEFAULT NULL,
  `power` smallint unsigned DEFAULT NULL,
  `image_url` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`deviceID`),
  CONSTRAINT `RedTiger_device_chk_1` CHECK ((`power` >= 0))
) AUTO_INCREMENT=32

'''
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
'''
DDL for listing table:

CREATE TABLE `RedTiger_listing` (
  `listingID` smallint NOT NULL AUTO_INCREMENT,
  `price` decimal(10,2) NOT NULL,
  `quantity` smallint unsigned NOT NULL,
  `deviceID_id` smallint NOT NULL,
  `seller_id` int NOT NULL,
  `condition` varchar(20) NOT NULL,
  `timestamp` datetime(6) NOT NULL,
  PRIMARY KEY (`listingID`),
  KEY `RedTiger_listing_seller_id_9a5542ce_fk_auth_user_id` (`seller_id`),
  KEY `brand_idx` (`deviceID_id`),
  CONSTRAINT `RedTiger_listing_deviceID_id_2648d33b_fk_RedTiger_` FOREIGN KEY (`deviceID_id`) REFERENCES `RedTiger_device` (`deviceID`),
  CONSTRAINT `RedTiger_listing_seller_id_9a5542ce_fk_auth_user_id` FOREIGN KEY (`seller_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `RedTiger_listing_chk_1` CHECK ((`quantity` >= 0)) AUTO_INCREMENT=10

'''

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
    timestamp = models.DateTimeField(auto_now_add=True)

'''
DDL for cart table:

CREATE TABLE `RedTiger_cart` (
  `id` int NOT NULL AUTO_INCREMENT,
  `quantity` smallint unsigned NOT NULL,
  `userID_id` int NOT NULL,
  `listingID_id` smallint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `RedTiger_cart_userID_id_listingID_id_1a5f017c_uniq` (`userID_id`,`listingID_id`),
  KEY `RedTiger_cart_listingID_id_b0831dc0_fk_RedTiger_` (`listingID_id`),
  CONSTRAINT `RedTiger_cart_listingID_id_b0831dc0_fk_RedTiger_` FOREIGN KEY (`listingID_id`) REFERENCES `RedTiger_listing` (`listingID`),
  CONSTRAINT `RedTiger_cart_userID_id_ada8148a_fk_auth_user_id` FOREIGN KEY (`userID_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `RedTiger_cart_chk_1` CHECK ((`quantity` >= 0))
) 

'''



class Cart(models.Model):
    id = models.AutoField(primary_key=True)  # Add a single primary key
    userID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listingID = models.ForeignKey(Listing, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(null=False)

    class Meta:
        unique_together = ('userID', 'listingID')  # Add a unique constraint

    def __str__(self):
        return str(self.userID) + " " + str(self.listingID) + " " + str(self.quantity)

'''
DDL for UserShipping table:

CREATE TABLE `RedTiger_usershipping` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `shipping_address` varchar(100) NOT NULL,
  `city` varchar(100) NOT NULL,
   `state` ENUM(
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
    ),
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `RedTiger_seller_user_id_d97b4f2c_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) 
'''

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