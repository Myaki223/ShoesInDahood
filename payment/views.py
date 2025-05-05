from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentsForm
from payment.models import CompletedOrder, ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from base.models import Product, Profile
import datetime
from django.urls import reverse

from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid





# Create your views here.
def orders (request, pk): 
    if request.user.is_authenticated and request.user.is_superuser:
        order = Order.objects.get(id=pk)
        items = OrderItem.objects.filter(order=pk)
        
        if request.POST:
            status = request.POST['shipping_status']
            if status == "true":
                order = Order.objects.filter(id=pk)
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped= now)
            else:
                order = Order.objects.filter(id=pk)
                order.update(shipped=False)
            messages.success(request, "Shipping Status Updated")
            return redirect('admin')
                
        return render(request, "payment/orders.html", {"order":order, "items":items})
    else:
        messages.success(request, "Access Denied")
        return redirect('index')

def completed_dash(request): 
    if request.user.is_authenticated and request.user.is_superuser:
        completed_orders = CompletedOrder.objects.select_related('order', 'user', 'profile').all()

        return render(request, "payment/completed.html", {"completed_orders": completed_orders})
    else:
        messages.error(request, "Access Denied")
        return redirect('index')
    
def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        
        if request.method == "POST":
            # If marking the order as completed
            if 'complete_order' in request.POST:
                order_id = request.POST.get('num')
                order = Order.objects.filter(id=order_id).first()

                # Check if the order exists and is shipped and paid
                if order and order.shipped and order.paid:
                    # Create CompletedOrder entry
                    profile = Profile.objects.filter(user=order.user).first()
                    shipping_address = order.user.shippingaddress_set.filter(is_default=True).first()
                    CompletedOrder.objects.create(
                        order=order,
                        user=order.user,
                        profile=profile,
                        shipping_address=shipping_address,
                    )
                    messages.success(request, "Order has been marked as completed!")
                    return redirect('admin')
            
            # If unmarking an order as shipped
            elif 'shipping_status' in request.POST:
                order_id = request.POST.get('num')
                order = Order.objects.filter(id=order_id)
                now = datetime.datetime.now()
                order.update(shipped=False, date_shipped=None)
                messages.success(request, "Shipping status updated!")
                return redirect('admin')

        return render(request, "payment/shipped_dash.html", {"orders": orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('index')



def not_shipped_dash (request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id=num)
            now = datetime.datetime.now()
            order.update(shipped=True, date_shipped= now)
           
            messages.success(request, "Shipping Status Updated")
            return redirect('admin')
        return render(request, "payment/not_shipped_dash.html", {"orders":orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('index')


def completed_dash_profile(request):
    if request.user.is_authenticated:
        # Get completed orders for the logged-in user
        completed_orders = CompletedOrder.objects.filter(user=request.user).select_related('order', 'user', 'profile')
        
        return render(request, "payment/completed_profile.html", {"completed_orders": completed_orders})
    else:
        messages.error(request, "Access Denied")
        return redirect('index')

    
def shipped_dash_profile(request):
    if request.user.is_authenticated:
        # Get orders that are shipped and belong to the logged-in user
        orders = Order.objects.filter(user=request.user, shipped=True)
        
        if request.method == "POST":
            # If marking the order as completed
            if 'complete_order' in request.POST:
                order_id = request.POST.get('num')
                order = Order.objects.filter(id=order_id, user=request.user).first()

                # Check if the order exists, is shipped, and is paid
                if order and order.shipped and order.paid:
                    # Create CompletedOrder entry
                    profile = Profile.objects.filter(user=order.user).first()
                    shipping_address = order.user.shippingaddress_set.filter(is_default=True).first()
                    CompletedOrder.objects.create(
                        order=order,
                        user=order.user,
                        profile=profile,
                        shipping_address=shipping_address,
                    )
                    messages.success(request, "Order has been marked as completed!")
                    return redirect('index')
            
            # If unmarking an order as shipped
            elif 'shipping_status' in request.POST:
                order_id = request.POST.get('num')
                order = Order.objects.filter(id=order_id, user=request.user)
                now = datetime.datetime.now()
                order.update(shipped=False, date_shipped=None)
                messages.success(request, "Shipping status updated!")
                return redirect('index')

        return render(request, "payment/shipped_dash_profile.html", {"orders": orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('index')




def not_shipped_dash_profile(request):
    if request.user.is_authenticated:
        # Get orders that are not shipped and belong to the logged-in user
        orders = Order.objects.filter(user=request.user, shipped=False)
        
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id=num, user=request.user)
            now = datetime.datetime.now()
            order.update(shipped=True, date_shipped=now)
           
            messages.success(request, "Shipping Status Updated")
            return redirect('index')
        
        return render(request, "payment/not_shipped_dash_profile.html", {"orders": orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('index')



def process_order (request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        payment_form = PaymentsForm(request.POST or None)
        my_shipping = request.session.get('my_shipping')
        full_name = my_shipping['shipping_full_name']
        email =  my_shipping['shipping_email']

        shipping_address =f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}\n"
        amount_paid = totals
        
        if request.user.is_authenticated:
            user=request.user
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            order_id = create_order.pk
            for product in cart_products():
                product_id = product.id
                price = product.price
                
                for key,value in quantities().items():
                    if int(key) == product.id:
                        create_order_item = OrderItem(order_id= order_id, product_id=product_id , user = user, quantity=value, price=price)
                        create_order_item.save()
            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]
                    
                    
            current_user = Profile.objects.filter(user__id=request.user.id)
            current_user.update(old_cart="")

            messages.success(request, "Order Placed")
            return redirect('index')
        else:
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

    else:
        messages.success(request, "Access Denied")
        return redirect('index')
    
def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    shipping_form = ShippingForm(request.POST or None)

    if request.user.is_authenticated:
        default_address = ShippingAddress.objects.filter(user=request.user, is_default=True).first()

        if default_address and not request.POST:
            shipping_form = ShippingForm(initial={
                'shipping_full_name': default_address.shipping_full_name,
                'shipping_email': default_address.shipping_email,
                'shipping_address1': default_address.shipping_address1,
                'shipping_address2': default_address.shipping_address2,
                'shipping_city': default_address.shipping_city,
                'shipping_state': default_address.shipping_state,
                'shipping_zipcode': default_address.shipping_zipcode,
                'shipping_country': default_address.shipping_country,
                'phone_number': default_address.phone_number,
            })

    return render(request, "payment/checkout.html", {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "shipping_form": shipping_form,
    })


def billing_info (request):
    if request.POST:

        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping
        my_shipping = request.session.get('my_shipping')
        full_name = my_shipping['shipping_full_name']
        email =  my_shipping['shipping_email']

        shipping_address =f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}\n"
        amount_paid = totals
        
        host = request.get_host()
        my_Invoice = str(uuid.uuid4())
        
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': totals,
            'item_name': 'Shoe Order',
            'no_shipping': '2',
            'invoice': my_Invoice,
            'currency_code': 'PHP',
            'notify_url': 'https://{}{}'.format(host, reverse("paypal-ipn")),
            'return_url': 'https://{}{}'.format(host, reverse("payment_success")),
            'cancel_return': 'https://{}{}'.format(host, reverse("payment_failed")),
            
            
        }
        
        paypal_form = PayPalPaymentsForm(initial=paypal_dict)

        if request.user.is_authenticated:
            billing_form = PaymentsForm()
            user=request.user
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid, invoice=my_Invoice)
            create_order.save()

            order_id = create_order.pk
            for product in cart_products():
                product_id = product.id
                price = product.price
                
                for key,value in quantities().items():
                    if int(key) == product.id:
                        create_order_item = OrderItem(order_id= order_id, product_id=product_id , user = user, quantity=value, price=price)
                        create_order_item.save()

                    
            current_user = Profile.objects.filter(user__id=request.user.id)
            current_user.update(old_cart="")
            
            return render(request, "payment/billing_info.html", {"paypal_form":paypal_form,"cart_products":cart_products, "quantities":quantities,"totals":totals, "shipping_info":request.POST, "billing_form":billing_form})

        else:
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()
            
            return render(request, "payment/billing_info.html", {"paypal_form":paypal_form,"cart_products":cart_products, "quantities":quantities,"totals":totals, "shipping_info":request.POST, "billing_form":billing_form})
    
    else:
        messages.success(request, "Access Denied")
        return redirect('index')
    


def payment_success (request):
    return render(request, "payment/payment_success.html", {})


def payment_failed (request):
    return render(request, "payment/payment_failed.html", {})