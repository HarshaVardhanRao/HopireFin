from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Invoice CRUD
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/edit/', views.invoice_update, name='invoice_update'),
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    # Quote CRUD
    path('quotes/', views.quote_list, name='quote_list'),
    path('quotes/create/', views.quote_create, name='quote_create'),
    path('quotes/<int:pk>/edit/', views.quote_update, name='quote_update'),
    path('quotes/<int:pk>/delete/', views.quote_delete, name='quote_delete'),
    # Expense CRUD
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/edit/', views.expense_update, name='expense_update'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    # Logs
    path('logs/', views.log_list, name='log_list'),
    # Customer CRUD
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    # Product CRUD
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    # Customer and Product Popups
    path('customers/create-popup/', views.customer_create_popup, name='customer_create_popup'),
    path('products/create-popup/', views.product_create_popup, name='product_create_popup'),
    # Preview routes
    path('invoices/<int:pk>/preview/', views.invoice_preview, name='invoice_preview'),
    path('quotes/<int:pk>/preview/', views.quote_preview, name='quote_preview'),
]
