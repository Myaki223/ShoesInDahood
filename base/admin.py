from django.contrib import admin
from .models import Customer, Product, ShoppingCart, Category
# Register your models here.
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(ShoppingCart)
admin.site.register(Category)
