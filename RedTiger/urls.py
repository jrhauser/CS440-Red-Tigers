from django.urls import path
from django.urls import include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("checkout", views.checkout, name="checkout"),
    path("login/", views.login, name="login"),
    path('userprofile/<str:username>', views.userprofile, name='userprofile'),
    path('listing/<int:listing_id>', views.listing, name='listing'),
    path('add_to_cart/<int:listing_id>', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:item_id>', views.remove_from_cart, name='remove_from_cart')
]