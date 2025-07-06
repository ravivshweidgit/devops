# Complete Django Project Guide - From Scratch to Running

This guide will walk you through creating a Django project from scratch and getting it running in your browser, following the exact steps we performed in class.

## Prerequisites

- **Python 3**: Verify with `python3 --version`
- **Terminal/Command Prompt**: Basic navigation skills
- **VS Code**: Code editor for development
- **Web Browser**: To view your Django application

## Step-by-Step Guide

### Step 1: Navigate to Your Development Directory

Open your terminal and navigate to your development folder:

```bash
cd /path/to/your/development/folder
```

If you have a Django directory:
```bash
cd Django/
```

### Step 2: Create Virtual Environment

Create an isolated Python environment:

```bash
python3 -m venv denv
```

### Step 3: Activate Virtual Environment

**macOS/Linux:**
```bash
source denv/bin/activate
```

**Windows (Command Prompt):**
```cmd
denv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
.\denv\Scripts\Activate.ps1
```

**Confirmation:** You should see `(denv)` at the beginning of your terminal prompt.

### Step 4: Install Django

Install Django with pip:

```bash
pip install django
```

### Step 5: Create Django Project

Create a new Django project:

```bash
django-admin startproject todo_project
```

### Step 6: Navigate to Project Directory

Move into your project folder:

```bash
cd todo_project/
```

### Step 7: Create Django App

Create a new app within your project:

```bash
python3 manage.py startapp tasks
```

### Step 8: Apply Initial Migrations

Set up the database with Django's built-in tables:

```bash
python3 manage.py migrate
```

### Step 9: Create Superuser

Create an admin user for the Django admin interface:

```bash
python3 manage.py createsuperuser
```

Enter the following when prompted:
- **Username**: (press Enter for default or type your preferred username)
- **Email**: (optional, can be left blank)
- **Password**: (type a secure password)
- **Password confirmation**: (retype the same password)

### Step 10: Start the Development Server

Run the Django development server:

```bash
python3 manage.py runserver
```

You should see output like:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
January 06, 2025 - 10:30:45
Django version 4.2.x, using settings 'todo_project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Step 11: Open in Browser

Open your web browser and visit:

**Main Django Welcome Page:**
```
http://127.0.0.1:8000/
```
or
```
http://localhost:8000/
```

You should see the Django welcome page with a rocket ship!

**Django Admin Interface:**
```
http://127.0.0.1:8000/admin/
```

Log in with the superuser credentials you created in Step 9.

## Complete Command Summary

Here's the complete sequence of commands to copy and paste:

```bash
# Navigate to your development directory
cd /path/to/your/development/folder

# Create virtual environment
python3 -m venv denv

# Activate virtual environment
source denv/bin/activate  # macOS/Linux
# OR
denv\Scripts\activate     # Windows

# Install Django
pip install django

# Create Django project
django-admin startproject todo_project

# Navigate to project directory
cd todo_project/

# Create Django app
python3 manage.py startapp tasks

# Apply initial migrations
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser

# Start development server
python3 manage.py runserver
```

## Project Structure

After completing these steps, your project structure will look like:

```
your-development-folder/
├── denv/                    # Virtual environment
└── todo_project/           # Django project directory
    ├── manage.py           # Django's command-line utility
    ├── todo_project/       # Main project package
    │   ├── __init__.py
    │   ├── settings.py     # Project settings
    │   ├── urls.py         # URL configuration
    │   ├── wsgi.py         # WSGI configuration
    │   └── asgi.py         # ASGI configuration
    ├── tasks/              # Django app directory
    │   ├── __init__.py
    │   ├── admin.py        # Admin interface configuration
    │   ├── apps.py         # App configuration
    │   ├── models.py       # Database models
    │   ├── tests.py        # Test cases
    │   ├── views.py        # View functions
    │   └── migrations/     # Database migrations
    └── db.sqlite3          # SQLite database file
```

## Server Management

### Starting the Server
```bash
python3 manage.py runserver
```

### Starting on Different Port
```bash
python3 manage.py runserver 8080
```

### Stopping the Server
Press `Ctrl + C` in the terminal where the server is running.

### Restarting the Server
1. Stop with `Ctrl + C`
2. Run `python3 manage.py runserver` again

## Browser Access Points

Once your server is running, you can access:

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/` | Main Django welcome page |
| `http://localhost:8000/` | Alternative main page URL |
| `http://127.0.0.1:8000/admin/` | Django admin interface |

## Important Notes

1. **Keep Terminal Open**: The server runs in your terminal, so keep it open while devel