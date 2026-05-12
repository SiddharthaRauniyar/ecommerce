from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from .models import Product, CartItem, WishlistItem, Order, OrderItem
from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta
from .models import Order, OrderStatusHistory
import json


# =========================
# HOME
# =========================
def home(request):
    products = Product.objects.all()
    return render(request, "store/home.html", {"products": products})


# =========================
# PRODUCTS
# =========================
def product_list(request):
    products = Product.objects.all()
    return render(request, "store/products.html", {"products": products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "store/product_detail.html", {"product": product})


def category(request):
    return render(request, "store/category.html")


def search_results(request):
    query = request.GET.get("q")
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.none()
    return render(request, "store/search_results.html", {"products": products, "query": query})


def review(request):
    return render(request, "store/review.html")


# =========================
# CART (SESSION BASED)
# =========================
def get_cart(request):
    return request.session.get("cart", {})


def save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


def cart(request):
    cart = get_cart(request)
    cart_items = []
    total = 0

    for product_id, qty in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_total = product.price * qty
        total += item_total

        cart_items.append({
            "product": product,
            "quantity": qty,
            "total_price": item_total
        })

    return render(request, "store/cart.html", {
        "cart_items": cart_items,
        "total": total
    })



def add_to_cart(request, product_id):

    cart = get_cart(request)
    product_id = str(product_id)

    qty = int(request.POST.get("quantity", 1))

    if product_id in cart:
        cart[product_id] += qty
    else:
        cart[product_id] = qty

    save_cart(request, cart)

    return redirect("cart")


def update_cart(request, item_id):

    cart = get_cart(request)
    product_id = str(item_id)

    if request.method == "POST":
        try:
            qty = int(request.POST.get("quantity", 1))
        except:
            qty = 1

        cart[product_id] = qty

    save_cart(request, cart)
    return redirect("cart")


def remove_from_cart(request, item_id):
    cart = get_cart(request)
    product_id = str(item_id)

    if product_id in cart:
        del cart[product_id]

    save_cart(request, cart)
    return redirect("cart")


# =========================
# CHECKOUT
# =========================

def checkout(request):

    cart = get_cart(request)
    cart_items = []
    total = 0

    # =========================
    # BUILD CART SUMMARY
    # =========================
    for product_id, qty in cart.items():
        product = get_object_or_404(Product, id=product_id)

        item_total = product.price * qty
        total += item_total

        cart_items.append({
            "product": product,
            "quantity": qty,
            "total_price": item_total
        })

    # =========================
    # PLACE ORDER
    # =========================
    if request.method == "POST":

        order = Order.objects.create(
             user=request.user,
            full_name=request.POST.get("full_name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
            city=request.POST.get("city"),
            postcode=request.POST.get("postcode"),
            total_price=total,
            status="pending"
        )

        # =========================
        # SAVE ORDER ITEMS + STOCK REDUCTION
        # =========================
        for item in cart_items:
            product = item["product"]

            OrderItem.objects.create(
                order=order,
                product_name=product.name,
                quantity=item["quantity"],
                price=product.price
            )

            # reduce stock safely
            product.stock -= item["quantity"]
            if product.stock < 0:
                product.stock = 0
            product.save()

        # clear cart
        request.session["cart"] = {}

        # =========================
        # BUILD EMAIL (HTML INVOICE)
        # =========================
        items_html = ""

        for item in cart_items:
            items_html += f"""
            <tr>
                <td>{item['product'].name}</td>
                <td>{item['quantity']}</td>
                <td>£{item['product'].price}</td>
            </tr>
            """

        html_message = f"""
        <h2>🧾 EcoSecure Order Invoice</h2>

        <p>Hi <b>{order.full_name}</b>,</p>

        <p>Your order <b>#{order.id}</b> has been successfully placed.</p>

        <h3>Order Summary</h3>

        <table border="1" cellpadding="8" cellspacing="0">
            <tr>
                <th>Product</th>
                <th>Qty</th>
                <th>Price</th>
            </tr>
            {items_html}
        </table>

        <h3>Total: £{order.total_price}</h3>

        <p>Thank you for shopping with EcoSecure 🌱</p>
        """

        email = EmailMultiAlternatives(
            subject="EcoSecure Order Confirmation",
            body="Order placed successfully",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )

        email.attach_alternative(html_message, "text/html")
        email.send()

        # redirect AFTER everything
        return redirect("order_success", order_id=order.id)

    # =========================
    # RENDER PAGE
    # =========================
    return render(request, "store/checkout.html", {
        "cart_items": cart_items,
        "total": total
    })
# =========================
# PAYMENT (SIMULATED)
# =========================
def payment(request):
    return render(request, "store/payment.html")


def payment_success(request):
    return render(request, "store/payment_success.html")


def payment_failed(request):
    return render(request, "store/payment_failed.html")



def invoice(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    return render(request, "store/invoice.html", {
        "order": order
    })

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "store/order_success.html", {"order": order})


# =========================
# AUTH
# =========================
def login_page(request):

    if request.method == "POST":

        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )

        if user:
            login(request, user)
            return redirect("home")

    return render(request, "registration/login.html")


def register_page(request):
    return render(request, "store/register.html")


def logout_page(request):
    logout(request)
    return redirect("home")


# =========================
# PROFILE / ORDERS
# =========================
def profile(request):
    return render(request, "store/profile.html")



@login_required
def orders(request):

    orders = Order.objects.all().order_by("-id")

    return render(request, "store/orders.html", {
        "orders": orders
    })



def order_detail(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    return render(request, "store/order_detail.html", {
        "order": order
    })

def cancel_order(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    order.status = "cancelled"
    order.save()

    return redirect("orders")


# =========================
# WISHLIST (FIXED)
# =========================
def wishlist(request):

    items = WishlistItem.objects.filter(user=request.user)
    return render(request, "store/wishlist.html", {"wishlist_items": items})


def add_to_wishlist(request, product_id):

    if not request.user.is_authenticated:
        return redirect("login")

    product = get_object_or_404(Product, id=product_id)

    WishlistItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect("wishlist")

def remove_from_wishlist(request, item_id):

    item = get_object_or_404(WishlistItem, id=item_id)
    item.delete()

    return redirect("wishlist")


# =========================
# STATIC
# =========================
def about(request):
    return render(request, "store/about.html")


def contact(request):
    return render(request, "store/contact.html")


def faq(request):
    return render(request, "store/faq.html")


# =========================
# ADMIN
# =========================
def admin_login(request):

    if request.method == "POST":

        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )

        if user and user.is_staff:
            login(request, user)
            return redirect("admin_dashboard")

    return render(request, "store/admin_login.html")


@login_required

def admin_dashboard(request):

    orders = Order.objects.all()

    last_7_days = []
    revenue_data = []

    for i in range(7):
        day = now().date() - timedelta(days=i)
        total = Order.objects.filter(created_at__date=day).aggregate(Sum('total_price'))['total_price__sum'] or 0

        last_7_days.append(str(day))
        revenue_data.append(float(total))

    return render(request, "store/admin_dashboard.html", {
        "total_orders": orders.count(),
        "total_products": Product.objects.count(),
        "pending_orders": orders.filter(status="pending").count(),
        "revenue": sum(o.total_price for o in orders),

        "chart_labels": last_7_days[::-1],
        "chart_data": revenue_data[::-1],
        "recent_orders": orders.order_by("-id")[:10],
    })

def admin_product_add(request):

    if request.method == "POST":

        Product.objects.create(
            name=request.POST.get("name"),
            category=request.POST.get("category"),
            description=request.POST.get("description"),
            price=request.POST.get("price"),
            stock=request.POST.get("stock"),
            eco_score=request.POST.get("eco_score"),
            image=request.FILES.get("image")
        )

    return redirect("admin_dashboard")


def admin_product_edit(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")
        product.save()

    return JsonResponse({"status": "updated"})


def admin_product_delete(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    product.delete()

    return JsonResponse({"status": "deleted"})




def admin_order_status(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":

        new_status = request.POST.get("status")
        order.status = new_status
        order.save()

        # =========================
        # EMAIL ON STATUS CHANGE
        # =========================
        send_mail(
            subject=f"Order #{order.id} Update",
            message=f"""
Hi {order.full_name},

Your order status has been updated to: {order.status}

Thank you for shopping with EcoSecure 🌱
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )

        return redirect("admin_dashboard")
def track_order(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    return render(request, "store/order_tracking.html", {
        "order": order
    })

def update_order_status(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":

        new_status = request.POST.get("status")

        # UPDATE ORDER
        order.status = new_status
        order.save()

        # SAVE HISTORY
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status
        )

        # EMAIL NOTIFICATION
        send_mail(
            subject=f"Order #{order.id} Update",
            message=f"Your order status is now: {new_status}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
        )

        return redirect("admin_dashboard")

    return render(request, "store/update_status.html", {"order": order})