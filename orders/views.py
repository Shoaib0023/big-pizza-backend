from django.shortcuts import render
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from decimal import Decimal
from django.contrib.auth import logout as django_logout

from django.contrib.auth import login as django_login
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from allauth.socialaccount.models import SocialAccount

from django.contrib.auth.decorators import login_required

import requests

from . import forms
from . models import PizzaTopping, Category, MenuItem, Order, OrderItem, UserProfile


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
        # data = {
        #     "phone_number": request.POST.get("phone_number", None),
        #     "security_code": request.POST.get("security_code", None),
        #     "session_token": request.POST.get("session_token", None)
        # }
        phone_number = request.POST.get("phone_number", None)
        session_token = request.POST.get("session_token", None)
        security_code = request.POST.get("security_code", None)

        print(phone_number, session_token, security_code)

        url = f'https://2factor.in/API/V1/ed4bd15d-180d-11eb-b380-0200cd936042/SMS/VERIFY/{session_token}/{security_code}'
        response = requests.get(url)
        print("Response : ", response.json())
        print("Response Status : ", response.status_code)

        if response.status_code == 200:
            if User.objects.filter(username=phone_number).exists():
                user = User.objects.get(username=phone_number)
                if user is not None:
                    print("User already exists !")
                    django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    print(request.user.is_authenticated)
                    return JsonResponse({"success": "Successfully Logged in"}, status=200)
                else:
                    print("Not authenticated !!")

            else:
                print("Creating new user !!")
                user = User.objects.create(
                            username=phone_number,
                            password="abcd@786"
                        )

                userProfile = UserProfile.objects.create(
                            user=user, 
                            phone=phone_number, 
                            is_phone_verified=True
                        )

                django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                print("IS USER AUTHENTICATED : ",request.user.is_authenticated)
                return JsonResponse({"success": "Successfully Logged in"}, status=201)

        else:
            return JsonResponse(response.json(), status=400)


def login(request):
    customer = request.user
    return render(request, 'login.html', {'customer': customer})


def logout(request):
    django_logout(request)
    return  HttpResponseRedirect('/menu')


def menu_view(request):
    categories = Category.objects.all()
    args = {
        'categories': categories
    }

    if request.user.is_authenticated:
        customer = request.user

        try:
            cart = Order.objects.get(customer=customer, in_cart=True)
            args["items"] = cart.items.all().count()

        except Order.DoesNotExist:
            print("Order does not exists !!!")

        except Order.MultipleObjectsReturned:
            cart = Order.objects.filter(customer=customer)[0]
            args["items"] = cart.items.all().count()

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

        # print(request.POST.getlist('toppings[]'))

        for topping_id in request.POST.getlist("toppings[]"):
            pizzatopping = PizzaTopping.objects.get(id=topping_id)
            newitem.toppings.add(pizzatopping)
            newitem.save()
            update_total(order)
            
    return HttpResponseRedirect(reverse('menu'))


@login_required(login_url='/login')
def cart_view(request):
    try:
        order = Order.objects.get(customer=request.user, in_cart=True)
        items = order.items.all()
        args = {
            'items': items,
            'order': order
        }
    
    except Order.DoesNotExist:
        print('Order Does not exists ')
        args = {}

    except Order.MultipleObjectsReturned:
        print("Multiple cart found")
        cart = Order.objects.filter(customer=request.user)[0]
        args = {}


    return render(request, 'orders/cart.html', args)


@login_required(login_url='/login')
def my_orders(request):
    customer = request.user
    orders = Order.objects.filter(customer=customer, placed=True)
    args = {
        'orders': orders
    }
    return render(request, 'orders/myorders.html', args)



def remove_item_cart(request):
    try:
        order_id = request.POST["order_id"]
        item_id = request.POST["item_id"]

        order = Order.objects.get(id=order_id)
        item = order.items.all().get(id=item_id)

        # print(item.id, item.name)
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


def checkout(request):
    return render(request, 'orders/checkout.html')


def toggle_place_order(request):
    try:
        customer = request.user
        profile = UserProfile.objects.get(user=customer)

    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=customer)

    if SocialAccount.objects.filter(user=customer).exists():
            socialaccount = SocialAccount.objects.get(user=customer)
            profile.is_email_verified = True
            profile.save()

    order_id = request.POST['order_id']

    args = {
        'address': profile.address,
        'phone': profile.phone,
        'is_phone_verified': profile.is_phone_verified,
        'is_email_verified': profile.is_email_verified,
        'email': customer.email,
        'firstname': customer.first_name,
        'lastname': customer.last_name,
        'order_id': order_id
    }

    return render(request, 'orders/place-order-modal.html', args)


def place_order(request):
    customer = request.user
    # print(request.user, request.user.id)
    # print(profile)
    profile = UserProfile.objects.get(user=customer)
    
    if not profile.address:
        profile.address = request.POST.get('address', '')
    
    if not profile.phone:
        profile.phone = request.POST.get('phone', '')

    if not customer.email:
        customer.email = request.POST.get('email', '')

    if not customer.first_name:
        customer.first_name = request.POST.get('firstname', '')

    if not customer.last_name:
        customer.last_name = request.POST.get('lastname', '')

    profile.save()
    customer.save()

    order_id = request.POST['order_id']
    order = Order.objects.get(id=order_id)
    order.placed = True
    order.in_cart = False
    order.save()
    return JsonResponse({"success": "Order is Placed !"})


def thanks(request):
    customer = request.user
    args = {
        'user': customer 
    }
    return render(request, 'orders/thanks.html', args)




