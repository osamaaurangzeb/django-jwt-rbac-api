# Django JWT Role-Based Access Control API (RBAC) 🔐

A secure and extensible Django REST API for managing users with **JWT authentication**, **custom user roles**, and **role-based access control** — currently **under development**.

---

## ✅ Project Status: Completed

This project has been fully developed and tested. All major features have been implemented successfully:

- ✅ **Custom login system** using email & password (via JWT)
- ✅  **Editor post creation** + **admin approval workflow**
- ✅  **Users can view only approved posts**
- ✅ Role-based route protection via middleware (`admin`, `editor`, `user`)
- ✅ Fully integrated Swagger and ReDoc API documentation
- 🧪 Unit + integration tests for authentication and role validation

---

## ✨ Key Features

- 🧑‍💼 Admin can:
  - View all user profiles
  - Create `editor` or `user` roles
  - Approve or reject editor-submitted posts
  - View system stats (dashboard)

- ✍️ Editor can:
  - Login via email/password
  - Submit content (text posts)
  - View own profile

- 👤 User can:
  - Self-register
  - Login and access own profile
  - View **only approved posts**

- 🔐 JWT-based authentication using `djangorestframework-simplejwt`
- ⚙️ Role access enforced via:
  - DRF permissions
  - Custom middleware
- 📜 API documentation with Swagger (`drf-yasg`)
- 🐳 Dockerized setup + Postgres-ready

---

## 🧪 Installation & Setup

```bash
# Clone the repository
git clone https://github.com/osamaaurangzeb/django-jwt-rbac-api.git
cd django-jwt-rbac

# Setup virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create demo data (admin/editor/user)
python manage.py create_demo_data

# Start server
python manage.py runserver
