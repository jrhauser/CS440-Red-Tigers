from django.urls import path
from django.urls import include, reverse
from . import views
from django.contrib.auth.views import LogoutView
from .views import LogoutViewAllowGet

urlpatterns = [
    path("", views.index, name="index"),
    path("checkout", views.checkout, name="checkout"),
    path("login/", views.login, name="login"),
    path('userprofile/<str:username>', views.userprofile, name='userprofile'),
    path('listing/<int:listing_id>', views.listing, name='listing'),
    path('listing/', views.all_listings, name='all_listings'),
    path('add_to_cart/<int:listing_id>', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:item_id>', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart_quantity/<int:item_id>', views.update_cart_quantity, name='update_cart_quantity'),
    path("createlisting", views.create_listing, name="createlisting"),
    path('edit_listing/<int:listing_id>', views.edit_listing, name='edit_listing'),
    path('delete_listing/<int:listing_id>', views.delete_listing, name='delete_listing'),
    path('logout/', LogoutViewAllowGet.as_view(next_page='index'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('process_purchase/', views.process_purchase, name='process_purchase'),
]