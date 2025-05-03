import csv
import random
from django.core.management.base import BaseCommand
from RedTiger.models import Device, Listing, UserShipping
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Imports CPU and Motherboard data from CSV files into the Device model and creates a Listing for each device.'

    def handle(self, *args, **kwargs):
        self.add_users()
        self.import_and_list('RedTiger/data/cpu_data.csv', 'CPU')
        self.import_and_list('RedTiger/data/motherboard_data.csv', 'MOBO')

    def add_users(self):

        user_data = [
            ("alexjone1", "apple", "alexjone1@yahoo.com", "Alex", "Jones", "123 Maple St", "Denver", "CO"),
            ("johnmayors8", "orange", "johnmayors8@gmail.com", "John", "Mayors", "456 Oak Ave", "Austin", "TX"),
            ("greeen_23", "pear", "greeen_23@hotmail.com", "Christine", "Green", "789 Pine Rd", "Seattle", "WA"),
            ("woods-tyler9", "mango", "woodstyler9@gmail.com", "Tyler", "Woods", "321 Birch Ln", "Chicago", "IL"),
            ("franklin_gta3", "berry", "franklin_gta3@yahoo.com", "Franklin", "Lamar", "654 Cedar Dr", "Miami", "FL"),
            ("tripper8745", "melon", "tripper8745@hotmail.com", "Trever", "Trip", "987 Spruce Ct", "Boston", "MA")
        ]
        for user_tuple in user_data:
            user = User.objects.create_user(username=user_tuple[0], password=user_tuple[1], email=user_tuple[2])
            user.first_name = user_tuple[3]
            user.last_name = user_tuple[4]
            user.save()
            UserShipping.objects.get_or_create(
                user_id = user.id,
                shipping_address=user_tuple[5], 
                city=user_tuple[6], 
                state=user_tuple[7]
            )

    def import_and_list(self, filepath, device_type):
        self.stdout.write(f"Importing {device_type}s from {filepath} and creating listings...")
        try:
            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    brand = row.get('Brand') or row.get('Manufacturer')
                    line = row.get('Line') or None
                    model = row.get('Model') or row.get('Name')
                    platform = row.get('Platform') or row.get('Socket') or ''
                    power = row.get('Power') or ''
                    image_url = row.get('ImageURL') or None

                    if brand and model:
                        device, created = Device.objects.get_or_create(
                            deviceType=device_type,
                            brand=brand.strip(),
                            line=line.strip() if line else None,
                            model=model.strip(),
                            platform=platform.strip() or None,
                            power=power.strip() or None,
                            storage=None,
                            image_url=image_url.strip() if image_url else None
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f"Imported device: {brand} {model}"))
                        # Create a listing for this device
                        sellers = User.objects.all()
                        seller = random.choice(sellers)
                        if seller:
                            Listing.objects.get_or_create(
                                deviceID=device,
                                defaults={
                                    'price': 100.00,
                                    'quantity': 10,
                                    'condition': 'Brand New',
                                    'seller': seller
                                }
                            )
            self.stdout.write(self.style.SUCCESS(f"Successfully imported {device_type}s and created listings from {filepath}"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File {filepath} not found."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing {device_type}s: {str(e)}"))
