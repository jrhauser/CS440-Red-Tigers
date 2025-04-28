from django.http import HttpResponse
from django.contrib import auth
from django.template import loader
from django.db import connection
from collections import namedtuple
from django.shortcuts import redirect, render, get_object_or_404
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Listing, Cart, Device
from django.middleware.csrf import get_token
from django.views.decorators.http import require_POST
from django.contrib.auth.views import LogoutView

class LogoutViewAllowGet(LogoutView):
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

def namedtuplefetchall(cursor):
    """
    Return all rows from a cursor as a namedtuple.
    Assume the column names are unique.
    """
    desc = cursor.description
    nt_result = namedtuple("result", [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def index(request):
    from django.contrib.auth.models import User
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM RedTiger_device')
        devices = namedtuplefetchall(cursor)
        cursor.execute('SELECT * FROM RedTiger_listing')
        listings_raw = namedtuplefetchall(cursor)

    # Convert each listing to a dict and attach seller User object
    listings = []
    for listing in listings_raw:
        listing_dict = listing._asdict()
        try:
            seller = User.objects.get(pk=listing.seller_id)
        except User.DoesNotExist:
            seller = None
        listing_dict['seller'] = seller
        listings.append(listing_dict)

    context = {
        'devices': devices,
        'listings': listings,
    }
    return render(request, "redtiger/index.html", context)

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(userID=request.user).select_related('listingID')
    total = sum(item.listingID.price * item.quantity for item in cart_items)
    return render(request, "redtiger/checkout.html", {
        'cart_items': cart_items,
        'total': total,
        'quantity_range': range(1, 21)
    })

def login(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password') 

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            return redirect('login')
    else:
      return render(request, "redtiger/login.html")
  

@login_required
def userprofile(request, username):
    user = User.objects.get(username=username)
    selling_history = user.listing_set.all()
    return render(request, 'redtiger/userprofile.html', {'user': request.user, 'selling_history': selling_history})

def listing(request, listing_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM RedTiger_listing WHERE listingID = %s', [listing_id])
        listing = namedtuplefetchall(cursor)[0]
        cursor.execute('SELECT * FROM RedTiger_device WHERE deviceID = %s', [listing.deviceID_id])
        device = namedtuplefetchall(cursor)[0]

    context = {
        'listing': listing,
        'device': device,
    }
    template = loader.get_template("redtiger/listing.html")
    return render(request, 'redtiger/listing.html', context)

@login_required
def add_to_cart(request, listing_id):
    if request.method == "POST":
        quantity = int(request.POST.get('quantity', 1))

        listing = get_object_or_404(Listing, pk=listing_id)
        user = request.user

        cart_item, created = Cart.objects.get_or_create(
            userID=user,
            listingID=listing,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return redirect('index')

    return redirect('index')

@login_required
@require_POST
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, userID=request.user)
    cart_item.delete()
    return redirect('checkout')

@login_required
@require_POST
def update_cart_quantity(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, userID=request.user)
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
        cart_item.quantity = quantity
        cart_item.save()
    except (ValueError, TypeError):
        pass  # Ignore invalid input
    return redirect('checkout')

@login_required
def create_listing(request):
    devices = Device.objects.all()
    error = None

    if request.method == "POST":
        print("POST data:", request.POST)  # Debug: print all POST data
        device_id = request.POST.get('device')
        device_type = request.POST.get('deviceType')
        # If user is creating a new device, device_id should be 'new'
        if device_id == 'new':
            brand = request.POST.get('brand')
            line = request.POST.get('line')
            model = request.POST.get('model')
            platform = request.POST.get('platform')
            power = request.POST.get('power')
            storage = request.POST.get('storage')
            image_url = request.POST.get('image_url')

            print(f"Creating new device: {brand=}, {line=}, {model=}, {platform=}, {power=}, {storage=}, {image_url=}, {device_type=}")

            # Validate required fields for new device
            if not (brand and model and platform and device_type):
                error = "Please fill in all required fields for the new device (brand, model, platform, and device type)."
                print("Error:", error)
                return render(request, "redtiger/createlisting.html", {"devices": devices, "error": error})

            # Create the new device
            device = Device.objects.create(
                deviceType=device_type,
                brand=brand,
                line=line,
                model=model,
                platform=platform,
                power=power or None,
                storage=storage or None,
                image_url=image_url,
            )
            print(f"Device created: {device}")
        elif device_id and device_id != '':
            # User selected an existing device
            try:
                device = Device.objects.get(pk=device_id)
                print(f"Using existing device: {device}")
            except Device.DoesNotExist:
                error = "Selected device does not exist."
                print("Error:", error)
                return render(request, "redtiger/createlisting.html", {"devices": devices, "error": error})
        else:
            # No device selected or created
            error = "Please select or create a device."
            print("Error:", error)
            return render(request, "redtiger/createlisting.html", {"devices": devices, "error": error})

        # Create the listing
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        condition = request.POST.get('condition')
        print(f"Creating listing: {price=}, {quantity=}, {condition=}, {device=}")

        # Validate required fields for listing
        if not (price and quantity and condition):
            error = "Please fill in all required fields for the listing (price, quantity, condition)."
            print("Error:", error)
            return render(request, "redtiger/createlisting.html", {"devices": devices, "error": error})

        Listing.objects.create(
            deviceID=device,
            price=price,
            quantity=quantity,
            condition=condition,
            seller=request.user
        )
        print("Listing created successfully!")

        return redirect('index')  # After creation, send user back to main page

    return render(request, "redtiger/createlisting.html", {"devices": devices, "error": error})

@login_required
@require_POST
def edit_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id, seller=request.user)
    price = request.POST.get('price')
    quantity = request.POST.get('quantity')
    if price is not None and quantity is not None:
        listing.price = price
        listing.quantity = quantity
        listing.save()
    return redirect('userprofile', username=request.user.username)

@login_required
@require_POST
def delete_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id, seller=request.user)
    listing.delete()
    return redirect('userprofile', username=request.user.username)

def all_listings(request):
    # Get filter parameters from GET request
    device_type = request.GET.getlist('device_type')
    brand = request.GET.getlist('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    listings = Listing.objects.select_related('deviceID', 'seller').all()
    devices = Device.objects.all()

    # Filtering
    if device_type:
        listings = listings.filter(deviceID__deviceType__in=device_type)
    if brand:
        listings = listings.filter(deviceID__brand__in=brand)
    if min_price:
        listings = listings.filter(price__gte=min_price)
    if max_price:
        listings = listings.filter(price__lte=max_price)

    # For filter options
    all_types = Device.objects.values_list('deviceType', flat=True).distinct()
    all_brands = Device.objects.values_list('brand', flat=True).distinct()

    context = {
        'listings': listings,
        'devices': devices,
        'all_types': all_types,
        'all_brands': all_brands,
        'selected_types': device_type,
        'selected_brands': brand,
        'min_price': min_price or '',
        'max_price': max_price or '',
    }
    return render(request, 'redtiger/listing.html', context)