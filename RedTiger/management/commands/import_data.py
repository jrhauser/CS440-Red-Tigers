import csv
from django.core.management.base import BaseCommand
from RedTiger.models import Device, Listing
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Imports CPU and Motherboard data from CSV files into the Device model and creates a Listing for each device.'

    def handle(self, *args, **kwargs):
        self.import_and_list('RedTiger/data/cpu_data.csv', 'CPU')
        self.import_and_list('RedTiger/data/motherboard_data.csv', 'MOBO')

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
                        seller = User.objects.order_by('id').first()
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
