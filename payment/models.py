from django.db import models
from django.contrib.auth.models import User
from base.models import Product
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
import datetime
from django.utils import timezone
from base.models import Profile

# Create your models here.

    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    shipping_address = models.TextField(max_length=15000)
    amount_paid = models.DecimalField(max_digits=7, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)
    
    invoice = models.CharField(max_length=250, null=True, blank=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f'Order - {str(self.id)}'


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    shipping_full_name = models.CharField(max_length=255)
    shipping_email = models.CharField(max_length=255)
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
    shipping_city = models.CharField(max_length=255)
    shipping_state = models.CharField(max_length=255, null=True, blank=True)
    shipping_zipcode = models.CharField(max_length=255, null=True, blank=True)
    shipping_country = models.CharField(max_length=255, default="Philippines")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Shipping Addresses"

    def __str__(self):
        default_status = "Default" if self.is_default else "Secondary"
        return f"{self.shipping_address1}, {self.shipping_city} ({default_status})"

    def save(self, *args, **kwargs):
        # Ensure only one address is marked as default per user
        if self.is_default and self.user:
            ShippingAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


    
@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance,**kwargs):
    if instance.pk:
        now = datetime.datetime.now()
        obj = sender._default_manager.get(pk=instance.pk)
        if instance.shipped and not obj.shipped:
            instance.date_shipped = now
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f'Order Item - {str(self.id)}'


class CompletedOrder(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='completed_order')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    
    completed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Completed Order #{self.order.id}"

    class Meta:
        verbose_name = "Completed Order"
        verbose_name_plural = "Completed Orders"

@receiver(post_save, sender=Order)
def create_completed_order(sender, instance, created, **kwargs):
    if instance.shipped and instance.paid:
        if not hasattr(instance, 'completed_order'):
            profile = Profile.objects.filter(user=instance.user).first()
            shipping_address = instance.user.shippingaddress_set.filter(is_default=True).first() if instance.user else None

            CompletedOrder.objects.create(
                order=instance,
                user=instance.user,
                profile=profile,
                shipping_address=shipping_address,
            )