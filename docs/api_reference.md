# Sales Analytics & Business Intelligence REST API - Reference Guide

This document provides complete instructions and `curl` request examples for all endpoints.

## Base URL
- **Local Development**: `http://127.0.0.1:5000`
- **Render Production**: `https://<your-render-app>.onrender.com`

---

## 1. Authentication Endpoints (`/api/v1/auth`)

### Register User
**`POST /api/v1/auth/register`**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "analyst2@company.com",
    "password": "SecurePassword123!",
    "full_name": "Marcus Vance",
    "role": "analyst"
  }'
```

### Login & Retrieve JWT Tokens
**`POST /api/v1/auth/login`**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "password": "AdminPass123!"
  }'
```
**Response**:
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "Bearer",
  "success": true,
  "user": {
    "email": "admin@company.com",
    "full_name": "Executive Administrator",
    "role": "admin"
  }
}
```

### Refresh Token
**`POST /api/v1/auth/refresh`**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"
```

### Get Current Profile
**`GET /api/v1/auth/me`**
```bash
curl -X GET http://127.0.0.1:5000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

---

## 2. Sales Management Endpoints (`/api/v1/sales`)

### List Sales (Paginated & Filtered)
**`GET /api/v1/sales`**
```bash
curl -X GET "http://127.0.0.1:5000/api/v1/sales?page=1&per_page=10&region=North&start_date=2026-01-01&end_date=2026-12-31" \
  -H "Authorization: Bearer <access_token>"
```

### Create Sales Record
**`POST /api/v1/sales`**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/sales \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN-2026-8001",
    "customer_id": 1,
    "product_id": 1,
    "quantity": 5,
    "unit_price": 1199.99,
    "unit_cost": 650.00,
    "discount": 0.05,
    "sale_date": "2026-08-15",
    "region": "North",
    "payment_method": "Credit Card",
    "status": "Completed"
  }'
```

### Bulk Ingest Sales Dataset (CSV or Excel)
**`POST /api/v1/sales/upload`**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/sales/upload \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@data/sample_sales.csv"
```
Or for Excel:
```bash
curl -X POST http://127.0.0.1:5000/api/v1/sales/upload \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@data/sample_sales.xlsx"
```

---

## 3. Business Intelligence & Analytics Endpoints (`/api/v1/analytics`)

### Executive KPI Summary
**`GET /api/v1/analytics/summary`**
```bash
curl -X GET "http://127.0.0.1:5000/api/v1/analytics/summary?start_date=2026-01-01&end_date=2026-12-31" \
  -H "Authorization: Bearer <access_token>"
```
**Response**:
```json
{
  "success": true,
  "data": {
    "total_revenue": 145020.50,
    "total_cost": 72100.00,
    "total_profit": 72920.50,
    "gross_profit_margin_percent": 50.28,
    "total_units_sold": 412,
    "total_orders": 98,
    "average_order_value": 1479.80
  }
}
```

### Top-Selling Products
**`GET /api/v1/analytics/products/top?limit=5&order_by=revenue`**
```bash
curl -X GET "http://127.0.0.1:5000/api/v1/analytics/products/top?limit=5&order_by=revenue" \
  -H "Authorization: Bearer <access_token>"
```

### Regional Performance Breakdown
**`GET /api/v1/analytics/regions`**
```bash
curl -X GET http://127.0.0.1:5000/api/v1/analytics/regions \
  -H "Authorization: Bearer <access_token>"
```

### Monthly Sales Growth & Trends (MoM %)
**`GET /api/v1/analytics/trends/monthly`**
```bash
curl -X GET http://127.0.0.1:5000/api/v1/analytics/trends/monthly \
  -H "Authorization: Bearer <access_token>"
```

### Yearly Sales Trends (YoY %)
**`GET /api/v1/analytics/trends/yearly`**
```bash
curl -X GET http://127.0.0.1:5000/api/v1/analytics/trends/yearly \
  -H "Authorization: Bearer <access_token>"
```

### Summary Statistics (NumPy / Pandas Distribution)
**`GET /api/v1/analytics/stats`**
```bash
curl -X GET http://127.0.0.1:5000/api/v1/analytics/stats \
  -H "Authorization: Bearer <access_token>"
```

---

## 4. Report Generation & Exports (`/api/v1/reports`)

### Export CSV
**`GET /api/v1/reports/export/csv`**
```bash
curl -X GET "http://127.0.0.1:5000/api/v1/reports/export/csv?region=North" \
  -H "Authorization: Bearer <access_token>" \
  -o sales_export.csv
```

### Export Multi-Tab Styled Excel Workbook
**`GET /api/v1/reports/export/excel`**
```bash
curl -X GET http://127.0.0.1:5000/api/v1/reports/export/excel \
  -H "Authorization: Bearer <access_token>" \
  -o sales_bi_report.xlsx
```
