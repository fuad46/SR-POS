from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User, Product, Order
from django.contrib.auth.decorators import login_required
from decimal import Decimal

# ✅ Register
def register_user(request):
    if request.method == 'POST':
        name = request.POST['name']
        phone = request.POST['phone']
        password = request.POST['password']
        if User.objects.filter(phone=phone).exists():
            messages.error(request, "Phone already exists")
        else:
            user = User.objects.create_user(name=name, phone=phone, password=password)
            messages.success(request, "Registered successfully!")
            return redirect('login')
    return render(request, 'register.html')

# ✅ Login
def login_user(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        password = request.POST['password']
        user = authenticate(phone=phone, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html')

# ✅ Logout
def logout_user(request):
    logout(request)
    return redirect('login')

# ✅ Home
from django.contrib.auth.decorators import login_required
@login_required
def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products, 'is_admin': request.user.is_admin})

# ✅ Add product (only for superuser)
# def add_product(request):
#     if request.method == "POST":
#         name = request.POST['name']
#         number = request.POST['number']
#         image = request.FILES['image']
#         quantity = request.POST['quantity']
#         price = request.POST['price']
#         production_cost = request.POST['production_cost']

#         Product.objects.create(
#             name=name,
#             number=number,
#             image=image,
#             quantity=quantity,
#             price=price,
#             production_cost=production_cost
#         )
#         return redirect('home')

#     return render(request, 'add_product.html')

# @login_required
# def add_product(request):
#     if request.method == "POST":
#         name = request.POST.get("name")
#         number = request.POST.get("number")
#         price = request.POST.get("price")
#         quantity = request.POST.get("quantity")
#         instock = request.POST.get("instock")
#         production_cost = request.POST.get("production_cost")
#         image = request.FILES.get("image")

#         Product.objects.create(
#             name=name,
#             number=number,
#             price=price,
#             quantity=quantity,
#             instock=instock,
#             production_cost=production_cost,
#             image=image
#         )

#         messages.success(request, "✅ Product added successfully!")
#         return redirect("add_product")  

#     return render(request, "add_product.html")

from django.db import IntegrityError

@login_required
def add_product(request):
    if request.method == "POST":
        try:
            name = request.POST.get("name")
            number = request.POST.get("number")
            price = request.POST.get("price")
            quantity = request.POST.get("quantity")
            instock = request.POST.get("instock")
            production_cost = request.POST.get("production_cost")
            image = request.FILES.get("image")

            Product.objects.create(
                name=name,
                number=number,
                price=price,
                quantity=quantity,
                instock=instock,
                production_cost=production_cost,
                image=image
            )
            messages.success(request, "✅ Product added successfully!")
            return redirect("add_product")

        except IntegrityError:
            messages.error(request, "❌ Product number already exists! Please choose another one.")
            return redirect("add_product")

    return render(request, "add_product.html")


@login_required
def update_price(request, product_id):
    if not request.user.is_admin:
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.number = request.POST.get('number', product.number)
        product.price = request.POST.get('price', product.price)
        product.production_cost = request.POST.get('production_cost', product.production_cost)
        product.quantity = request.POST.get('quantity', product.quantity)
        product.instock = request.POST.get('instock', product.instock)

        if request.FILES.get('image'):
            product.image = request.FILES['image']

        product.save()
        messages.success(request, "✅ Product updated successfully!")
        return redirect('home')

    return render(request, 'add_product.html', {'update': True, 'product': product})


# ✅ Add to Cart (Session-based)
# @login_required
# def add_to_cart(request, product_id):
#     cart = request.session.get('cart', {})
#     cart[str(product_id)] = cart.get(str(product_id), 0) + 1
#     request.session['cart'] = cart
#     return redirect('home')

@login_required
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
    else:
        quantity = 1

    # 🟢 Check if requested + existing in cart exceeds stock
    current_in_cart = cart.get(str(product_id), 0)
    if current_in_cart + quantity > product.instock:
        messages.error(request, f"❌ Not enough stock for {product.name}. Available: {product.instock}")
        return redirect('all_products')  # 👈 stays on product list

    # ✅ Otherwise add safely
    cart[str(product_id)] = current_in_cart + quantity
    request.session['cart'] = cart
    messages.success(request, f"✅ Added {quantity} × {product.name} to cart")
    return redirect('all_products')


# ✅ View Cart
@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for pid, qty in cart.items():
        product = Product.objects.get(id=int(pid))
        subtotal = product.price * qty
        total += subtotal
        items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})
    return render(request, 'cart.html', {'items': items, 'total': total})

# @login_required
# def buy_all(request):
#     cart = request.session.get('cart', {})
#     for pid, qty in cart.items():
#         product = Product.objects.get(id=int(pid))
#         total_price = Decimal(product.price) * qty
#         Order.objects.create(
#             user=request.user,
#             product=product,
#             product_name=product.name,
#             product_price=product.price,
#             quantity=qty,
#             total_price=total_price
#         )
#     request.session['cart'] = {}
#     messages.success(request, "Purchase successful!")
#     return redirect('home')

@login_required
# @login_required
# def buy_all(request):
#     cart = request.session.get('cart', {})
#     if not cart:
#         messages.error(request, "Cart is empty!")
#         return redirect('home')

#     session = PurchaseSession.objects.create(user=request.user)

#     for pid, qty in cart.items():
#         product = Product.objects.get(id=int(pid))

       
#         if product.instock < qty:
#             messages.error(request, f"Not enough stock for {product.name}! Available: {product.instock}")
#             return redirect('view_cart')

       
#         product.instock -= qty
#         product.save()

#         total_price = Decimal(product.price) * qty
#         Order.objects.create(
#             user=request.user,
#             session=session,
#             product=product,
#             product_name=product.name,
#             product_price=product.price,
#             quantity=qty,
#             total_price=total_price,
#             confirmed=True
#         )

#     request.session['cart'] = {}
#     messages.success(request, "Purchase successful!")
#     return redirect('see_buy_all')

@login_required
def buy_all(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Cart is empty!")
        return redirect('home')

    session = PurchaseSession.objects.create(user=request.user)

    for pid, qty in cart.items():
        product = Product.objects.get(id=int(pid))

        # 🛑 If stock not enough, cancel whole session and show message
        if product.instock < qty:
            session.delete()  # rollback empty session
            messages.error(request, f"❌ Not enough stock for {product.name}. Available: {product.instock}")
            return redirect('cart')

        # ✅ Deduct stock
        product.instock -= qty
        product.save()

        total_price = Decimal(product.price) * qty
        Order.objects.create(
            user=request.user,
            session=session,
            product=product,
            product_name=product.name,
            product_price=product.price,
            quantity=qty,
            total_price=total_price,
            confirmed=True
        )

    # 🧹 Clear cart only after success
    request.session['cart'] = {}
    messages.success(request, "✅ Purchase successful!")
    return redirect('see_buy_all')


from .models import PurchaseSession
@login_required
def see_buy_all(request):
    sessions = PurchaseSession.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'see_buy_all.html', {'sessions': sessions})


from django.shortcuts import render, get_object_or_404
from .models import Product, PurchaseSession, Order

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def purchase_details(request, session_id):
    session = get_object_or_404(PurchaseSession, id=session_id, user=request.user)
    orders = session.orders.all()
    total_price = sum(order.total_price for order in orders)
    return render(request, 'purchase_details.html', {
        'session': session,
        'orders': orders,
        'total_price': total_price
    })

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def delete_product(request, product_id):
    if not request.user.is_admin:
        return redirect('home')  # Prevent non-admin from deleting

    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('home')  # ✅ Return after deletion


from django.shortcuts import render
from django.db.models import Q
from .models import Product

def all_products(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(number__icontains=query)
        )
    else:
        products = Product.objects.all()
    return render(request, 'all-products.html', {'products': products, 'query': query})

@login_required
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
    else:
        quantity = 1  # fallback if accessed wrongly

    cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
    request.session['cart'] = cart
    return redirect('all_products')

# views.py
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.utils.timezone import now
from django.db.models.functions import ExtractMonth, ExtractYear
from calendar import month_name
from .models import Order

def profit_view(request):
    # Only confirmed orders that have a product
    confirmed_orders = Order.objects.filter(confirmed=True, product__isnull=False)

    # Annotate each order with revenue & profit
    confirmed_orders = confirmed_orders.annotate(
        revenue=ExpressionWrapper(
            F('product__price') * F('quantity'),
            output_field=DecimalField()
        ),
        profit=ExpressionWrapper(
            (F('product__price') - F('product__production_cost')) * F('quantity'),
            output_field=DecimalField()
        )
    )

    # Group by year + month
    monthly_data = (
        confirmed_orders
        .annotate(year=ExtractYear('created_at'), month=ExtractMonth('created_at'))
        .values('year', 'month')
        .annotate(
            total_revenue=Sum('revenue'),
            total_profit=Sum('profit')
        )
        .order_by('year', 'month')
    )

    # Format month name
    for entry in monthly_data:
        entry['month_name'] = month_name[entry['month']]

    return render(request, "profit.html", {
        "orders": confirmed_orders,
        "monthly_data": monthly_data,
    })


from django.shortcuts import render
from .models import Product

def inventory(request):
    products = Product.objects.all()
    return render(request, "inventory.html", {"products": products})


from django.shortcuts import render

def error_500(request):
    return render(request, "err.html", {
        "message": "Oops! Something went wrong. Please contact developer."
    }, status=500)



