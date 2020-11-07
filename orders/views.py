from django.shortcuts import render
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from decimal import Decimal
from django.contrib.auth import logout as django_logout

import requests

from . import forms
from . models import PizzaTopping, Category, MenuItem, Order, OrderItem


def index(request):
    return render(request, 'orders/index.html')


def home(request):
    args = {}

    if request.user.is_authenticated:
        customer = request.user
        try:
            cart = Order.objects.get(customer=customer, in_cart=True)
        except Order.DoesNotExist:
            cart = Order.objects.create(customer=request.user)

        args = {
            "items": cart.items.all().count()
        }

    return render(request, 'orders/home.html', args)


def verify_and_register(request):
    if request.method == "POST":
        data = {
            "phone_number": request.POST.get("phone_number", None),
            "security_code": request.POST.get("security_code", None),
            "session_token": request.POST.get("session_token", None)
        }

        url = 'http://127.0.0.1:8000/api/phone/verify'
        response = requests.post(url, data)
        print(response.json())
        print(response.status_code)

        if response.status_code == 200:
            return JsonResponse(response.json())

        else:
            return JsonResponse(response.json(), status=400)


def login(request):
    customer = request.user
    return render(request, 'login.html', {'customer': customer})


def logout(request):
    django_logout(request)
    return  HttpResponseRedirect('/menu')
    # return render(request, 'orders/index.html', {'message': 'Logged out.'})


def menu_view(request):
    categories = Category.objects.all()
    args = {
        'categories': categories
    }

    if request.user.is_authenticated:
        customer = request.user
        try:
            cart = Order.objects.get(customer=customer)
            args["items"] = cart.items.all().count()

        except Order.DoesNotExist:
            print("Order does not exists !!!")

    return render(request, 'orders/menu.html', args)


def location_view(request):
    return render(request, 'orders/location.html')


def about_view(request):
    return render(request, 'orders/about.html')


def contact_view(request):
    return render(request, 'orders/contact.html')


def get_pizza(request):
    try:
        if request.method == "GET":
            # print(request.GET)
            # toppingsForm = forms.PizzaToppingForm()
            # print(toppingsForm)
            toppings = PizzaTopping.objects.all()
            pizza = MenuItem.objects.get(id=request.GET["id"])
            args = {
                'pizza': pizza,
                'toppings': toppings,
                # 'toppingsForm': toppingsForm
            }
            
        return render(request, 'orders/modal.html', args)

    except Exception as err:
        print("Some error occured : ", err)


def update_total(order):
    if not isinstance(order, Order):
        raise Http404("{} is not an instance of Order.".format(order))
    else:     
        items = order.items.all()
        order.total = 0
        for item in items:
            order.total += item.price
            if item.toppings:
                for topping in item.toppings.all():
                    order.total += Decimal(60.00)

        order.save()


def add_item(request):
    print("User ", request.user)
    print("Data ", request.POST)
    if request.method == "GET":
        raise Http404

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Please Login first !!'},  status=403)

    if request.method == "POST":
        # print(request.POST)
        #? Get cart of current Customer 
        try:
            order = Order.objects.get(customer=request.user, in_cart=True)
        except Order.DoesNotExist:
            print("Creating new Order ... ")
            order = Order(customer=request.user) 
            order.save()

        #? Initializing a Order
        try:
            menuitem = MenuItem.objects.get(id=request.POST["id"])
        except MenuItem.DoesNotExist:
            raise Http404("Can't find price for added item .")
        else:
            if request.POST["size"] == 'Small':
                price = menuitem.sm_price
            elif request.POST["size"] == 'Medium':
                price = menuitem.md_price
            elif request.POST["size"] == 'Large':
                price = menuitem.lg_price
            else:
                return JsonResponse({'error': 'Please Select a Size'},  status=500)

            newitem = OrderItem(
                name=menuitem.name,
                description=menuitem.description,
                category=menuitem.category,
                price=price,
                size=request.POST["size"],
                order=order
            )
            newitem.save()
            update_total(order)

        print(request.POST.getlist('toppings[]'))
        # print(request.POST['toppings'])

        for topping_id in request.POST.getlist("toppings[]"):
            pizzatopping = PizzaTopping.objects.get(id=topping_id)
            newitem.toppings.add(pizzatopping)
            newitem.save()
            update_total(order)
            
    return HttpResponseRedirect(reverse('menu'))


def cart_view(request):
    try:
        order = Order.objects.get(customer=request.user)
        items = order.items.all()
        args = {
            'items': items,
            'order': order
        }
    
    except Order.DoesNotExist:
        print('Order Does not exists ')
        args = {}

    return render(request, 'orders/cart.html', args)


def remove_item_cart(request):
    try:
        order_id = request.POST["order_id"]
        item_id = request.POST["item_id"]

        order = Order.objects.get(id=order_id)
        item = order.items.all().get(id=item_id)

        print(item.id, item.name)

        item.delete()
        update_total(order)

        return JsonResponse({"success": "Removed Successfully"})

    except Exception as err:
        return JsonResponse({"error": err}, status="400")


def empty_cart(request, id):
    try:
        customer = request.user
        order = Order.objects.get(id=id, customer=customer).delete()
    except ProtectedError:
        raise Http404("Protected : cannnot be deleted !!")
    except Order.DoesNotExist:
        raise Http404("Order Does not Exists !! ")

    return HttpResponseRedirect(reverse('cart-view'))


def place_order(request):
    customer = request.user 
    try:
        order = Order.objects.get(customer=request.user, in_cart=True)
    except Order.DoesNotExist:
        raise Http404("Order does not exists !!! ")
    else:
        order.placed=True
        order.in_cart=False
        order.save()

    return render(request, 'orders/thanks.html')
