from django.urls import path, include
from . import views


	
urlpatterns = [
    path('payment_success', views.payment_success, name="payment_success"),
    path('payment_failed', views.payment_failed, name="payment_failed"),
    path('checkout', views.checkout, name="checkout"),
    path('billing_info', views.billing_info, name="billing_info"),
    path('process_order', views.process_order, name="process_order"),
    path('shipped_dash', views.shipped_dash, name="shipped_dash"),
    path('completed_dash', views.completed_dash, name="completed_dash"),
    path('not_shipped_dash', views.not_shipped_dash, name="not_shipped_dash"),
    path('orders/<int:pk>', views.orders, name="orders"),
    path('paypal', include("paypal.standard.ipn.urls")),
    path('shipped_dash_profile', views.shipped_dash_profile, name="shipped_dash_profile"),
    path('completed_dash_profile', views.completed_dash_profile, name="completed_dash_profile"),
    path('not_shipped_dash_profile', views.not_shipped_dash_profile, name="not_shipped_dash_profile"),
    

]

 