# 🚀 DRF Role-Based User & Task Management API

This project is a Django REST Framework-based role-based task manager. It supports JWT authentication, has role-based permissions (Admin, Manager, User), and allows Managers to assign tasks with deadlines. If users miss 5 tasks, they are automatically deactivated using a scheduled cron job, and managers are notified via email.

---

## 📦 Features

- 🔐 Authentication: JWT Authentication (Login, Logout)
- 👤 User Registration with Roles (admin, manager, user)
- 🧑‍💼 Role-based permissions
- 📝 Task assignment and status update
- 📄 Custom API responses with error handling


## ✅ Task Management Features

- Managers and Admins can **assign tasks** to users with deadlines.
- Users can **view their assigned tasks**.
- Users (and Admins) can **update the status** of their tasks.
- Admins and Managers can see **all tasks** in the system.
- Notify Managers if a **user misses a deadline**.
- Automatically **deactivate users** who miss 5 tasks.
- Managers can **reactivate deactivated users**.

---

## 📁 Project Structure

---

## Installation
To get started with this project, follow the steps below to set up your environment.

## Requirements
```
Python 3.x
Django==5.2
psycopg2-binary==2.9.9
djangorestframework==3.16.0
djangorestframework_simplejwt==5.5.0
```


## ⚙️ Setup Instructions

```
# Clone the project
git clone git@github.com:hiteshsakrodiya5/user-management-syatem.git
cd cd user-management-syatem
git checkout stage

# Create virtual environment & activate
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run the development server
python manage.py runserver

# Run Notification & Auto-Deactivation System
python manage.py check_overdue_tasks
```
## DATABASE Configration

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

Then for development/testing purpose i have used sqlit:

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```
## Email Configration
```
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

## JWT Configration
```
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_BLACKLIST_ENABLED": True,
}


```


## 🔐 Authentication Flow (JWT)
```
This app uses **JWT (JSON Web Tokens)** for authentication via the `djangorestframework-simplejwt` package.  
After login, you receive an **access** and **refresh** token pair.

Login: /login/
Returns access and refresh tokens.

Logout: /logout/
Blacklists the refresh token.

Register: /register/
Registers a new user with a default role of "user".
```
## 📡 API Endpoints

```
👥 User APIs

| **Method** | **Endpoint**               | **Description**                    |
|------------|----------------------------|------------------------------------|
| POST       | `/register/`               | Register a new user                |
| POST       | `/login/`                  | Login and get tokens               |
| POST       | `/logout/`                 | Logout and blacklist token         |
| GET        | `/fetchUsers/`             | List all users (Manager/Admin)     |
| GET        | `/getUser/<id>/`           | Get user detail                    |
| PUT        | `/updateUser/<id>/`        | Update user (Manager/Admin)        |
| DELETE     | `/deleteUser/?pk=<id>`     | Delete user (Manager/Admin)        |

---


### ✅ Task APIs

| **Method** | **Endpoint**               | **Description**                          |
|------------|----------------------------|------------------------------------------|
| POST       | `/assign/`                 | Assign task (Manager/Admin)              |
| GET        | `/fetchTask/`              | Get tasks (based on role)                |
| PUT        | `/updateStatus/<id>/`      | Update task status (User/Admin)          |

```
## 🧑‍💼 Permissions & Role Management

```
The application implements custom **role-based access control (RBAC)**:

| **Role**   | **Permissions**                                                                 |
|------------|---------------------------------------------------------------------------------|
| Admin      | Full access to all features, including user and task management                 |
| Manager    | Can create/update/delete non-admin users, assign tasks, view all users/tasks    |
| User       | Can only view/update their own tasks                                            |

- Custom permission classes: `IsManagerOrAdmin`, `IsUserOrAdmin`
- These are applied to API views for strict access control
