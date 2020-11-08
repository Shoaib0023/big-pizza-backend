from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.IntegerField(blank=False)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.phone}'


class PizzaTopping(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.name}'


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.name}'


class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    image = models.FileField(upload_to="images/menu", blank=True)
    name = models.CharField(max_length=30, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    sm_price = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    md_price = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    lg_price = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sm_available = models.BooleanField(default=True)
    md_available = models.BooleanField(default=True)
    lg_available = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.category} - {self.name}'


class Order(models.Model):
    customer = models.ForeignKey(
        User, 
        null=True, 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    timestamp = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    in_cart = models.BooleanField(default=True)
    placed = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f'Order #{self.id} by {self.customer.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        null=True, 
        related_name='items'
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    size = models.CharField(max_length=5, blank=True)
    toppings = models.ManyToManyField(
        PizzaTopping, 
        blank=True, 
        related_name='pizza'
    )
    extra = models.BooleanField(default=False)
    
    def __str__(self):
        if self.extra:
            return f'+ {self.name}'
        if self.toppings:
            return f'{self.category.name} / {self.size} {self.name}'
        else:
            return f'{self.category.name} / {self.size} {self.name}'



