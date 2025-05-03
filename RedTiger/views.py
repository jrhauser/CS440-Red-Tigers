from django.http import HttpResponse
from django.contrib import auth
from django.template import loader
from django.db import connection
from collections import namedtuple
from django.shortcuts import redirect, render, get_object_or_404
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Listing, Cart, Device, UserShipping
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
            seller = User.objects.raw("SELECT id, first_name, last_name FROM auth_user WHERE id = %s", [listing.seller_id])
            address = UserShipping.objects.raw("SELECT id, city, state FROM RedTiger_usershipping WHERE user_id = %s", [listing.seller_id])
        except User.DoesNotExist:
            seller = None
        listing_dict['seller'] = seller[0]
        if address:
            listing_dict['address'] = address[0]
        listings.append(listing_dict)
    context = {
        'devices': devices,
        'listings': listings,
    }
    return render(request, "redtiger/index.html", context)

@login_required
def checkout(request):
    cart_items = Cart.objects.raw("SELECT id, listingID_id, userID_id FROM RedTiger_cart WHERE userID_id = %s", [request.user.id])
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
    user = User.objects.raw("SELECT username, id FROM auth_user WHERE username = %s", [username])
    if request.method == "POST":
        print(str(user[0].id) + "|" + str(request.POST.get('shipping_address')) + '|' + str(request.POST.get('city')) + '|' + str(request.POST.get('state')))
        with connection.cursor() as cursor:
            cursor.execute("REPLACE INTO RedTiger_usershipping (user_id, shipping_address, city, state) VALUES (%s, %s, %s, %s)", 
                                 [user[0].id, request.POST.get('shipping_address'), request.POST.get('city'), request.POST.get('state')])
        return(redirect('userprofile', username))
    selling_history = Listing.objects.raw("SELECT * FROM RedTiger_listing WHERE seller_id = %s", [user[0].id])
    address = UserShipping.objects.raw("SELECT * FROM RedTiger_usershipping WHERE user_id = %s", [user[0].id])
    if not address:
            return render(request, 'redtiger/userprofile.html', {'user': request.user, 'selling_history': selling_history, 'address': None})        
    return render(request, 'redtiger/userprofile.html', {'user': request.user, 'selling_history': selling_history, 'address': address[0]})

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
        # TODO: Change to SQL 
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
    cart_item = Cart.objects.raw("SELECT * FROM RedTiger_cart WHERE id = %s AND userID_id = %s", [item_id, request.user.id])
    cart_item.delete()
    return redirect('checkout')

@login_required
@require_POST
def update_cart_quantity(request, item_id):
    cart_item = Cart.objects.raw("SELECT * FROM RedTiger_cart WHERE id = %s AND userID_id = %s", [item_id, request.user.id])[0]
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
        cart_item.quantity = quantity
        cart_item = Cart.objects.raw("UPDATE RedTiger_cart SET quantity = %s WHERE id = %s", [quantity, item_id])
    except (ValueError, TypeError):
        pass  # Ignore invalid input
    return redirect('checkout')

@login_required
def create_listing(request):
    devices = Device.objects.raw("SELECT * FROM RedTiger_device")
    error = None

    if request.method == "POST":
        print("POST data:", request.POST)  # Debug: print all POST data
        device_type = request.POST.get('deviceType')
        if request.POST.get('device') == 'new':
            if not device_type:
                error = "Please select a device type when creating a new device."
                print("Error:", error)
                return render(request, "redtiger/createlisting.html", {"devices": devices, "error": error})
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
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO RedTiger_device (deviceType, brand, line, model, platform, power, storage, image_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    [device_type, brand, line, model, platform, power, storage, image_url]
                )
                cursor.execute("SELECT LAST_INSERT_ID()")
                device_id = cursor.fetchone()[0]
            print(f"Device created: {device_id}")
        elif request.POST.get('device'):
            device_id = int(request.POST.get('device'))
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM RedTiger_device WHERE deviceID = %s", [device_id])
                device_result = cursor.fetchone()
                if not device_result:
                    error = "Selected device does not exist."
                    print("Error:", error)
                    return render(request, "redtiger/createlisting.html", {"devices": devices, "error": error})
            print(f"Using existing device: {device_id}")
        else:
            error = "Please select or create a device."
            print("Error:", error)
            return render(request, "redtiger/createlisting.html", {"devices": devices, "error": error})

        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        condition = request.POST.get('condition')
        print(f"Creating listing: {price=}, {quantity=}, {condition=}, {device_id=}")

        if not (price and quantity and condition):
            error = "Please fill in all required fields for the listing (price, quantity, condition)."
            print("Error:", error)
            return render(request, "redtiger/createlisting.html", {"devices": devices, "error": error})

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO RedTiger_listing (deviceID_id, price, quantity, `condition`, seller_id) VALUES (%s, %s, %s, %s, %s)",
                [device_id, price, quantity, condition, request.user.id]
            )
        print("Listing created successfully!")
        return redirect('index')

    return render(request, "redtiger/createlisting.html", {"devices": devices, "error": error})

@login_required
@require_POST
def edit_listing(request, listing_id):
    price = request.POST.get('price')
    quantity = request.POST.get('quantity')
    if price is not None and quantity is not None:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE RedTiger_listing SET price = %s, quantity = %s WHERE listingID = %s AND seller_id = %s",
                [price, quantity, listing_id, request.user.id]
            )
    else:
        error = "Please fill in all required fields for the listing (price, quantity)."
        # Optionally, fetch the listing to display in the form
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM RedTiger_listing WHERE listingID = %s AND seller_id = %s", [listing_id, request.user.id])
            listing = cursor.fetchone()
        return render(request, "redtiger/editlisting.html", {"listing": listing, "error": error})
    
    return redirect('userprofile', username=request.user.username)

@login_required
@require_POST
def delete_listing(request, listing_id):
    # TODO: remove?
    listing = Listing.objects.raw("SELECT * FROM RedTiger_listing WHERE listingID = %s AND seller_id = %s", [listing_id, request.user.id])
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM RedTiger_listing WHERE listingID = %s AND seller_id = %s", [listing_id, request.user.id])
    return redirect('userprofile', username=request.user.username)

def all_listings(request):
    device_type = request.GET.getlist('device_type')
    brand = request.GET.getlist('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    devices = Device.objects.raw("SELECT * FROM RedTiger_device")

    # Build SQL query dynamically, select all device columns with alias
    sql = """
        SELECT l.*, 
               d.deviceID as d_deviceID, d.deviceType as d_deviceType, d.brand as d_brand, d.model as d_model, d.line as d_line, 
               d.platform as d_platform, d.storage as d_storage, d.power as d_power, d.image_url as d_image_url
        FROM RedTiger_listing l
        INNER JOIN RedTiger_device d ON l.deviceID_id = d.deviceID
        WHERE 1=1
    """
    params = []
    if device_type:
        sql += " AND d.deviceType IN ({})".format(','.join(['%s'] * len(device_type)))
        params.extend(device_type)
    if brand:
        sql += " AND d.brand IN ({})".format(','.join(['%s'] * len(brand)))
        params.extend(brand)
    if min_price:
        sql += " AND l.price >= %s"
        params.append(min_price)
    if max_price:
        sql += " AND l.price <= %s"
        params.append(max_price)

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        listings_raw = namedtuplefetchall(cursor)

    # Attach deviceID as a namedtuple for template compatibility
    DeviceTuple = namedtuple('DeviceTuple', ['deviceID', 'deviceType', 'brand', 'model', 'line', 'platform', 'storage', 'power', 'image_url'])
    listings = []
    for l in listings_raw:
        device = DeviceTuple(
            l.d_deviceID, l.d_deviceType, l.d_brand, l.d_model, l.d_line, l.d_platform, l.d_storage, l.d_power, l.d_image_url
        )
        # Convert to dict to allow attribute access in template
        listing_dict = l._asdict()
        listing_dict['deviceID'] = device
        listings.append(type('ListingObj', (), listing_dict))
    # TODO: CHANGE TO SQL
    all_types = Device.objects.values_list('deviceType', flat=True).distinct()
    all_types = sorted(set(all_types))  # Ensure unique and sorted device types
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

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        #TODO: Change to SQL
        if User.objects.filter(username=username).exists():
            return render(request, "redtiger/signup.html", {"error": "Username already exists."})
        if User.objects.filter(email=email).exists():
            return render(request, "redtiger/signup.html", {"error": "Email already exists."})

        # TODO: ADD CORRESPONDING QUERY EVEN THO ITS NOT USED
        user = User.objects.create_user(username=username, password=password, email=email)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        auth.login(request, user)
        return redirect('index')
    else:
        return render(request, "redtiger/signup.html")

