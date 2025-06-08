from django import forms
from .models import Invoice, Quote, Expense, Customer, Product

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer', 'quote', 'reference_id', 'payment_method', 'total_amount', 'notes', 'is_paid']

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['customer', 'expiry_date', 'status', 'total_amount', 'notes']

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'amount', 'category', 'vendor', 'payment_method', 'receipt', 'notes']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customer_type', 'name', 'billing_address', 'shipping_address', 'gstin', 'phone', 'email']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price_inr', 'is_service']
