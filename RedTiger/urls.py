from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("checkout", views.checkout, name="checkout"),
    path("signin", views.signin, name="signin")
]