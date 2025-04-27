from django.http import HttpResponse
from django.contrib import auth
from django.template import loader
from django.db import connection
from collections import namedtuple
from django.shortcuts import redirect, render, get_object_or_404
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Listing, Cart
from django.middleware.csrf import get_token

def namedtuplefetchall(cursor):
    """
    Return all rows from a cursor as a namedtuple.
    Assume the column names are unique.
    """
    desc = cursor.description
    nt_result = namedtuple("result", [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def index(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM RedTiger_device')
        devices = namedtuplefetchall(cursor)
        listings = cursor.execute('SELECT * FROM RedTiger_listing')
        listings = namedtuplefetchall(cursor)

    context = {
        'devices': devices,
        'listings': listings,
    }
    return render(request, "redtiger/index.html", context)

def checkout(request):
    #template = loader.get_template("redtiger/checkout.html")
    return render(request, "redtiger/checkout.html")

def login(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')  # Fixed typo

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            return redirect('login')
    else:
      #  template = loader.get_template("redtiger/login.html")
      return render(request, "redtiger/login.html")
   # return render(request, "redtiger/login.html")

@login_required
def userprofile(request, username):
    user = User.objects.get(username=username)
    return render(request, 'redtiger/userprofile.html', {'user': request.user})

def listing(request, listing_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM RedTiger_listing WHERE id = %s', [listing_id])
        listing = namedtuplefetchall(cursor)[0]
        cursor.execute('SELECT * FROM RedTiger_device WHERE id = %s', [listing.device_id])
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

        return redirect('cart')

    return redirect('index')