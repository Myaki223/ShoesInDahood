from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from base.forms import DeliveryAddressForm
from .models import Category, CompletedOrder, Customer, DeliveryAddress, Product, ShoppingCart
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
# Create your views here.

@login_required
def adminpanel(request):
    if not request.user.is_superuser:
        messages.error(request, 'You are not authorized to access this page', extra_tags='adminError')
        return redirect('index')
    
    users = User.objects.select_related('customer').filter(is_superuser=False)
    products = Product.objects.all()
    shopping_carts = ShoppingCart.objects.select_related('user', 'cart_item', 'user__customer').all()
    
    total_spent = Customer.objects.aggregate(total=Sum('total_spent')).get('total', 0)
    total_users = users.count()
    
    context = {
        'users': users,
        'products': products,
        'total_spent': total_spent,
        'total_users': total_users,
        'shopping_carts': shopping_carts,
    }
    
    return render(request, 'admin.html', context)




def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.name = request.POST.get('product_name')
        product.quantity = request.POST.get('product_quantity')
        product.price = request.POST.get('product_price')
        product.description = request.POST.get('product_description')
        if request.POST.get('update_image'):
          product.image = request.FILES.get('image')
        product.save()
        return redirect('admin')

    else:
        context = {'product': product}
        return render(request, 'edit_product.html', context)
      

def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('product_name')
        quantity = request.POST.get('product_quantity')
        price = request.POST.get('product_price')
        description = request.POST.get('product_description')
        image = request.FILES.get('image')
        category_cid = request.POST.get('category')  # Assuming you have a select field in your form for category

        # Retrieve the category object based on the selected category_id
        category = Category.objects.get(cid=category_cid)

        new_product = Product.objects.create(
            name=name,
            quantity=quantity,
            price=price,
            description=description,
            image=image,
            category=category,
        )
        
        new_product.save()
        return redirect('admin')
    else:
        categories = Category.objects.all()
        return render(request, 'add_product.html', {'categories': categories})


@login_required
def profile(request):
    user = request.user
    customer = Customer.objects.get(user=user)
    
    # Fetch all addresses for the customer
    addresses = DeliveryAddress.objects.filter(customer=customer)
    
    # Handle the address form
    if request.method == "POST":
        form = DeliveryAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.customer = customer
            address.save()
            return redirect('profile')  # Redirect to clear the form
    else:
        form = DeliveryAddressForm()

    # Fetch shopping cart items
    shopping_cart_items = ShoppingCart.objects.filter(user=user)

    context = {
        'shopping_cart_items': shopping_cart_items,
        'addresses': addresses,
        'form': form,
        'user_name': user.username,
    }
    return render(request, 'profile.html', context)

@login_required
def set_default_address(request, address_id):
    # Assuming the Address model uses a customer field, not user
    address = get_object_or_404(DeliveryAddress, id=address_id, customer__user=request.user)

    # Reset all addresses to not be default
    DeliveryAddress.objects.filter(customer__user=request.user).update(is_default=False)

    # Set the selected address as default
    address.is_default = True
    address.save()

    return redirect('profile')  # Redirect back to the profile page

# @login_required
# def MyCart(request):
#     user = request.user
#     shopping_cart_items = ShoppingCart.objects.filter(user=user)
#     completed_orders = CompletedOrder.objects.filter(user=user)

#     context = {
#         'shopping_cart_items': shopping_cart_items,
#         'completed_orders': completed_orders,
#         'user_name': user.username,
#     }
#     return render(request, 'mycart.html', context)


# @login_required
# def complete_order(request, shopping_cart_id):
#     shopping_cart = get_object_or_404(ShoppingCart, id=shopping_cart_id, user=request.user)

#     # Mark the shopping cart as completed
#     shopping_cart.cart_status = 3
#     shopping_cart.save()

#     # Create a new completed order
#     completed_order = CompletedOrder.objects.create(user=request.user, total_amount=shopping_cart.cart_item_total)
#     completed_order.cart_items.add(shopping_cart)

#     # Remove items from the shopping cart
#     shopping_cart.delete()

#     return redirect('my_cart')  # or redirect to any other page



# @login_required
# def update_cart_status(request, shopping_cart_id):
#     shopping_cart = get_object_or_404(ShoppingCart, id=shopping_cart_id)

#     if shopping_cart.user == request.user or request.user.is_superuser:
#         shopping_cart.cart_status = 3
#         shopping_cart.save()

#         customer = Customer.objects.get(user=shopping_cart.user)
#         customer.total_spent += shopping_cart.cart_item_total
#         customer.save()

#         # Decrease the quantity of the product
#         product = shopping_cart.cart_item
#         product.quantity -= shopping_cart.cart_item_quantity
#         product.save()

#         return redirect('admin')
#     else:
#         return JsonResponse({'error': 'You are not authorized to update this cart status.'}, status=403)






# @login_required
# def buy(request, shopping_cart_id):
#     shopping_cart_item = get_object_or_404(ShoppingCart, id=shopping_cart_id, user=request.user)
#     product = shopping_cart_item.cart_item
#     shopping_cart_item.cart_status = 2
#     shopping_cart_item.save()

#     return redirect('profile')

# @login_required
# def cancel(request, shopping_cart_id):
#     shopping_cart_item = get_object_or_404(ShoppingCart, id=shopping_cart_id, user=request.user)
#     product = shopping_cart_item.cart_item
#     shopping_cart_item.delete()

#     return redirect('profile')


def user_logout(request):
    logout(request)
    messages.success(request, 'logout', extra_tags='loggedOut')
    return redirect('index')

def form(request):
  return render(request, 'form.html')

def home(request):
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'index.html', context)

def signin(request):
  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
      if not user.is_superuser:
          login(request, user)
          return redirect('profile')
      else:
          login(request, user)
          return redirect('admin')
    else:
      messages.error(request, "Invalid username or password. Please try again.", extra_tags='login_error')
      return redirect('login')
  return render(request, 'login.html')

def reciept(request):
  return render(request, 'reciept.html')

def register(request):
  if request.method == "POST":
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    first_name = request.POST.get('firstName')
    last_name = request.POST.get('lastName')
    location = request.POST.get('location')
    phone_number = request.POST.get('phoneNumber')

    new_user = User.objects.create_user(username=username, password=password, email=email)
    new_user.first_name = first_name
    new_user.last_name = last_name
    new_user.save()

    new_customer = Customer(user=new_user)
    new_customer.location = location
    new_customer.phone_number = phone_number
    new_customer.save()
    return redirect ('index')
  else:
    return render(request, 'register.html')

def shop(request):
    categories = Category.objects.prefetch_related('product_set')  # Fetch all categories with their associated products

    context = {
        "categories": categories,
    }
    return render(request, 'shop.html', context)
# @login_required
# def add_to_cart(request):
#     if request.method == 'POST':
#         product_id = request.POST.get('product_id')
#         quantity = int(request.POST.get('itemQuantity'))
#         product = get_object_or_404(Product, pk=product_id)

#         if quantity <= product.quantity:
#             user = request.user
#             cart_item = ShoppingCart.objects.create(user=user, cart_item=product, cart_item_quantity=quantity)
#             cart_item.save()
#             return redirect('profile')
#         else:
#             messages.error(request, 'Total quantity input exceeds the in-stock quantity, please check the in stock quantity and try again.', extra_tags='qtyError')
#             return redirect('shop')  # Redirect to an appropriate URL or show an error message
#     else:
#         return redirect('shop')
    

def utilities_animation(request):
    return render(request, 'utilities_animation.html')

def item_item(request):
    products = Product.objects.all()
    context = { 'products' : products }
    return render(request, 'product.html', context)

def user_user(request):
    users = User.objects.select_related('customer').filter(is_superuser=False)
    products = Product.objects.all()
    # shopping_carts = ShoppingCart.objects.select_related('user', 'cart_item', 'user__customer').all()
    
    total_spent = Customer.objects.aggregate(total=Sum('total_spent')).get('total', 0)
    total_users = users.count()
    
    context = {
        'users': users,
        'products': products,
        'total_spent': total_spent,
        'total_users': total_users,
        # 'shopping_carts': shopping_carts,
    }
    return render(request, 'users.html', context)