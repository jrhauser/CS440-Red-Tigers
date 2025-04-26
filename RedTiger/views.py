from django.http import HttpResponse
from django.contrib import auth
from django.template import loader
from django.db import connection
from collections import namedtuple
from django.shortcuts import redirect, render, get_object_or_404
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Listing

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
    template = loader.get_template("redtiger/index.html")
    return HttpResponse(template.render(context))

def checkout(request):
    template = loader.get_template("redtiger/checkout.html")
    return HttpResponse(template.render())

def login(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.method.get('password')

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            return redirect('login')
    else:
        template = loader.get_template("redtiger/login.html")
    return HttpResponse(template.render())

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

def buy(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    # Logic for handling the purchase can be added here
    return JsonResponse({"message": "Purchase successful", "listing_id": listing_id})