from django.contrib import admin
from .models import Product, Customer, Quote, QuoteLineItem, Invoice, InvoiceLineItem, Expense
from .admin_branding import *

class QuoteLineItemInline(admin.TabularInline):
    model = QuoteLineItem
    extra = 1

class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price_inr", "is_service")
    search_fields = ("name",)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "customer_type", "gstin", "phone", "email", "receivables")
    search_fields = ("name", "gstin", "phone", "email")

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "total_amount", "expiry_date", "created_at")
    list_filter = ("status", "created_at")
    inlines = [QuoteLineItemInline]

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "total_amount", "is_paid", "created_at")
    list_filter = ("is_paid", "created_at")
    inlines = [InvoiceLineItemInline]

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("date", "amount", "category", "vendor", "payment_method")
    list_filter = ("category", "date")
    search_fields = ("vendor",)
