from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    # Leave as empty string for store url
    path("", views.store, name="store"),
    path("search/", views.product_search, name="product_search"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("update_item/", views.updateItem, name="update_item"),
    path("process_order/", views.processOrder, name="process_order"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout", views.logout, name="logout"),
]
