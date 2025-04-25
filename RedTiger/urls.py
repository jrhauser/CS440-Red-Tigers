from django.urls import path
from django.urls import include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("checkout", views.checkout, name="checkout"),
    path("login/", views.login, name="login"),
]