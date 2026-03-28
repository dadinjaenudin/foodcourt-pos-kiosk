from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from decimal import Decimal
import json

from .models import Tenant, Product, Category, Order, OrderItem


def get_cart(request):
    """Get cart from session"""
    return request.session.get('cart', {})


def save_cart(request, cart):
    """Save cart to session"""
    request.session['cart'] = cart
    request.session.modified = True


def get_cart_summary(cart, tenant_id=None):
    """Calculate cart totals"""
    items = []
    subtotal = Decimal('0')
    
    for key, item in cart.items():
        item_total = Decimal(str(item['price'])) * item['quantity']
        subtotal += item_total
        if tenant_id is None or item.get('tenant_id') == tenant_id:
            items.append({
                'product_id': item['product_id'],
                'name': item['name'],
                'price': Decimal(str(item['price'])),
                'quantity': item['quantity'],
                'total': item_total,
                'image': item.get('image', ''),
                'tenant_name': item.get('tenant_name', ''),
            })
    
    tax = subtotal * Decimal('0.11')
    service = subtotal * Decimal('0.05')
    total = subtotal + tax + service
    
    return {
        'items': items,
        'subtotal': subtotal,
        'tax': tax,
        'service': service,
        'total': total,
        'count': sum(item['quantity'] for item in cart.values()),
    }


CUISINE_LIST = [
    ('🍽️', 'Semua', 'all'),
    ('🍜', 'Jepang', 'japanese'),
    ('🥩', 'Korea', 'korean'),
    ('🍕', 'Italia', 'italian'),
    ('🍛', 'Indonesia', 'indonesian'),
    ('🍔', 'Amerika', 'american'),
    ('🌶️', 'Thailand', 'thai'),
    ('🥟', 'China', 'chinese'),
    ('🧋', 'Minuman', 'beverage'),
    ('🌮', 'Meksiko', 'mexican'),
    ('🍨', 'Dessert', 'dessert'),
]


def home(request):
    """Main food court homepage - tenant selection"""
    tenants = Tenant.objects.filter(is_active=True).order_by('stall_number')
    cart = get_cart(request)
    cart_summary = get_cart_summary(cart)
    
    context = {
        'tenants': tenants,
        'cart_count': cart_summary['count'],
        'cart_total': cart_summary['total'],
        'cuisine_list': CUISINE_LIST,
    }
    return render(request, 'pos/home.html', context)


def tenant_detail(request, slug):
    """Tenant menu page"""
    tenant = get_object_or_404(Tenant, slug=slug, is_active=True)
    categories = tenant.categories.all()
    products = tenant.products.filter(is_available=True)
    featured = products.filter(is_featured=True)
    
    cart = get_cart(request)
    cart_summary = get_cart_summary(cart)
    
    context = {
        'tenant': tenant,
        'categories': categories,
        'products': products,
        'featured': featured,
        'cart': cart_summary,
        'cart_count': cart_summary['count'],
        'cart_total': cart_summary['total'],
    }
    return render(request, 'pos/tenant_detail.html', context)


def order_page(request):
    """Order review and checkout page"""
    cart = get_cart(request)
    cart_summary = get_cart_summary(cart)
    
    if not cart:
        return redirect('home')
    
    context = {
        'cart': cart_summary,
        'cart_count': cart_summary['count'],
        'cart_total': cart_summary['total'],
    }
    return render(request, 'pos/order.html', context)


def order_success(request, order_number):
    """Order success page"""
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'pos/order_success.html', {'order': order})


def receipt(request, order_number):
    """Receipt page"""
    order = get_object_or_404(Order, order_number=order_number)
    items = order.items.all().select_related('product')
    return render(request, 'pos/receipt.html', {'order': order, 'items': items})


# ===== HTMX Views =====

def htmx_tenant_products(request, slug):
    """HTMX: Load tenant products"""
    tenant = get_object_or_404(Tenant, slug=slug)
    category_id = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    products = tenant.products.filter(is_available=True)
    
    if category_id:
        products = products.filter(category_id=category_id)
    if search:
        products = products.filter(name__icontains=search)
    
    cart = get_cart(request)
    
    return render(request, 'pos/partials/product_grid.html', {
        'products': products,
        'tenant': tenant,
        'cart': cart,
    })


@require_http_methods(["POST"])
def htmx_cart_add(request):
    """HTMX: Add item to cart"""
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    
    product = get_object_or_404(Product, id=product_id, is_available=True)
    cart = get_cart(request)
    
    key = str(product_id)
    if key in cart:
        cart[key]['quantity'] += quantity
    else:
        cart[key] = {
            'product_id': product.id,
            'name': product.name,
            'price': str(product.price),
            'quantity': quantity,
            'image': product.image.url if product.image else '',
            'tenant_name': product.tenant.name,
            'tenant_id': product.tenant.id,
            'tenant_slug': product.tenant.slug,
        }
    
    save_cart(request, cart)
    cart_summary = get_cart_summary(cart)
    
    response = render(request, 'pos/partials/cart_sidebar.html', {
        'cart': cart_summary,
    })
    response['HX-Trigger'] = 'cartUpdated'
    return response


@require_http_methods(["POST"])
def htmx_cart_remove(request, product_id):
    """HTMX: Remove item from cart"""
    cart = get_cart(request)
    key = str(product_id)
    
    if key in cart:
        del cart[key]
        save_cart(request, cart)
    
    cart_summary = get_cart_summary(cart)
    response = render(request, 'pos/partials/cart_sidebar.html', {
        'cart': cart_summary,
    })
    response['HX-Trigger'] = 'cartUpdated'
    return response


@require_http_methods(["POST"])
def htmx_cart_update(request):
    """HTMX: Update cart item quantity"""
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    
    cart = get_cart(request)
    key = str(product_id)
    
    if key in cart:
        if quantity <= 0:
            del cart[key]
        else:
            cart[key]['quantity'] = quantity
        save_cart(request, cart)
    
    cart_summary = get_cart_summary(cart)
    response = render(request, 'pos/partials/cart_sidebar.html', {
        'cart': cart_summary,
    })
    response['HX-Trigger'] = 'cartUpdated'
    return response


@require_http_methods(["POST"])
def htmx_cart_clear(request):
    """HTMX: Clear entire cart"""
    save_cart(request, {})
    cart_summary = get_cart_summary({})
    response = render(request, 'pos/partials/cart_sidebar.html', {
        'cart': cart_summary,
    })
    response['HX-Trigger'] = 'cartUpdated'
    return response


def htmx_cart(request):
    """HTMX: Get cart partial"""
    cart = get_cart(request)
    cart_summary = get_cart_summary(cart)
    return render(request, 'pos/partials/cart_sidebar.html', {
        'cart': cart_summary,
    })


def htmx_checkout(request):
    """HTMX: Show checkout form"""
    cart = get_cart(request)
    cart_summary = get_cart_summary(cart)
    return render(request, 'pos/partials/checkout_form.html', {
        'cart': cart_summary,
    })


@require_http_methods(["POST"])
def htmx_place_order(request):
    """HTMX: Place order"""
    cart = get_cart(request)
    
    if not cart:
        return HttpResponse('<div class="text-red-500">Cart is empty!</div>')
    
    customer_name = request.POST.get('customer_name', 'Guest')
    table_number = request.POST.get('table_number', '')
    payment_method = request.POST.get('payment_method', 'cash')
    notes = request.POST.get('notes', '')
    
    # Group items by tenant
    tenant_items = {}
    for key, item in cart.items():
        tid = item['tenant_id']
        if tid not in tenant_items:
            tenant_items[tid] = []
        tenant_items[tid].append(item)
    
    orders = []
    for tenant_id, items in tenant_items.items():
        tenant = Tenant.objects.get(id=tenant_id)
        subtotal = sum(Decimal(str(i['price'])) * i['quantity'] for i in items)
        tax = subtotal * Decimal('0.11')
        service = subtotal * Decimal('0.05')
        total = subtotal + tax + service
        
        order = Order.objects.create(
            tenant=tenant,
            customer_name=customer_name,
            table_number=table_number,
            payment_method=payment_method,
            payment_status='paid',
            status='confirmed',
            subtotal=int(subtotal),
            tax=int(tax),
            service_charge=int(service),
            total=int(total),
            notes=notes,
        )
        
        for item in items:
            product = Product.objects.get(id=item['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                unit_price=Decimal(str(item['price'])),
                subtotal=Decimal(str(item['price'])) * item['quantity'],
            )
        
        tenant.total_orders += 1
        tenant.save()
        orders.append(order)
    
    # Clear cart
    save_cart(request, {})
    
    main_order = orders[0]
    response = HttpResponse()
    response['HX-Redirect'] = f'/order/success/{main_order.order_number}/'
    return response


def htmx_product_filter(request):
    """HTMX: Filter products"""
    tenant_id = request.GET.get('tenant_id')
    category_id = request.GET.get('category', '')
    
    tenant = get_object_or_404(Tenant, id=tenant_id)
    products = tenant.products.filter(is_available=True)
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    cart = get_cart(request)
    return render(request, 'pos/partials/product_grid.html', {
        'products': products,
        'tenant': tenant,
        'cart': cart,
    })
