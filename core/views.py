from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Invoice, Quote, Expense, Customer, Product, Log
from .forms import InvoiceForm, QuoteForm, ExpenseForm, CustomerForm, ProductForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Q
from .utils import create_log
from django.core.paginator import Paginator

# Create your views here.

def home(request):
    # Receivables: sum of all accepted quotes MINUS sum of all invoices (regardless of paid/unpaid)
    accepted_quotes_total = Quote.objects.filter(status='accepted').aggregate(total=Sum('total_amount'))['total'] or 0
    invoiced_total = Invoice.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_receivables = accepted_quotes_total - invoiced_total
    # Outstanding invoices: sum of all unpaid invoices
    outstanding_invoices = Invoice.objects.filter(is_paid=False).aggregate(total=Sum('total_amount'))['total'] or 0
    # Total expenses
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    # Amount received: sum of all paid invoices
    total_received = Invoice.objects.filter(is_paid=True).aggregate(total=Sum('total_amount'))['total'] or 0
    # Total inflow: sum of all invoices (regardless of paid/unpaid)
    total_inflow = Invoice.objects.aggregate(total=Sum('total_amount'))['total'] or 0

    # Filtering
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    customer_id = request.GET.get('customer')
    invoice_qs = Invoice.objects.all()
    if from_date:
        invoice_qs = invoice_qs.filter(created_at__date__gte=from_date)
    if to_date:
        invoice_qs = invoice_qs.filter(created_at__date__lte=to_date)
    if customer_id:
        invoice_qs = invoice_qs.filter(customer_id=customer_id)
    filtered_inflow = invoice_qs.aggregate(total=Sum('total_amount'))['total'] or 0

    # Recent activity
    recent_logs = []
    for inv in Invoice.objects.order_by('-created_at')[:2]:
        recent_logs.append(f"Invoice #{inv.id} for {inv.customer.name} (₹{inv.total_amount})")
    for q in Quote.objects.order_by('-created_at')[:2]:
        recent_logs.append(f"Quote #{q.id} for {q.customer.name} (₹{q.total_amount})")
    for exp in Expense.objects.order_by('-date')[:2]:
        recent_logs.append(f"Expense: {exp.category} (₹{exp.amount})")
    recent_logs = sorted(recent_logs, reverse=True)[:5]

    customers = Customer.objects.all()
    return render(request, "home.html", {
        "total_receivables": total_receivables,
        "outstanding_invoices": outstanding_invoices,
        "total_expenses": total_expenses,
        "total_received": total_received,
        "total_inflow": total_inflow,
        "filtered_inflow": filtered_inflow,
        "recent_logs": recent_logs,
        "customers": customers,
        "from_date": from_date,
        "to_date": to_date,
        "selected_customer": int(customer_id) if customer_id else None,
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
            invoice = form.save()
            create_log(
                action='create',
                entity_type='invoice',
                entity_id=invoice.id,
                description=f"Created invoice #{invoice.id} for {invoice.customer.name}",
                amount=invoice.total_amount,
                user=request.user.username if request.user.is_authenticated else None
            )
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
            updated_invoice = form.save()
            create_log(
                action='update',
                entity_type='invoice',
                entity_id=invoice.id,
                description=f"Updated invoice #{invoice.id} for {invoice.customer.name}",
                amount=updated_invoice.total_amount,
                user=request.user.username if request.user.is_authenticated else None
            )
            return redirect('invoice_list')
    else:
        form = InvoiceForm(instance=invoice)
    return render(request, "invoice_form.html", {"form": form, "invoice": invoice})

@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        customer_name = invoice.customer.name
        invoice_id = invoice.id
        amount = invoice.total_amount
        invoice.delete()
        create_log(
            action='delete',
            entity_type='invoice',
            entity_id=invoice_id,
            description=f"Deleted invoice #{invoice_id} for {customer_name}",
            amount=amount,
            user=request.user.username if request.user.is_authenticated else None
        )
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
            quote = form.save()
            create_log(
                action='create',
                entity_type='quote',
                entity_id=quote.id,
                description=f"Created quote #{quote.id} for {quote.customer.name}",
                amount=quote.total_amount,
                user=request.user.username if request.user.is_authenticated else None
            )
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
            updated_quote = form.save()
            create_log(
                action='update',
                entity_type='quote',
                entity_id=quote.id,
                description=f"Updated quote #{quote.id} for {quote.customer.name}",
                amount=updated_quote.total_amount,
                user=request.user.username if request.user.is_authenticated else None
            )
            return redirect('quote_list')
    else:
        form = QuoteForm(instance=quote)
    return render(request, "quote_form.html", {"form": form, "quote": quote})

@login_required
def quote_delete(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    if request.method == 'POST':
        customer_name = quote.customer.name
        quote_id = quote.id
        amount = quote.total_amount
        quote.delete()
        create_log(
            action='delete',
            entity_type='quote',
            entity_id=quote_id,
            description=f"Deleted quote #{quote_id} for {customer_name}",
            amount=amount,
            user=request.user.username if request.user.is_authenticated else None
        )
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
            expense = form.save()
            create_log(
                action='create',
                entity_type='expense',
                entity_id=expense.id,
                description=f"Created expense: {expense.category}",
                amount=expense.amount,
                user=request.user.username if request.user.is_authenticated else None
            )
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
            updated_expense = form.save()
            create_log(
                action='update',
                entity_type='expense',
                entity_id=expense.id,
                description=f"Updated expense: {updated_expense.category}",
                amount=updated_expense.amount,
                user=request.user.username if request.user.is_authenticated else None
            )
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, "expense_form.html", {"form": form, "expense": expense})

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        category = expense.category
        expense_id = expense.id
        amount = expense.amount
        expense.delete()
        create_log(
            action='delete',
            entity_type='expense',
            entity_id=expense_id,
            description=f"Deleted expense: {category}",
            amount=amount,
            user=request.user.username if request.user.is_authenticated else None
        )
        return redirect('expense_list')
    return render(request, "expense_confirm_delete.html", {"expense": expense})

@login_required
def log_list(request):
    logs = Log.objects.all().order_by('-timestamp')
    
    # Filter by entity type
    entity_type = request.GET.get('entity_type')
    if entity_type:
        logs = logs.filter(entity_type=entity_type)
    
    # Filter by action
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
    
    # Filter by date range
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    if from_date:
        logs = logs.filter(timestamp__date__gte=from_date)
    if to_date:
        logs = logs.filter(timestamp__date__lte=to_date)
    
    # Pagination
    paginator = Paginator(logs, 25)  # Show 25 logs per page
    page = request.GET.get('page')
    logs = paginator.get_page(page)
    
    context = {
        'logs': logs,
        'entity_types': dict(Log.ENTITY_CHOICES),
        'action_types': dict(Log.ACTION_CHOICES),
        'from_date': from_date,
        'to_date': to_date,
        'selected_entity_type': entity_type,
        'selected_action': action,
    }
    return render(request, 'logs.html', context)

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
