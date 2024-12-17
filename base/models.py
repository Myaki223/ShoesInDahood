from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from django.contrib.auth.models import User
# Create your models here.


class Customer (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    total_spent = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username
    
class DeliveryAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="addresses")
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="Philippines")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.address_line1}, {self.city} ({'Default' if self.is_default else 'Secondary'})"

    def save(self, *args, **kwargs):
        # Ensure only one address is marked as default
        if self.is_default:
            DeliveryAddress.objects.filter(customer=self.customer, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    
class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="cat", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100, default="Shoes")
    image = models.ImageField(upload_to="category", default="category.jpg")

    class Meta:
        verbose_name_plural = "Categories"
    
    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50">' % (self.image.url))

    def __str__(self):
        return self.title

class Product(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    price = models.IntegerField(blank=True, default=0)
    description = models.CharField(max_length=250, blank=True, null=True)
    image = models.ImageField(upload_to='', max_length=100, blank=True, null=True)
    def __str__(self):
        return self.name

class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart_item = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart_status = models.IntegerField(default='1', blank=True)
    cart_item_quantity = models.IntegerField(blank=True, null=True)
    cart_item_total = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s shopping cart"

    def save(self, *args, **kwargs):
        # Calculate the total price for the item based on its quantity and price
        self.cart_item_total = self.cart_item_quantity * self.cart_item.price
        super().save(*args, **kwargs)

class CompletedOrder(models.Model):
    order_id = ShortUUIDField(unique=True, length=10, max_length=30, prefix="order", alphabet="abcdefgh12345")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart_items = models.ManyToManyField(ShoppingCart)
    total_amount = models.IntegerField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, default="PayPal")
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"
    

