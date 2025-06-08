from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Invoice, Quote, Expense, Customer, Product
from .forms import InvoiceForm, QuoteForm, ExpenseForm, CustomerForm, ProductForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Q
# Create your views here.

def home(request):
    total_receivables = Customer.objects.aggregate(
        total=Sum('invoices__total_amount', filter=Q(invoices__is_paid=False))
    )["total"] or 0
    outstanding_invoices = Invoice.objects.filter(is_paid=False).aggregate(
        total=Sum('total_amount')
    )["total"] or 0
    total_expenses = Expense.objects.aggregate(
        total=Sum('amount')
    )["total"] or 0
    # For demo, show last 5 invoices/quotes/expenses as 'recent activity'
    recent_logs = []
    for inv in Invoice.objects.order_by('-created_at')[:2]:
        recent_logs.append(f"Invoice #{inv.id} for {inv.customer.name} (₹{inv.total_amount})")
    for q in Quote.objects.order_by('-created_at')[:2]:
        recent_logs.append(f"Quote #{q.id} for {q.customer.name} (₹{q.total_amount})")
    for exp in Expense.objects.order_by('-date')[:2]:
        recent_logs.append(f"Expense: {exp.category} (₹{exp.amount})")
    recent_logs = sorted(recent_logs, reverse=True)[:5]
    return render(request, "home.html", {
        "total_receivables": total_receivables,
        "outstanding_invoices": outstanding_invoices,
        "total_expenses": total_expenses,
        "recent_logs": recent_logs,
    })

@login_required
def invoice_list(request):
    invoices = Invoice.objects.select_related('customer').all().order_by('-created_at')
    return render(request, "invoices.html", {"invoices": invoices})

@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('invoice_list')
    else:
        form = InvoiceForm()
    return render(request, "invoice_form.html", {"form": form})

@login_required
def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            return redirect('invoice_list')
    else:
        form = InvoiceForm(instance=invoice)
    return render(request, "invoice_form.html", {"form": form, "invoice": invoice})

@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        return redirect('invoice_list')
    return render(request, "invoice_confirm_delete.html", {"invoice": invoice})

@login_required
def quote_list(request):
    quotes = Quote.objects.select_related('customer').all().order_by('-created_at')
    return render(request, "quotes.html", {"quotes": quotes})

@login_required
def quote_create(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('quote_list')
    else:
        form = QuoteForm()
    return render(request, "quote_form.html", {"form": form})

@login_required
def quote_update(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    if request.method == 'POST':
        form = QuoteForm(request.POST, instance=quote)
        if form.is_valid():
            form.save()
            return redirect('quote_list')
    else:
        form = QuoteForm(instance=quote)
    return render(request, "quote_form.html", {"form": form, "quote": quote})

@login_required
def quote_delete(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    if request.method == 'POST':
        quote.delete()
        return redirect('quote_list')
    return render(request, "quote_confirm_delete.html", {"quote": quote})

@login_required
def expense_list(request):
    expenses = Expense.objects.all().order_by('-date')
    return render(request, "expenses.html", {"expenses": expenses})

@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, "expense_form.html", {"form": form})

@login_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, "expense_form.html", {"form": form, "expense": expense})

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')
    return render(request, "expense_confirm_delete.html", {"expense": expense})

@login_required
def log_list(request):
    logs = []
    return render(request, "logs.html", {"logs": logs})

@csrf_exempt
@login_required
def customer_create_popup(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            return JsonResponse({'success': True, 'id': customer.id, 'name': customer.name})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = CustomerForm()
    return render(request, 'customer_form_popup.html', {'form': form})

@csrf_exempt
@login_required
def product_create_popup(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            return JsonResponse({'success': True, 'id': product.id, 'name': product.name})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = ProductForm()
    return render(request, 'product_form_popup.html', {'form': form})
