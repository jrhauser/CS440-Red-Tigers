from django.http import Http404, HttpResponse
from django.contrib import auth
from django.template import loader
from django.db import connection, transaction
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
        cursor.execute('SELECT * FROM RedTiger_listing WHERE quantity > 0')
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

    # Check for CPU and MOBO platform compatibility
    cpu_platform = None
    mobo_platform = None
    for item in cart_items:
        device = item.listingID.deviceID
        if device.deviceType == 'CPU' and cpu_platform is None:
            cpu_platform = device.platform
        elif device.deviceType in ('MOBO', 'MOTHERBOARD') and mobo_platform is None:
            mobo_platform = device.platform
    platform_warning = None
    if cpu_platform and mobo_platform and cpu_platform != mobo_platform:
        platform_warning = f"Warning: The CPU (platform: {cpu_platform}) and Motherboard (platform: {mobo_platform}) in your cart are not compatible. Please check their socket/platform before purchasing."

    return render(request, "redtiger/checkout.html", {
        'cart_items': cart_items,
        'total': total,
        'quantity_range': range(1, 21),
        'platform_warning': platform_warning,
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
    # Fetch order history for this user (no OrderItem, just Order, Listing, Device)
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT o.orderID, o.timestamp, o.quantity, l.price, l.listingID, l.deviceID_id, d.brand, d.model, d.deviceType
            FROM RedTiger_Order o
            JOIN RedTiger_listing l ON o.productID_id = l.listingID
            JOIN RedTiger_device d ON l.deviceID_id = d.deviceID
            WHERE o.userID_id = %s
            ORDER BY o.timestamp DESC, o.orderID DESC
        ''', [user[0].id])
        order_rows = namedtuplefetchall(cursor)
    # Build orders list with nested product and device info for template compatibility
    orders = []
    for row in order_rows:
        order = {
            'orderID': row.orderID,
            'timestamp': row.timestamp,
            'quantity': row.quantity,
            'price': row.price,
            'productID': {
                'listingID': row.listingID,
                'deviceID': {
                    'brand': row.brand,
                    'model': row.model,
                    'deviceType': row.deviceType,
                }
            }
        }
        orders.append(order)
    if not address:
        return render(request, 'redtiger/userprofile.html', {
            'user': request.user,
            'selling_history': selling_history,
            'address': None,
            'orders': orders
        })        
    return render(request, 'redtiger/userprofile.html', {
        'user': request.user,
        'selling_history': selling_history,
        'address': address[0],
        'orders': orders
    })

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
        listing = Listing.objects.raw("SELECT * FROM RedTiger_listing WHERE listingID = %s", [listing_id])
        if not listing:
            raise Http404("The listing you are trying to add to cart doesn't exist")
        user = request.user
        cart_item = Cart.objects.raw("SELECT * FROM RedTiger_cart WHERE listingID_id = %s AND userID_id = %s", [listing[0].listingID, user.id])
        print(user.id)
        if not cart_item:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO RedTiger_cart VALUES (NULL, %s, %s, %s)", [quantity, user.id, listing[0].listingID])
            return redirect('index')
        with connection.cursor() as cursor:
            quantity += 1
            cursor.execute("UPDATE RedTiger_cart SET quantity = %s", [quantity])
        return redirect('index')

    return redirect('index')

@login_required
@require_POST
def remove_from_cart(request, item_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM RedTiger_cart WHERE id = %s AND userID_id = %s", [item_id, request.user.id])
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
        WHERE l.quantity > 0
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
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT deviceType FROM RedTiger_device")
        all_types = namedtuplefetchall(cursor)
        cursor.execute("SELECT DISTINCT brand FROM RedTiger_device")
        all_brands = namedtuplefetchall(cursor)
    all_types = sorted(set(all_types))  # Ensure unique and sorted device types
    all_brands = sorted(set(all_brands))
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
        exists = False
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM auth_user WHERE username = %s OR email = %s", [username, email])
            if cursor.fetchone() is not None:
                exists = True
        if exists:
            return render(request, "redtiger/signup.html", {"error": "Username or email already exists."})
        '''
            Create User Query, not used because Django doesn't like it
            INSERT INTO RedTiger_auth (password, last_login, is_superuser, username, first_name, last_name
                email, is_staff, is_active, date_joined) 
                VALUES ('password', NOW(), 0, 'username', 'first_name', 'last_name', 'email', 0, 1, NOW())
        '''
        user = User.objects.create_user(username=username, password=password, email=email)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        auth.login(request, user)
        return redirect('index')
    else:
        return render(request, "redtiger/signup.html")

@login_required
def process_purchase(request):
    user_id = request.user.id
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT listingID_id, quantity FROM RedTiger_cart WHERE userID_id = %s", [user_id]
                )
                cart_items = namedtuplefetchall(cursor)
                for item in cart_items:
                    # Insert one order per cart item
                    cursor.execute(
                        "INSERT INTO RedTiger_Order (userID_id, productID_id, quantity, timestamp) VALUES (%s, %s, %s, NOW())",
                        [user_id, item.listingID_id, item.quantity]
                    )
                    cursor.execute(
                        "UPDATE RedTiger_listing SET quantity = quantity - %s WHERE listingID = %s AND quantity >= %s",
                        [item.quantity, item.listingID_id, item.quantity]
                    )
                    if cursor.rowcount == 0:
                        raise Exception("Insufficient stock for listing ID: %s" % item.listingID_id)
                cursor.execute(
                    "DELETE FROM RedTiger_cart WHERE userID_id = %s", [user_id]
                )
            return redirect('userprofile', username=request.user.username)
    except Exception as e:
        with connection.cursor() as cursor:
            cursor.execute("ROLLBACK")
        return render(request, "redtiger/checkout.html", {"error": str(e)})