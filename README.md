# Piexlinsta

Piexlinsta is a social media application built with Django that allows users to share posts, stories, follow each other, and send direct messages.

## Prerequisites

Since you do not have experience with Python or Django, this guide will walk you through setting everything up from scratch on Windows.

1. **Install Python**: 
   - Download Python from the official website: https://www.python.org/downloads/
   - Run the installer. **CRITICAL STEP: Check the box that says "Add Python.exe to PATH"** at the bottom of the installer before clicking "Install Now".

2. **Install MySQL (or MariaDB)**:
   - This project uses a MySQL database. You can install an easy-to-use package like XAMPP, which includes a MySQL database server.
   - Download XAMPP: https://www.apachefriends.org/index.html
   - Run the installer. Start the "MySQL" module from the XAMPP Control Panel once installed.

## Setup Instructions

Once Python and MySQL are installed, follow these steps:

### 1. Set up the Database

1. Open your XAMPP Control Panel and ensure MySQL is running.
2. Click the "Admin" button next to MySQL to open phpMyAdmin in your browser.
3. Click on "Databases" at the top.
4. Under "Create database", enter `pixelinsta` and click "Create".
5. Next, create a user account for the database (or if you are just testing locally, the settings are currently configured to look for the user `root` with the password `kali@2005`. You will either need to create this user in MySQL OR change the database credentials in the code).

**Updating the credentials in the code to match your setup:**
Open the file `pixelinstapro/pixelinstapro/settings.py` with a text editor (like Notepad). Scroll down to the `DATABASES` section (around line ~80) and change the `USER` and `PASSWORD` to match your local MySQL setup (e.g., if you use XAMPP, the default user is `root` and the password is `""` (empty string)).

### 2. Install Project Dependencies

1. Open a terminal or Command Prompt. You can do this by pressing `Win` + `R`, typing `cmd`, and pressing Enter.
2. Navigate to the folder where this project is located using the `cd` command. For example:
   ```cmd
   cd C:\Users\YourUsername\Downloads\pixelinsta\pixelinstapro
   ```
   *(Note: You need to be in the folder that contains `manage.py`)*
3. Install the required Python packages by running:
   ```cmd
   pip install django mysqlclient pillow
   ```
   *(Note: `mysqlclient` can sometimes be tricky to install on Windows. If it fails, you may need to install the Microsoft Visual C++ Build Tools or you can use `PyMySQL` instead and modify the settings slightly).*

### 3. Set up the Database Tables

Now we need to create the tables in your MySQL database so the app can store data.

1. In the same Command Prompt window (ensure you are still in the folder with `manage.py`), run:
   ```cmd
   python manage.py makemigrations
   ```
2. Then run:
   ```cmd
   python manage.py migrate
   ```

### 4. Run the Application!

1. Finally, start the local development server:
   ```cmd
   python manage.py runserver
   ```
2. Open your web browser and go to: `http://127.0.0.1:8000/`

You should now see the Piexlinsta application running! You can create a new account to get started.
