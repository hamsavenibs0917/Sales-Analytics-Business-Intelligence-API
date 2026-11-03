# 📊 Sales Analytics & Business Intelligence REST API

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Flask%203.0-green.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/database-PostgreSQL%20%7C%20SQLite-blue.svg)](https://www.postgresql.org/)
[![Testing](https://img.shields.io/badge/tests-Pytest%20(20%2F20%20passed)-brightgreen.svg)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

An enterprise-grade **Sales Analytics and Business Intelligence (BI) REST API** built with **Python Flask**, **PostgreSQL**, **SQLAlchemy**, **Pandas**, **NumPy**, and **JWT Authentication**. 

It provides end-to-end sales transactions management, high-performance data processing, file cleaning and deduplication for CSV/Excel uploads, advanced business intelligence analytics (MoM/YoY growth trajectories, regional and product performance, statistical distributions), and automated multi-tab corporate Excel and CSV report exports.

---

## 🏛️ System Architecture

```
                              ┌───────────────────────────────────┐
                              │    Client (Web / Mobile / BI)     │
                              └─────────────────┬─────────────────┘
                                                │ HTTPS / JSON / Multipart
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Flask Application                                      │
│                                                                                        │
│  ┌────────────────────┐   ┌───────────────────────────┐   ┌─────────────────────────┐  │
│  │   Auth Blueprint   │   │      Sales Blueprint      │   │   Analytics Blueprint   │  │
│  │ (JWT, RBAC, Users) │   │ (CRUD, CSV/Excel Ingest)  │   │ (KPIs, MoM/YoY, Trends) │  │
│  └────────────────────┘   └───────────────────────────┘   └─────────────────────────┘  │
│  ┌────────────────────┐   ┌───────────────────────────┐   ┌─────────────────────────┐  │
│  │ Customer Blueprint │   │     Product Blueprint     │   │    Reports Blueprint    │  │
│  │   (CRM endpoints)  │   │   (Catalog & Margins)     │   │   (CSV & Excel Export)  │  │
│  └────────────────────┘   └───────────────────────────┘   └─────────────────────────┘  │
│                                       │                                                │
│                                       ▼                                                │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │                       Service Layer & Business Intelligence                      │  │
│  │  - DataProcessor (Pandas/NumPy data cleaning, validation, deduplication)         │  │
│  │  - AnalyticsService (SQL aggregates + Pandas time-series, growth calculations)   │  │
│  │  - ReportService (openpyxl multi-sheet workbook generation, CSV streams)         │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                                │
│                                       ▼                                                │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │                      Data Access Layer (SQLAlchemy ORM)                          │  │
│  │       Models: User, Customer, Product, Sale (Indexes, Foreign Keys, Joins)       │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────┬────────────────────────────────────────────────┘
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────┐
             │       PostgreSQL (Production) / SQLite (Dev)        │
             └─────────────────────────────────────────────────────┘
```

---

## ⚡ Technology Stack

- **Web Framework**: Python Flask (Application Factory pattern, Blueprints)
- **Database & ORM**: PostgreSQL (production), SQLite (local dev & testing), SQLAlchemy 2.0, Flask-SQLAlchemy
- **Authentication**: JWT (JSON Web Tokens) with `Flask-JWT-Extended` & Role-Based Access Control (`admin`, `analyst`, `user`)
- **Data Engineering & Analytics**:
  - **Pandas**: Ingestion, data cleaning, date coercion, column mapping, in-batch deduplication, Month-over-Month (MoM) and Year-over-Year (YoY) momentum calculations
  - **NumPy**: Statistical distribution modeling (mean, median, standard deviation, interquartile ranges, quartiles)
- **Report Generation**: `openpyxl` (styled multi-tab formatted Excel workbooks) & streaming CSV
- **Validation**: Marshmallow schemas
- **Testing**: Pytest with in-memory database test fixtures
- **Production Server**: Gunicorn WSGI

---

## 🚀 Key Features

### 1. Sales Data Management
- Complete CRUD operations on sales records.
- Automated server-side financial calculations: Total Revenue ($qty \times price \times (1 - discount)$), Total Cost ($qty \times cost$), and Net Profit ($revenue - cost$).
- Flexible date-range and multi-criteria query filtering.

### 2. High-Performance ETL & Dataset Upload
- Supports both **CSV** (`.csv`) and **Excel** (`.xlsx`, `.xls`) uploads via `POST /api/v1/sales/upload`.
- Automatic header alias normalization (matches variations like `order_id`, `invoice_no`, `trans_id`).
- Two-tier deduplication:
  1. In-batch transaction deduplication.
  2. Database cross-check against existing records to ensure idempotency.
- Automatic catalog resolution: automatically creates new `Customer` or `Product` records on-the-fly when unfamiliar codes are encountered.

### 3. Business Intelligence & Analytics Engine
- **Executive KPIs**: Real-time totals for Gross Revenue, Cost, Profit, Gross Profit Margin %, Units Sold, Order Count, and Average Order Value (AOV).
- **Product Rankings**: Top products by revenue, volume, or profit contribution.
- **Regional Intelligence**: Territorial sales performance, margins, and global revenue contribution percentages.
- **Growth Analysis**:
  - **Month-over-Month (MoM)** percentage growth calculated via Pandas vector operations.
  - **Year-over-Year (YoY)** multi-year trend analysis.
- **Statistical Distributions**: Transaction value percentiles (25th, 75th), IQR, standard deviation, mean, and median computed via NumPy.

### 4. Multi-Sheet Corporate Reports
- **Formatted Multi-Tab Excel Workbook**:
  - Sheet 1: *Executive Summary* (KPI scorecards)
  - Sheet 2: *Monthly Trends* (MoM % growth rates)
  - Sheet 3: *Regional Performance*
  - Sheet 4: *Top Products*
  - Sheet 5: *Detailed Transactions*
- **Streaming CSV Export**: Fast, memory-efficient streaming download.

---

## 📁 Project Directory Structure

```
Runshaw/
├── app/
│   ├── __init__.py                 # Application Factory (create_app)
│   ├── config.py                   # Multi-environment configs (Dev, Test, Prod)
│   ├── extensions.py               # db, jwt, cors instances
│   ├── models/                     # SQLAlchemy relational models
│   │   ├── __init__.py
│   │   ├── user.py                 # User & password hashing
│   │   ├── customer.py             # Customer master
│   │   ├── product.py              # Product catalog & pricing
│   │   └── sale.py                 # Sales records, financial metrics, indexes
│   ├── schemas/                    # Marshmallow validation schemas
│   │   ├── __init__.py
│   │   ├── auth_schema.py
│   │   ├── customer_schema.py
│   │   ├── product_schema.py
│   │   └── sale_schema.py
│   ├── services/                   # Business & data logic
│   │   ├── __init__.py
│   │   ├── data_processor.py       # Pandas/NumPy cleaning, deduplication, stats
│   │   ├── analytics_service.py    # SQL aggregates, MoM/YoY growth
│   │   └── report_service.py       # Openpyxl multi-tab Excel & CSV builder
│   ├── utils/                      # Utilities & helpers
│   │   ├── __init__.py
│   │   ├── decorators.py           # @role_required, @validate_payload
│   │   ├── exceptions.py           # Custom APIException hierarchy
│   │   ├── error_handlers.py       # Centralized JSON error responses
│   │   ├── logger.py               # Rotating file & console logging
│   │   └── pagination.py           # Standardized pagination helper
│   └── api/                        # REST Controllers (Blueprints)
│       ├── __init__.py
│       ├── auth.py                 # /api/v1/auth
│       ├── sales.py                # /api/v1/sales
│       ├── analytics.py            # /api/v1/analytics
│       ├── reports.py              # /api/v1/reports
│       ├── customers.py            # /api/v1/customers
│       └── products.py             # /api/v1/products
├── data/
│   ├── sample_sales.csv            # Sample dataset for upload testing
│   └── sample_sales.xlsx           # Sample Excel dataset for upload testing
├── docs/
│   ├── api_reference.md            # Detailed API documentation with curl commands
│   └── openapi.json                # OpenAPI 3.0 specification
├── scripts/
│   ├── seed_db.py                  # Database seeder with sample multi-year data
│   └── generate_sample_data.py     # Generator for sample CSV & Excel files
├── tests/                          # Automated Pytest suite
│   ├── conftest.py                 # In-memory test db & JWT fixtures
│   ├── test_auth.py
│   ├── test_sales.py
│   ├── test_upload.py
│   ├── test_analytics.py
│   └── test_reports.py
├── .env.example                    # Environment variable template
├── .gitignore
├── requirements.txt                # Pinned dependencies
├── Dockerfile                      # Production container configuration
├── render.yaml                     # Render Infrastructure as Code blueprint
├── README.md                       # Main documentation
└── run.py                          # WSGI Application entry point
```

---

## 🛠️ Getting Started (Local Setup)

### 1. Clone & Set Up Virtual Environment

```bash
# Clone the repository
git clone https://github.com/your-username/sales-analytics-bi-api.git
cd sales-analytics-bi-api

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default SQLite database is used out of the box (`sales_bi.db`). To use local PostgreSQL, update `DATABASE_URL` in `.env`:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/sales_analytics_db
```

### 3. Initialize & Seed Database

Run the database seeder to create tables, default users, products, customers, and 200+ historical multi-year transactions:
```bash
python scripts/seed_db.py
```

#### Default Seed Accounts:
| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@company.com` | `AdminPass123!` | Full CRUD, Bulk Upload, Deletion |
| **Analyst** | `analyst@company.com` | `AnalystPass123!` | Analytics, Reports, Upload |
| **User** | `user@company.com` | `UserPass123!` | Standard Sales Queries |

### 4. Run Development Server

```bash
python run.py
```
The API will be available at: `http://127.0.0.1:5000`

---

## 🧪 Running Automated Tests

Run the complete test suite with verbose output:
```bash
pytest -v tests/
```
Output:
```
tests/test_analytics.py::test_executive_kpis PASSED                      [  5%]
tests/test_analytics.py::test_top_products PASSED                        [ 10%]
tests/test_analytics.py::test_regional_breakdown PASSED                  [ 15%]
tests/test_analytics.py::test_monthly_growth_trends PASSED               [ 20%]
tests/test_analytics.py::test_summary_statistics PASSED                  [ 25%]
tests/test_auth.py::test_register_success PASSED                         [ 30%]
tests/test_auth.py::test_register_duplicate_email PASSED                 [ 35%]
tests/test_auth.py::test_login_success PASSED                            [ 40%]
tests/test_auth.py::test_login_invalid_password PASSED                   [ 45%]
tests/test_auth.py::test_get_current_user PASSED                         [ 50%]
tests/test_auth.py::test_get_current_user_unauthorized PASSED            [ 55%]
tests/test_reports.py::test_export_csv PASSED                            [ 60%]
tests/test_reports.py::test_export_excel_workbook PASSED                 [ 65%]
tests/test_sales.py::test_create_sale PASSED                             [ 70%]
tests/test_sales.py::test_get_sale_by_id PASSED                          [ 75%]
tests/test_sales.py::test_update_sale PASSED                             [ 80%]
tests/test_sales.py::test_delete_sale_rbac PASSED                        [ 85%]
tests/test_upload.py::test_upload_csv_dataset PASSED                     [ 90%]
tests/test_upload.py::test_upload_excel_dataset PASSED                   [ 95%]
tests/test_upload.py::test_upload_missing_file PASSED                    [100%]

======================== 20 passed in 5.18s ========================
```

---

## 📖 API Documentation & Quick Examples

For full API specifications, see [docs/api_reference.md](docs/api_reference.md) or open [docs/openapi.json](docs/openapi.json) in Swagger UI.

### 1. Authenticate (Login)
```bash
curl -X POST http://127.0.0.1:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@company.com", "password": "AdminPass123!"}'
```

### 2. Get Executive KPI Summary
```bash
curl -X GET "http://127.0.0.1:5000/api/v1/analytics/summary" \
  -H "Authorization: Bearer <access_token>"
```

### 3. Ingest Bulk Sales Dataset (CSV or Excel)
```bash
curl -X POST http://127.0.0.1:5000/api/v1/sales/upload \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@data/sample_sales.csv"
```

### 4. Download Formatted Multi-Sheet Excel BI Report
```bash
curl -X GET http://127.0.0.1:5000/api/v1/reports/export/excel \
  -H "Authorization: Bearer <access_token>" \
  -o monthly_bi_report.xlsx
```

---

## ☁️ Deployment Instructions for Render

You can deploy this application on [Render](https://render.com) using either the **Automated Blueprint** or **Manual Dashboard Setup**.

### Method A: Automated Deployment via `render.yaml` (Recommended)

1. Push your repository to **GitHub**.
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** and select **Blueprint**.
4. Connect your GitHub repository.
5. Render reads `render.yaml` and will automatically provision:
   - A **Managed PostgreSQL Database** (`sales-analytics-db`).
   - A **Web Service** (`sales-analytics-api`) with Gunicorn WSGI.
   - Secure auto-generated `SECRET_KEY` and `JWT_SECRET_KEY`.
   - Automatic execution of `pip install -r requirements.txt` and `python scripts/seed_db.py`.
6. Click **Apply**. Once built, your API is live with a public HTTPS URL!

---

### Method B: Manual Dashboard Deployment

#### Step 1: Create a PostgreSQL Database on Render
1. Go to Render Dashboard -> **New +** -> **PostgreSQL**.
2. Set Name: `sales-analytics-db`.
3. Set Database Name: `sales_bi`.
4. Select the **Free** instance plan.
5. Click **Create Database**.
6. Once provisioned, copy the **Internal Database URL** (e.g. `postgres://sales_admin:...@dpg-xxx/sales_bi`).

#### Step 2: Create Web Service
1. Click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Configure the following:
   - **Name**: `sales-analytics-api`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python scripts/seed_db.py`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT run:app --workers 2 --threads 4 --timeout 120`
4. Add the following **Environment Variables**:
   | Key | Value |
   | :--- | :--- |
   | `FLASK_ENV` | `production` |
   | `DATABASE_URL` | *(Paste Internal Database URL from Step 1)* |
   | `SECRET_KEY` | *(A long random 32+ character string)* |
   | `JWT_SECRET_KEY` | *(A long random 32+ character string)* |
   | `JWT_ACCESS_TOKEN_EXPIRES_MINUTES` | `120` |
   | `JWT_REFRESH_TOKEN_EXPIRES_DAYS` | `30` |
   | `LOG_LEVEL` | `INFO` |
5. Click **Create Web Service**.

---

## 🔒 Security Best Practices Implemented
- **Password Hashing**: PBKDF2 with SHA-256 via Werkzeug Security.
- **JWT Protection**: RFC 7518 compliant secret keys with short-lived access tokens and token refresh rotation.
- **RBAC**: Multi-tiered role enforcement preventing unauthorized data manipulation.
- **Centralized Error Handling**: Prevents internal stack traces from leaking to client responses in production.
- **SQL Injection Prevention**: 100% parameterized SQLAlchemy queries.

---

## 📄 License
This project is open-source and licensed under the MIT License.
