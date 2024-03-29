from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

from src.base.models import BaseModel, BaseEnum
# from src.users.models import WaiterModel

PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Card'),
    )


class Categories(BaseEnum):
    Main_meal = 'Main_meal'
    Salads = "Salads"
    Drinks = 'Drinks'
    Soups = "Soups"
    Desserts = 'Desserts'
    Paste = 'Paste'
    Sets = 'Sets'
    Second_courses = 'Second_courses'
    Pizza = 'Pizza'
    Burgers = 'Burgers'


class RestaurantModel(BaseModel):
    title = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to="restaurant/image/")
    owner = models.OneToOneField(
        "users.UserModel", on_delete=models.CASCADE, related_name='restaurant', blank=True, null=True
    )

    class Meta:
        db_table = 'restaurant'
        verbose_name = 'Restaurant'
        verbose_name_plural = 'Restaurants'

    def __str__(self):
        return self.title


class Dish(models.Model):
    title = models.CharField(max_length=16)
    image = models.ImageField()
    price = models.CharField(max_length=16)
    categories = models.CharField(max_length=16, choices=Categories.get_choice(), default='Main_meal')
    description = models.CharField(max_length=255, null=True)
    restaurant = models.ForeignKey(RestaurantModel, on_delete=models.CASCADE, related_name='dishes')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class FavoriteRestaurant(models.Model):
    user = models.ForeignKey('users.UserModel', on_delete=models.CASCADE, related_name="favorites")
    restaurant = models.ForeignKey(RestaurantModel, on_delete=models.CASCADE, related_name='favorites')

    def __str__(self):
        return f"{self.user} favorite {self.restaurant.name}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('users.UserModel', on_delete=models.CASCADE, null=True, blank=True)
    table_number = models.PositiveIntegerField()
    restaurant = models.ForeignKey(RestaurantModel, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cash')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_accepted = models.BooleanField(default=False)
    is_end = models.BooleanField(default=False)
    waiter = models.ForeignKey("users.WaiterModel", on_delete=models.SET_NULL, null=True, blank=True)
    is_check = models.BooleanField(default=False)

    def calculate_total_amount(self):
        items = self.order_items.all()
        total = sum([(int(item.quantity) * int(item.dish.price)) for item in items])
        self.total_amount = total
        self.save()

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey('Order', related_name='order_items', on_delete=models.CASCADE)
    dish = models.ForeignKey('Dish', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"Order Item #{self.pk}"



class WaiterComment(models.Model):
    user = models.ForeignKey('users.UserModel', on_delete=models.SET_NULL, related_name='waiter_comment', null=True, blank=True)
    waiter = models.ForeignKey("users.WaiterModel", on_delete=models.SET_NULL, related_name='waiter_comment', null=True, blank=True)
    text = models.TextField()
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, related_name='waiter_comment', null=True, blank=True)
    restaurant = models.ForeignKey(RestaurantModel, on_delete=models.SET_NULL, related_name='waiter_comment', null=True, blank=True)

    def __str__(self):
        return self.text


class WaiterRating(models.Model):
    user = models.ForeignKey('users.UserModel', on_delete=models.SET_NULL, related_name='waiter_rating', null=True, blank=True)
    waiter = models.ForeignKey("users.WaiterModel", on_delete=models.SET_NULL, related_name='waiter_rating', null=True, blank=True)
    rating = models.PositiveIntegerField()

    def __str__(self):
        return str(self.rating)


class OrderComment(models.Model):
    user = models.ForeignKey('users.UserModel', on_delete=models.SET_NULL, null=True, related_name='order_comment')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, related_name='order_comment', null=True)
    text = models.TextField()
    restaurant = models.ForeignKey(RestaurantModel, on_delete=models.SET_NULL, related_name='order_comment', null=True, blank=True)

    def __str__(self):
        return self.text
