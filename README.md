***

# QuantFlow-Inventory-System

## 🚀 Project Overview
QuantFlow-Inventory-System is a Flask web application for inventory management featuring secure user authentication, email notifications, and Supabase cloud database integration. The app streamlines item management and bulk imports, improves reliability with duplicate detection, and enhances user feedback through flash messages.

## ✨ Features

### 🔐 Authentication & Security
- User signup, login, and logout powered by Supabase Auth (JWT tokens).
- Password hashing with Werkzeug and secure session management.
- Input validation and email sanitization throughout user flows.

### 📦 Inventory Management
- Add, edit, and delete items linked to individual users.
- Duplicate detection via fuzzy string matching (difflib).
- Timestamped item entries to track item history.

### 📂 File Uploads & Data Handling
- Upload CSV/Excel files for bulk inventory import.
- Automatic column detection even if file headers differ.
- Thorough row validation and error feedback.
- Staging area to review imports, handle duplicates (option to update or replace).

### 📧 Contact & Notifications
- In-app contact form saves user messages to Supabase.
- Email alerts sent via Flask-Mail (Gmail SMTP).
- Flash messages for instant success and error feedback.

### 🛡️ Security
- Dynamic secret key generation (`secrets.token_hex`).
- Robust error handling for all DB and email operations.
- User data isolation: each account only sees its own inventory.

### 🎨 User Experience
- Clean dashboard UI built with Bootstrap templates.
- Flash alerts for critical actions (add/update/delete/upload).
- Session-based workflows for seamless navigation.

## ⚙️ Tech Stack

| Layer      | Technology                           |
|------------|--------------------------------------|
| **Backend**   | Flask (Python)                      |
| **Database & Auth** | Supabase (PostgreSQL + Auth)         |
| **File Handling**   | Pandas, OpenPyXL                    |
| **Email Service**   | Flask-Mail (SMTP)                   |
| **Frontend**   | Jinja2 (templates), Bootstrap        |
| **Security**   | Werkzeug, secrets, input validation   |



***
