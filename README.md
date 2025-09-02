# QuantFlow-Inventory-System  

Features

🔐 Authentication & Security

-User signup/login/logout with Supabase Auth (JWT).

-Password hashing & secure session management.

-Input validation & email sanitization.


📦 Inventory Management

-Add, edit, delete items linked to the logged-in user.

-Duplicate detection using fuzzy string matching (difflib).

-Timestamped entries for tracking item history.


📂 File Uploads & Data Handling

-Upload CSV/Excel files to bulk import items.

-Smart automatic column detection (works even if headers differ)

-Handles invalid rows and provides error feedback.

-Staging area (review before saving) with duplicate handling (update vs replace).


📧 Contact & Notifications

-Contact form saves messages in Supabase.

-Sends email alerts via Flask-Mail (Gmail SMTP).

-Flash messages for instant success/error feedback.


🛡️ Security

-Dynamic secret key generation (secrets.token_hex).

-Clean error handling for DB and email operations.

-User isolation – each account only sees their own inventory.


🎨 User Experience

-Clean dashboard with Bootstrap templates.

-Flash alerts for actions (add/update/delete/upload).

-Session-based workflows for smooth navigation.


⚙️ Tech Stack

-Backend: Flask (Python)

-Database & Auth: Supabase (PostgreSQL + Auth)

-File Handling: Pandas, OpenPyXL

-Email Service: Flask-Mail (SMTP)

-Frontend: Jinja2 templates + Bootstrap

-Security: Werkzeug (password hashing), Secrets, Input validation


<img width="944" height="499" alt="image" src="https://github.com/user-attachments/assets/ec8d7960-da2e-4f8f-b0c1-f2f22b70d0ed" />
