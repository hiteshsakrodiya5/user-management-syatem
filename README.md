# 🚀 Django Role-Based Task Management System

A secure web application built with Django REST Framework implementing:

- User CRUD operations with role-based access (Admin, Manager, User)
- JWT Authentication (with Refresh Token)
- Task assignment by Managers
- Automatic notification for missed deadlines
- Auto-deactivation of users after 5 missed tasks
- Reactivation feature for Managers
- Cron-based periodic check for overdue tasks

---

## ⚙️ Tech Stack

- **Backend**: Python, Django, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (with Refresh Tokens)
- **Task Scheduling**: Cron Jobs
- **Email Notification**: Django `send_mail` method

---

## 🏁 Setup Instructions

### 1. Clone the Repository
git clone git@github.com:hiteshsakrodiya5/user-management-syatem.git

### 2. Create Virtual Environment & Install Dependencies
python -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt


### 3. Setup PostgreSQL Database (For testing purpose I did with sqlite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

Then Run:
python manage.py makemigrations

python manage.py migrate

I have also created a django custom command for run automation task like 
- Missed deadlines
- Auto-deactivates users after 5 missed tasks
- Sends email to manager for each missed task

Use the command to run those task by:

- python manage.py check_overdue_tasks

```