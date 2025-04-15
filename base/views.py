from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import json
from base.forms import DeliveryAddressForm, UpdateUserForm, UserInfoForm
from .models import Category, Customer, DeliveryAddress, Product, Profile
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from cart.cart import Cart
from payment.forms import ShippingForm
from payment.models import ShippingAddress

# Create your views here.

@login_required
def adminpanel(request):
    if not request.user.is_superuser:
        messages.error(request, 'You are not authorized to access this page', extra_tags='adminError')
        return redirect('index')
    
    users = User.objects.select_related('customer').filter(is_superuser=False)
    products = Product.objects.all()
    
    total_spent = Customer.objects.aggregate(total=Sum('total_spent')).get('total', 0)
    total_users = users.count()
    
    context = {
        'users': users,
        'products': products,
        'total_spent': total_spent,
        'total_users': total_users,
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

    context = {
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
          current_user = Profile.objects.get(user__id=request.user.id)
          saved_cart = current_user.old_cart
          if saved_cart:
             converted_cart = json.loads(saved_cart)
             cart = Cart(request)
             for key,value in converted_cart.items():
                cart.db_add(product=key, quantity=value)
             
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
    return redirect ('update_info')
  else:
    return render(request, 'register.html')
  

def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request, "User has been updated!")
            return redirect('profile')

        return render(request, 'update_user.html', {'user_form': user_form})  # Fixed syntax error

    else:
        messages.error(request, "You must be logged in!")
        return redirect('index')
    
def update_info(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user=request.user)

        # Use filter().first() to safely get the shipping address
        shipping_user = ShippingAddress.objects.filter(user=request.user).first()

        # If no shipping address exists yet, you might want to create a blank one:
        if not shipping_user:
            shipping_user = ShippingAddress(user=request.user)

        form = UserInfoForm(request.POST or None, instance=current_user)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        if form.is_valid() or shipping_form.is_valid():
            form.save()
            shipping_form.save()
            messages.success(request, "Your info has been updated!")
            return redirect('profile')

        return render(request, 'update_info.html', {'form': form, 'shipping_form': shipping_form})

    else:
        messages.error(request, "You must be logged in!")
        return redirect('index')

def shop(request):
    categories = Category.objects.prefetch_related('product_set')  # Fetch all categories with their associated products

    context = {
        "categories": categories,
    }
    return render(request, 'shop.html', context)

    

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