from django.db import models
from django.utils import timezone

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price_inr = models.DecimalField(max_digits=12, decimal_places=2)
    is_service = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Customer(models.Model):
    INDIVIDUAL = 'individual'
    COMPANY = 'company'
    CUSTOMER_TYPE_CHOICES = [
        (INDIVIDUAL, 'Individual'),
        (COMPANY, 'Company'),
    ]
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES)
    name = models.CharField(max_length=255)
    billing_address = models.TextField()
    shipping_address = models.TextField(blank=True)
    gstin = models.CharField(max_length=15, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name

    @property
    def receivables(self):
        from django.db.models import Sum, Q
        # Receivables: sum of all accepted quotes minus sum of all paid invoices
        accepted_quotes = self.quotes.filter(status='accepted').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        unpaid_invoices = self.invoices.filter(is_paid=False).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        paid_invoices = self.invoices.filter(is_paid=True).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        # Receivables = accepted quotes (not yet invoiced) + unpaid invoices
        return accepted_quotes + unpaid_invoices

    @property
    def amount_received(self):
        from django.db.models import Sum
        # Amount received: sum of all paid invoices
        paid_invoices = self.invoices.filter(is_paid=True).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        return paid_invoices

class Quote(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    customer = models.ForeignKey(Customer, related_name='quotes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Quote #{self.id} - {self.customer.name}"

class QuoteLineItem(models.Model):
    quote = models.ForeignKey(Quote, related_name='line_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def line_total(self):
        return (self.unit_price * self.quantity) - self.discount + self.tax

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Invoice(models.Model):
    customer = models.ForeignKey(Customer, related_name='invoices', on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, related_name='invoices', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reference_id = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=100, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer.name}"

class InvoiceLineItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='line_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def line_total(self):
        return (self.unit_price * self.quantity) - self.discount + self.tax

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('rent', 'Rent'),
        ('legal', 'Legal'),
        ('utilities', 'Utilities'),
        ('other', 'Other'),
    ]
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    vendor = models.CharField(max_length=255, blank=True)
    payment_method = models.CharField(max_length=100, blank=True)
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.category} - {self.amount} on {self.date}"

class Log(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('payment', 'Payment'),
    ]
    ENTITY_CHOICES = [
        ('invoice', 'Invoice'),
        ('quote', 'Quote'),
        ('expense', 'Expense'),
        ('customer', 'Customer'),
        ('product', 'Product'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=20, choices=ENTITY_CHOICES)
    entity_id = models.PositiveIntegerField()
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    user = models.CharField(max_length=255, blank=True)  # Store username or user identifier

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} {self.entity_type} #{self.entity_id} - {self.timestamp}"
