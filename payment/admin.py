from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem, CompletedOrder
from django.contrib.auth.models import User
# Register your models here.

admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)

class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["date_ordered"]
    fields = ["user", "full_name", "email", "shipping_address", "amount_paid", "date_ordered","shipped","date_shipped", "invoice","paid"]
    inlines = [OrderItemInline]
    
    
class CompletedOrderAdmin(admin.ModelAdmin):
    list_display = ("order", "user", "completed_at")
    list_filter = ("completed_at",)
    search_fields = ("user__email", "order__invoice")




admin.site.unregister(Order)

admin.site.register(Order, OrderAdmin)

admin.site.register(CompletedOrder, CompletedOrderAdmin)