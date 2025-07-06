# Django Project Creation Guide

This guide will walk you through creating a Django project from scratch, following the same steps we performed in class. You'll learn how to set up a virtual environment, install Django, create a project, and configure it for development.

## Prerequisites

Before starting, make sure you have:

- **Python 3**: Verify installation by running `python3 --version` in your terminal
- **Terminal/Command Prompt**: Basic familiarity with navigating directories
- **VS Code**: We'll be using VS Code as our code editor

## Step-by-Step Project Creation

### Step 1: Navigate to Your Development Directory

Open your terminal and navigate to where you want to create your Django project:

```bash
cd /path/to/your/development/folder
```

If you have a specific Django directory, navigate to it:

```bash
cd Django/
```

### Step 2: Create a Virtual Environment

Create an isolated Python environment for your Django project:

```bash
python3 -m venv denv
```

This creates a new folder named `denv` (Django environment) containing an isolated Python environment.

### Step 3: Activate the Virtual Environment

Activate the virtual environment:

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

**Confirmation:** Your terminal prompt should now show `(denv)` at the beginning.

### Step 4: Install Django

With the virtual environment activated, install Django:

```bash
pip install django
```

This installs the latest version of Django and all its dependencies.

### Step 5: Create Django Project

Create a new Django project called `todo_project`:

```bash
django-admin startproject todo_project
```

This creates a new directory with the basic Django project structure.

### Step 6: Navigate to Project Directory

Move into your newly created project directory:

```bash
cd todo_project/
```

### Step 7: Create Django App

Create a new Django app called `tasks`:

```bash
python3 manage.py startapp tasks
```

This creates a new directory called `tasks` with the basic app structure.

### Step 8: Apply Initial Database Migrations

Run the initial database migrations to set up Django's built-in tables:

```bash
python3 manage.py migrate
```

This creates the SQLite database file and sets up the necessary tables for Django's admin interface and user management.

### Step 9: Create Superuser

Create an admin user to access Django's admin interface:

```bash
python3 manage.py createsuperuser
```

You'll be prompted to enter:
- Username (press Enter for default or type your preferred username)
- Email address (optional, can be left blank)
- Password (type a secure password)
- Password confirmation

### Step 10: Configure VS Code

1. Open your Django project folder in VS Code
2. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
3. Type "Python: Select Interpreter" and select it
4. Choose the interpreter pointing to your virtual environment:
   ```
   /path/to/your/project/denv/bin/python
   ```
5. Restart VS Code completely to ensure all changes take effect

## Running Your Django Project

### Start the Development Server

1. **Ensure virtual environment is active** (you should see `(denv)` in your terminal)

2. **Navigate to your project directory** (where `manage.py` is located):
   ```bash
   cd todo_project/
   ```

3. **Start the development server:**
   ```bash
   python3 manage.py runserver
   ```

4. **Access your application:**
   - Open your web browser
   - Navigate to `http://127.0.0.1:8000`
   - You should see the Django welcome page!

5. **Access the admin interface:**
   - Navigate to `http://127.0.0.1:8000/admin`
   - Log in with the superuser credentials you created

## Project Structure

After following these steps, your project structure should look like this:

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

## Common Django Commands

### Development Commands

**Start development server:**
```bash
python3 manage.py runserver
```

**Start server on different port:**
```bash
python3 manage.py runserver 8080
```

**Stop the server:**
Press `Ctrl + C` in the terminal

### Database Commands

**Create new migrations:**
```bash
python3 manage.py makemigrations
```

**Apply migrations:**
```bash
python3 manage.py migrate
```

**Create superuser:**
```bash
python3 manage.py createsuperuser
```

### App Management

**Create new app:**
```bash
python3 manage.p