from django.urls import path
from . import views

urlpatterns = [
    # Main kiosk pages
    path('', views.home, name='home'),
    path('tenant/<slug:slug>/', views.tenant_detail, name='tenant_detail'),
    path('order/', views.order_page, name='order_page'),
    path('order/success/<str:order_number>/', views.order_success, name='order_success'),
    
    # HTMX endpoints
    path('htmx/tenant/<slug:slug>/products/', views.htmx_tenant_products, name='htmx_tenant_products'),
    path('htmx/cart/add/', views.htmx_cart_add, name='htmx_cart_add'),
    path('htmx/cart/remove/<int:product_id>/', views.htmx_cart_remove, name='htmx_cart_remove'),
    path('htmx/cart/update/', views.htmx_cart_update, name='htmx_cart_update'),
    path('htmx/cart/clear/', views.htmx_cart_clear, name='htmx_cart_clear'),
    path('htmx/cart/', views.htmx_cart, name='htmx_cart'),
    path('htmx/checkout/', views.htmx_checkout, name='htmx_checkout'),
    path('htmx/products/filter/', views.htmx_product_filter, name='htmx_product_filter'),
    path('htmx/order/place/', views.htmx_place_order, name='htmx_place_order'),
    
    # Receipt
    path('receipt/<str:order_number>/', views.receipt, name='receipt'),
]
