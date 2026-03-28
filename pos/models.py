from django.db import models
from django.utils import timezone
import uuid


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='tenants/logos/', blank=True, null=True)
    banner_color = models.CharField(max_length=7, default='#FF6B35')
    secondary_color = models.CharField(max_length=7, default='#F7C59F')
    cuisine_type = models.CharField(max_length=50)
    stall_number = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    is_open = models.BooleanField(default=True)
    opening_time = models.TimeField(default='08:00')
    closing_time = models.TimeField(default='22:00')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    total_orders = models.IntegerField(default=0)
    icon_emoji = models.CharField(max_length=10, default='🍽️')

    class Meta:
        ordering = ['stall_number']

    def __str__(self):
        return f"{self.stall_number} - {self.name}"


class Category(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=50)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.tenant.name} - {self.name}"


class Product(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)
    preparation_time = models.IntegerField(default=10, help_text='Minutes')
    calories = models.IntegerField(null=True, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.tenant.name} - {self.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('qris', 'QRIS'),
        ('gopay', 'GoPay'),
        ('ovo', 'OVO'),
        ('dana', 'DANA'),
    ]

    order_number = models.CharField(max_length=20, unique=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='orders')
    table_number = models.CharField(max_length=10, blank=True)
    customer_name = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, blank=True)
    payment_status = models.CharField(max_length=20, default='unpaid')
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    service_charge = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} - {self.tenant.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=0)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order.order_number} - {self.product.name} x{self.quantity}"
