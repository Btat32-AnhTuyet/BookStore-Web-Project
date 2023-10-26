from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from.models import *
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .paypal import get_paypal_client
from paypalcheckoutsdk.orders import OrdersCreateRequest
import requests

#Create your views here.
def detail(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer =customer, complete =False)
        items = order.orderitem_set.all()
        cartItems= order.get_cart_items
        user_not_login = "hidden;"
        user_login = "visible;"
    else:
        items =[]
        order ={'get_cart_items':0, 'get_cart_total' :0}
        cartItems= order['get_cart_items']
        user_not_login = "visible;"
        user_login = "hidden;"
    id = request.GET.get('id', '')
    product_s = Product.objects.filter(id=id)    
    categories = Category.objects.filter(is_sub = False)
    active_category = request.GET.get('category', '')
    context={'categories': categories,'product_s':product_s , 'active_category': active_category ,'items':items, 'order':order,'cartItems' :cartItems, 'user_not_login': user_not_login, 'user_login': user_login}
    return render(request, 'app/detail.html', context)

def category(request):
    categories = Category.objects.filter(is_sub = False)
    active_category = request.GET.get('category', '')
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer =customer, complete =False)
        items = order.orderitem_set.all()
        cartItems= order.get_cart_items
    else:
        items =[]
        order ={'get_cart_items':0, 'get_cart_total' :0}
        cartItems= order['get_cart_items']
    if active_category:
        products = Product.objects.filter(category__slug= active_category)
    context = {'categories': categories, 'products': products, 'active_category': active_category, 'items':items, 'order':order,'cartItems' :cartItems}
    return render(request, 'app/category.html', context)

def register(request):
    if request.user.is_authenticated:
        user_not_login = "hidden;"
        user_login = "visible;"
    else:
        user_not_login = "visible;"
        user_login = "hidden;"
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    context = {'form': form, 'user_not_login': user_not_login, 'user_login': user_login}
    return render(request, 'app/register.html', context)

def search(request):
    if request.method == "POST":
        searched = request.POST["searched"]
        keys = Product.objects.filter(name__contains = searched)
    
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden;"
        user_login = "visible;"
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
        user_not_login = "visible;"
        user_login = "hidden;"
    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category', '')
    products = Product.objects.all()

    context = {
        'categories': categories,
        'active_category': active_category,
        "searched": searched,
        "keys": keys,
        'products': products,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login
    }
    
    return render(request, 'app/search.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        user_not_login = "hidden;"
        user_login = "visible;"
        return redirect('home')
    else:
        user_not_login = "visible;"
        user_login = "hidden;"
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or password is incorrect!')
    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category', '')
    products = Product.objects.all()
    context = {'user_not_login': user_not_login, 'user_login': user_login,'categories': categories, 'active_category': active_category, 'products': products}
    return render(request, 'app/login.html', context)

@login_required
def profile(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items  # Đảm bảo rằng phương thức này tồn tại và trả về số lượng mong muốn
        context = {'items': items, 'order': order, 'cartItems': cartItems}
        return render(request, 'app/profile.html', context)
    else:
        return redirect('login')

@login_required
def editprofile(request):
    user = request.user
    order, created = Order.objects.get_or_create(customer=user, complete=False)
    items = order.orderitem_set.all()
    cartItems = order.get_cart_items
    context = {'items':items, 'order':order,'cartItems' :cartItems}
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        # Cập nhật thông tin người dùng
        user = request.user
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        # Hiển thị thông báo cho người dùng và chuyển hướng về trang hồ sơ
        messages.success(request, 'Thông tin cá nhân đã được cập nhật thành công!')
        return redirect('profile')
    else:
        return render(request, 'app/editprofile.html', context)

def logoutPage(request):
    logout(request)
    return redirect('login')

def home(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer =customer, complete =False)
        items = order.orderitem_set.all()
        cartItems= order.get_cart_items
        user_not_login = "hidden;"
        user_login = "visible;"
    else:
        items =[]
        order ={'get_cart_items':0, 'get_cart_total' :0}
        cartItems= order['get_cart_items']
        user_not_login = "visible;"
        user_login = "hidden;"
    categories = Category.objects.filter(is_sub = False)
    active_category = request.GET.get('category', '')
    products = Product.objects.all()
    context={'products': products, 'cartItems' :cartItems, 'user_not_login': user_not_login, 'user_login': user_login, 'categories':categories, 'active_category':active_category}
    # context={'products': products, 'cartItems' :cartItems, 'user_not_login': user_not_login, 'user_login': user_login, 'categories':categories}

    return render(request, 'app/home.html', context)

def cart(request):
    current_path = request.path
    on_auth_page = current_path in ['/login', '/register']
    
    # Initialize default values
    items = []
    order = {'get_cart_items': 0, 'get_cart_total': 0}
    cartItems = 0
    user_not_login = "visible;"
    user_login = "hidden;"
    
    # For authenticated users
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        
        # I'm assuming get_cart_items and get_cart_total are either properties or methods of the Order model.
        cartItems = order.get_cart_items  
        user_not_login = "hidden;"
        user_login = "visible;"
    
    # For authentication pages
    elif on_auth_page:
        user_not_login = "hidden;"
        user_login = "hidden;"
    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category', '')
    
    context = {
        'categories': categories,
        'active_category': active_category,
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'items': items,
    }
    
    return render(request, 'app/cart.html', context)

@login_required
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer =customer, complete =False)
        items = order.orderitem_set.all()
        cartItems= order.get_cart_items
        user_not_login = "hidden;"
        user_login = "visible;"
    else:
        items =[]
        order ={'get_cart_items':0, 'get_cart_total' :0}
        cartItems= order['get_cart_items']
        user_not_login = "visible;"
        user_login = "hidden;"
    context={'items':items, 'order':order,'cartItems' :cartItems, 'user_not_login': user_not_login, 'user_login': user_login}
    return render(request, 'app/checkout.html', context)

def PaymentSuccsessful(request):
    data = json.loads(request.body)
    productId = data['productId']
    product = Product.objects.get(id = productId)
    context={'product' : product}
    return render(request, 'payment-succsess.html', context)

def paymentFailed(request):
    data = json.loads(request.body)
    productId = data['productId']
    product = Product.objects.get(id = productId)
    context={'product' : product}
    return render(request, 'paymentFailed.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer =customer, complete =False)
    orderItem, created = OrderItem.objects.get_or_create(order =order, product =product)
    if action == 'add':
        orderItem.quantity +=1
    elif action =='remove': 
        orderItem.quantity -=1
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('added', safe=False)

def create_paypal_transaction(request):
    data = json.loads(request.body)
    order_id = data.get('orderID')
    tx_id = data.get('txID')

    order = Order.objects.get(id=order_id)
    order.complete = True
    order.transaction_id = tx_id
    order.save()

    formatted_total_amount = "{:.2f}".format(convert_to_usd(order.get_cart_total))
    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "USD",
                    "value": formatted_total_amount
                }
            }
        ]
    }

    client = get_paypal_client()
    request = OrdersCreateRequest()
    request.prefer('return=representation')
    request.request_body(order_data)

    try:
        response = client.execute(request)
        order_id = response.result.id
        return JsonResponse({'orderID': order_id})
    except IOError as ioe:
        return JsonResponse({'error': str(ioe)}, status=500)

def convert_to_usd(local_amount):
    response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')  # từ VND sang USD
    data = response.json()
    rate = data['rates']['VND']
    usd_amount = local_amount / rate
    return usd_amount

def payment_success(request):
    user = request.user
    order, created = Order.objects.get_or_create(customer=user, complete=False)
    items = order.orderitem_set.all()
    cartItems = order.get_cart_items
    context = {'items':items, 'order':order,'cartItems' :cartItems}
    return render(request, 'app/payment_success.html', context)
