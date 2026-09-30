
# Farm ERP

Django-based poultry farm ERP for tracking flocks, feed, drugs, stock, sales, costs and margins.

Built for real farm operations: multi-role access (pen workers, store keepers, supervisors, managers, sales, accounts) with structured recording of placements, daily events, inventory movements and commercial activity.

## Features

- **Farm structure** – Farm units, pens, worker roles and assignments
- **Flock management** – Layers and broilers; placement, current count, close-out
- **Feed** – Procurement, delivery, stock balance, issuance, reorder thresholds
- **Drugs & supplements** – Stock, movements, treatments
- **Daily / operational logging** – Mortality, egg production, weight and related events
- **Sales & shop** – Customers, products, sales, deliveries
- **Suppliers & payments** – Feed and other supply tracking with payment records
- **Cost awareness** – Unit costs, stock balances and margin-oriented data model
- **Role-based access** – Pen worker, store keeper, supervisor, manager, salesperson, accountant, director

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | Django 6 |
| Database | SQLite (dev) / PostgreSQL (production via `dj-database-url`) |
| Forms | django-crispy-forms + Bootstrap 5 |
| Static | WhiteNoise |
| Server | Gunicorn |
| Deploy | Procfile-ready |

## Project Structure

```text
farm_erp/
├── manage.py
├── requirements.txt
├── Procfile
├── farm_erp/          # project config (settings, urls, wsgi, asgi)
├── core/              # main application
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── admin.py
│   ├── signals.py
│   ├── permissions.py
│   ├── urls.py
│   └── templates/
└── staticfiles/

```

## Core data model (high level)

- **FarmUnit → Pen → Flock** (layer / broiler)
- **Worker** + role + pen assignments
- **Supplier** (feed, birds, drugs, mixed)
- **Feed**: procurement → delivery → stock → movements (in/out)
- **Drugs & supplements**: catalogue + stock movements
- **Operational events**: mortality, production, weight, treatments
- **Shop / sales**: customers, products, sales, deliveries

Stock balances and key cost fields are maintained so unit costs, inventory and margins can be derived from operational data.

## Design principles

- Reflect real farm workflows (placement → daily events → stock → sales)
- Strong referential integrity (`PROTECT` on critical FKs)
- Clear separation of operational recording vs commercial (shop) activity
- Role-aware permissions for different staff types
- Data structured for cost and performance analysis, not only data entry

## Status

Active development under Assista Tech Concepts.

---

**Role:** Design & implementation lead (data model, workflows, cost/stock logic)
