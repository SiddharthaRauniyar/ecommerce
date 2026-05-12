
from django.urls import path, include
from . import views

urlpatterns = [

    # =========================
    # HOME
    # =========================
    path('', views.home, name='home'),

    # =========================
    # PRODUCTS
    # =========================
    path('products/', views.product_list, name='products'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),

    path('category/', views.category, name='category'),
    path('search/', views.search_results, name='search_results'),
    path('review/', views.review, name='review'),

    # =========================
    # CART
    # =========================
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # =========================
    # CHECKOUT & PAYMENT
    # =========================
    path('checkout/', views.checkout, name='checkout'),

    path('payment/', views.payment, name='payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),

    path('order-success/<int:order_id>/', views.order_success, name='order_success'),

    path('invoice/<int:order_id>/', views.invoice, name='invoice'),

    # =========================
    # USER AUTH
    # =========================
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_page, name='logout'),

    # =========================
    # USER ORDERS
    # =========================
    path('profile/', views.profile, name='profile'),

    path('orders/', views.orders, name='orders'),

    path('order/<int:order_id>/', views.order_detail, name='order_detail'),

    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),

    path('track-order/<int:order_id>/', views.track_order, name='track_order'),

    # =========================
    # WISHLIST
    # =========================
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    # =========================
    # STATIC PAGES
    # =========================
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),

    # =========================
    # ADMIN PANEL
    # =========================
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('admin-product-add/', views.admin_product_add, name='admin_product_add'),
    path('admin-product-edit/<int:product_id>/', views.admin_product_edit, name='admin_product_edit'),
    path('admin-product-delete/<int:product_id>/', views.admin_product_delete, name='admin_product_delete'),

    path('admin-order-status/<int:order_id>/', views.admin_order_status, name='admin_order_status'),

    # =========================
    # DJANGO AUTH SYSTEM
    # =========================
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/update-status/<int:order_id>/', views.update_order_status, name='update_status'),
]