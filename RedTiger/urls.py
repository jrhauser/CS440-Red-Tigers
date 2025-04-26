from django.urls import path
from django.urls import include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("checkout", views.checkout, name="checkout"),
    path("login/", views.login, name="login"),
    path('userprofile/<str:username>', views.userprofile, name='userprofile'),
    path('listing/<int:listing_id>', views.listing, name='listing'),
    path('buy/<int:listing_id>/', views.buy, name='buy')
]