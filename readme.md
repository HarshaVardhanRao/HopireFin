I want to build a Django-based internal ERP-style web application for our company Hopire to manage all key business workflows including product/service listing, customer management, quote generation, invoicing, receivables tracking, and expense tracking.

The system should have:

1. Product/Service Catalog
Add and manage services/products with default INR pricing and descriptions.

2. Customer Management
Add customers (individual or company) with details like name, billing/shipping addresses, GSTIN, phone, email, etc.

Show receivables per customer.

3. Quote Management
Create quotes by selecting a customer and adding line items (products/services).

Apply discounts and taxes per item.

Set expiry date and quote status (draft, sent, accepted, declined).

Share as PDF or email.

4. Quote Approval Logic
Once a quote is marked "Accepted", its total value should be reflected as the customer's receivable.

5. Invoice Management
Create invoices from accepted quotes (full/partial).

Also allow independent invoice creation.

Include reference ID, payment method, and optional notes.

6. Expense Tracking
Add operational expenses like rent, legal, etc.

Store date, amount, category, vendor, and payment method.

Optional upload of receipts.

7. (Optional) Dashboard
Overview of total receivables, income vs expenses chart, outstanding invoices, recent activity.

8. Tech Requirements
Backend: Django (w/ optional DRF)

DB: PostgreSQL

UI: Django Admin (or basic custom UI)

PDF Export: WeasyPrint or ReportLab

Email Integration for quote/invoice sending
