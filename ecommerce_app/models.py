from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

# ✅ Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, name, phone, password=None):
        if not phone:
            raise ValueError("Phone is required")
        user = self.model(name=name, phone=phone)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, phone, password=None):
        user = self.create_user(name, phone, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

# ✅ Custom User Model
class User(AbstractBaseUser):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None): return True
    def has_module_perms(self, app_label): return True
    @property
    def is_staff(self): return self.is_admin

# ✅ Product Model
class Product(models.Model):
    name = models.CharField(max_length=200)
    number = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='products/')
    quantity = models.IntegerField()
    production_cost = models.DecimalField(max_digits=10, decimal_places=2)  # new field
    price = models.DecimalField(max_digits=10, decimal_places=2)
    instock = models.PositiveIntegerField(default=0)  # NEW field for inventory tracking
    def __str__(self):
        return self.name


class PurchaseSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return f"Purchase on {self.created_at.strftime('%d-%m-%Y %I:%M %p')}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey(PurchaseSession, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    confirmed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # calculate total price before saving
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def get_profit(self):
        return (self.product.price - self.product.production_cost) * self.quantity

# models.py
