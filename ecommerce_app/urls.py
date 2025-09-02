from django.urls import path
from . import views
from django.shortcuts import redirect
urlpatterns = [
    
    path('', views.home, name='home'),
    path('', lambda request: redirect('login')),  # root → login
     path('login/', views.login_user, name='login'),   # ✅ Add this
    path('register/', views.register_user, name='register'),
    
    path('add_product/', views.add_product, name='add_product'),
    path('update_price/<int:product_id>/', views.update_price, name='update_price'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('buy_all/', views.buy_all, name='buy_all'),
    path('logout/', views.logout_user, name='logout'),
    path('see-buy-all/', views.see_buy_all, name='see_buy_all'),
    path('purchase-details/<int:session_id>/', views.purchase_details, name='purchase_details'),

    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('all-products/', views.all_products, name='all_products'),

    path("profit/", views.profit_view, name="profit"),
    path("inventory/", views.inventory, name="inventory"),


]
