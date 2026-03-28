# 🍜 FoodCourt Grand Galaxy — Multi-Tenant POS Kiosk

A modern, elegant self-service POS kiosk application for multi-tenant food courts, built with Django, Tailwind CSS, and HTMX.

## ✨ Features

- **10 Tenants** with individual menus (100+ dishes total)
- **7 Beautiful Landing Page Themes** — switchable at runtime
- **Real-time Cart** powered by HTMX (no page reload)
- **Checkout Flow** with table selection & multiple payment options
- **Digital Receipt** — printable & shareable
- **Django Admin** for full menu/tenant management

## 🎨 Themes

| # | Theme | Style |
|---|-------|-------|
| ⭐ | **Yogya Brand** *(default)* | Warm orange-yellow, family-friendly |
| 🌌 | **Aurora Borealis** | Deep space dark, glassmorphism, living aurora gradient |
| 💻 | **Neon Cyberpunk** | Dark futuristic, cyan-magenta glow |
| 👑 | **Warm Luxury** | Gold shimmer on dark premium background |
| 🌿 | **Fresh Modern** | Clean white, bento grid layout |
| 🌸 | **Retro Japanese** | Warm cream-red, horizontal cards |
| 🏮 | **Night Market** | Dark amber, lantern sway, street-food vibe |

## 🏪 Tenants

| Stall | Name | Cuisine | Rating |
|-------|------|---------|--------|
| A01 | 🍜 Ramen Sanpachi | Japanese | ⭐ 4.8 |
| A02 | 🥩 Korean House | Korean | ⭐ 4.7 |
| B01 | 🍕 Pizza Bella | Italian | ⭐ 4.6 |
| B02 | 🍛 Rumah Padang | Indonesian | ⭐ 4.9 |
| C01 | 🍔 Burger Bros | American | ⭐ 4.7 |
| C02 | 🌶️ Thai Orchid | Thai | ⭐ 4.6 |
| D01 | 🥟 Dim Sum Palace | Chinese | ⭐ 4.8 |
| D02 | 🧋 Boba Paradise | Beverage | ⭐ 4.5 |
| E01 | 🌮 Taco Fiesta | Mexican | ⭐ 4.4 |
| E02 | 🍨 Sweet Moments | Dessert | ⭐ 4.9 |

## 🛠 Tech Stack

- **Backend**: Django 6 + django-htmx
- **Frontend**: Tailwind CSS (CDN) + HTMX
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Media**: Pillow for image handling
- **Static**: Whitenoise

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/dadinjaenudin/foodcourt-pos-kiosk.git
cd foodcourt-pos-kiosk

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Seed sample data
python manage.py seed_data

# 6. Create superuser
python manage.py createsuperuser

# 7. Run dev server
python manage.py runserver
```

Visit: http://localhost:8000

Admin panel: http://localhost:8000/admin (default: admin / admin123)

## 💳 Payment Options

- Cash
- Credit/Debit Card
- QRIS
- GoPay
- OVO
- DANA

## 📱 Pages

| URL | Description |
|-----|-------------|
| `/` | Landing page (theme picker + tenant grid) |
| `/tenant/<slug>/` | Tenant detail + menu ordering |
| `/cart/` | Cart HTMX partial |
| `/checkout/` | Checkout modal |
| `/order-success/<id>/` | Order confirmation |
| `/receipt/<id>/` | Printable digital receipt |
| `/admin/` | Django admin panel |

## 🎨 Theme Switching

Themes are stored in `localStorage` — customers can switch freely. The theme switcher button `🎨 Ganti Tema` appears on the bottom-left corner of the landing page.

## 📂 Project Structure

```
foodcourt-pos-kiosk/
├── foodcourt_pos/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── pos/                    # Main app
│   ├── models.py           # Tenant, Product, Order, OrderItem
│   ├── views.py            # All views
│   ├── urls.py
│   ├── admin.py
│   └── management/
│       └── commands/
│           └── seed_data.py   # Sample data seeder
├── templates/
│   └── pos/
│       ├── base.html          # Base template (nav, cart, CSS)
│       ├── home.html          # Landing page (7 themes)
│       ├── tenant_detail.html # Menu page
│       ├── order_success.html # Success page
│       ├── receipt.html       # Digital receipt
│       └── partials/
│           └── product_grid.html
├── requirements.txt
└── manage.py
```

## 📄 License

MIT License — free to use and modify.

---

Built with ❤️ using Django + Tailwind CSS + HTMX
