from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from django.urls import reverse
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib import messages


def register(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already taken")
                return redirect("register")
            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email already used ")
                return redirect(reverse("register"))

            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password
                )
                user.save()
                return redirect("login")
        else:
            messages.error(request, "Password does not  match")
            return redirect("register")
    else:
        context = {"cartItems": cartItems}
        return render(request, "store/authenticate.html", context)


def login(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("store")
        else:
            messages.info(request, "Invalid Credentials!")
            return redirect("login")
    else:
        context = {"cartItems": cartItems}
        return render(request, "store/authenticate.html", context)


def logout(request):
    auth.logout(request)
    return redirect("store")


def product_search(request):
    query = request.GET.get("q")
    data = cartData(request)
    cartItems = data["cartItems"]
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    context = {"products": products, "cartItems": cartItems}
    return render(request, "store/store.html", context)


def store(request):
    data = cartData(request)

    query = request.GET.get("q")
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems}
    return render(request, "store/store.html", context)


def cart(request):
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "store/cart.html", context)


@login_required(login_url=login)
def checkout(request):
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "store/checkout.html", context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]
    print("Action:", action)
    print("Product:", productId)

    customer = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == "add":
        orderItem.quantity = orderItem.quantity + 1
    elif action == "remove":
        orderItem.quantity = orderItem.quantity - 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data["form"]["total"])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data["shipping"]["address"],
            city=data["shipping"]["city"],
            state=data["shipping"]["state"],
            zipcode=data["shipping"]["zipcode"],
        )

    return JsonResponse("Payment submitted..", safe=False)
