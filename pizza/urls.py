from django.contrib import admin
from django.urls import path, include
from orders import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index, name="index"),
    path('verify_and_register/', views.verify_and_register, name="verify-and-register"),

    path('accounts/', include('allauth.urls')),
    path('api/', include('orders.urls')),
    path('menu/', views.menu_view, name="menu"),
    path('location/', views.location_view, name="location"),
    path('about/', views.about_view, name="about"),
    path('contact/', views.contact_view, name="contact"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('get-pizza/', views.get_pizza, name="get-pizza"),

    path('addItem/', views.add_item, name="add-item"),
    path('cart/', views.cart_view, name="cart-view"),
    path('removeItem/', views.remove_item_cart, name="remove-item"),

    path('emptyCart/<str:id>', views.empty_cart, name="empty-cart"),
    path('place-order/', views.place_order, name="place-order"),
    path('', views.home, name="home"),
]



# Username - admin123
# Password - Mshoaib@123