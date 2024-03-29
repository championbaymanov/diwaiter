from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

from src.base.models import BaseModel, BaseEnum
from src.restaurants.models import RestaurantModel

PAYMENT_METHODS = [
    ('Cash', 'Cash'),
    ('Card', 'Card')
]


class GenderChoice(BaseEnum):
    MALE = "Male"
    FEMALE = "Female"


class PermissionsChoice(BaseEnum):
    ADMIN = 1
    MANAGER = 2
    USER = 3


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if email is None:
            raise TypeError("Users must have a email.")

        if password is None:
            raise TypeError("Both password fields must be filled")
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class UserModel(BaseModel, AbstractBaseUser, PermissionsMixin):
    username: str = models.CharField(db_index=True, max_length=255, db_column="username")
    email: str = models.EmailField(db_index=True, unique=True, db_column="email")
    is_active: bool = models.BooleanField(default=True, db_column="is_active")
    is_superuser: bool = models.BooleanField(default=False, db_column="is_superuser")
    is_staff: bool = models.BooleanField(default=False, db_column="is_staff")
    groups = None
    user_permissions = None
    USERNAME_FIELD: str = 'email'
    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f'ID: {self.pk}, username: {self.username}'


class JwtModel(BaseModel):
    user: UserModel = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name="jwt", db_column="user")
    access: str = models.TextField(db_column="access")
    refresh: str = models.TextField(db_column="refresh")

    class Meta:
        db_table = "jwt"
        verbose_name = "Jwt"
        verbose_name_plural = "Jwt"

    def __str__(self):
        return "Model: %s username: %s id: %s" % (self.__class__.__name__, self.user.username, self.pk)


class WaiterModel(BaseModel):
    restaurant = models.ForeignKey(RestaurantModel, on_delete=models.CASCADE, related_name='waiters')
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='waiter', null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    def update_average_rating(self):
        average_rating = WaiterRating.objects.filter(waiter=self).aggregate(Avg('rating'))['rating__avg']
        if average_rating is not None:
            self.average_rating = round(average_rating, 2)
        else:
            self.average_rating = 0

    def save(self, *args, **kwargs):
        # self.update_average_rating()
        # print(self)
        super().save(*args, **kwargs)
        

    class Meta:
        db_table = "waiters"
        verbose_name = "Waiter"
        verbose_name_plural = "Waiters"
