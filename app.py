from flask import Flask, render_template, request, redirect, url_for, flash, session
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import secrets
import re


secret_key = secrets.token_hex(32)  # 64 hex chars = 256 bits random


app = Flask(__name__)
app.secret_key = secret_key  # Needed for flash messages and sessions


supabase_url = "https://rdvwutmjprwxsmqojyfr.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJkdnd1dG1qcHJ3eHNtcW9qeWZyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU3NzgxMzgsImV4cCI6MjA3MTM1NDEzOH0.cKao31BA_cch-fMQMFe7smyrwIkZ4WES8HkCREixPnc"


# Note: supabase client without auth token for public requests
supabase: Client = create_client(supabase_url, supabase_key)


# global INVENTORY not required since now inventory is created dynamically
INVENTORY = []  # This is left empty initially, and items are added through the add_item route.


# Helper function to create supabase client with current user's access token
def get_supabase_client():
    # Supabase Python client currently does NOT support passing headers,
    # so just return the global client (service key)
    return supabase


def sanitize_email(email):
    return re.sub(r'\W+', '_', email)
# contains only alphanumeric and underscores


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/inventory')
def inventory():
    # Protect inventory so only logged-in users can access
    if not session.get('user_email'):
        flash("Please log in to view your inventory.")
        return redirect(url_for('login'))
    user_email = session['user_email']
    supabase_user = get_supabase_client()
    try:
        # Query from single shared table filtering by user_email (simulate RLS)
        response = supabase_user.table('user_inventory').select("*").eq('user_email', user_email).execute()
        inventory = response.data or []
    except Exception as e:
        inventory = []
        flash("Error loading inventory: " + str(e))
    return render_template('inventory.html', inventory=inventory)


@app.route('/add-item', methods=['GET', 'POST'])
def add_item():
    if not session.get('user_email'):
        flash("Please log in to add items.")
        return redirect(url_for('login'))
    user_email = session['user_email']
    supabase_user = get_supabase_client()
    if request.method == 'POST':
        names = request.form.getlist('name[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')
        for name, qty, price in zip(names, quantities, prices):
            if not name.strip():
                continue
            try:
                quantity = int(qty)
                price_val = float(price)
            except ValueError:
                continue
            data = {
                "user_email": user_email,
                "name": name.strip(),
                "quantity": quantity,
                "price": price_val,
                "created_at": datetime.datetime.utcnow().isoformat()
            }


            # inserting data into shared user_inventory table using service key client
            try:
                supabase_user.table('user_inventory').insert(data).execute()
            except Exception as e:
                flash("Error adding item: " + str(e))
        return redirect(url_for('inventory'))
    else:
        return render_template('add_item.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for('signup'))


        existing_user = supabase.table('user_details').select("*").eq('email_id', email).execute()
        if existing_user.data:
            flash("Email already registered. Please login.")
            return redirect(url_for('login'))


        # Sign up user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })


        # Check for errors safely
        if getattr(auth_response, "status_code", 200) >= 400 or not getattr(auth_response, "user", None):
            try:
                error_json = auth_response.json()
                error_message = error_json.get('error_description') or error_json.get('message') or 'Signup failed'
            except Exception:
                error_message = 'Signup failed'
            flash("Error signing up: " + error_message)
            return redirect(url_for('signup'))


        hashed_password = generate_password_hash(password)
        data = {
            "name": name,
            "email_id": email,
            "password": hashed_password,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        supabase.table('user_details').insert(data).execute()


        # Removed per-user inventory table creation (no longer needed with shared table)


        flash("Signup successful! Please login.")
        return render_template('signup.html', show_login_link=True)
    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']


        # Authenticate using Supabase Auth for proper JWT token
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})


        # Check for errors safely
        if getattr(response, "status_code", 200) >= 400 or not getattr(response, "user", None):
            flash("Incorrect email or password.")
            return redirect(url_for('login'))


        user = response.user
        access_token = response.session.access_token if response.session else None


        if not user or not access_token:
            flash("Login failed. Please try again.")
            return redirect(url_for('login'))


        # Save email and JWT token in session for auth requests
        flash("Login successful!")
        session['user_email'] = user.email


        user_name = "User"
        if hasattr(user, "user_metadata") and user.user_metadata is not None:
            if isinstance(user.user_metadata, dict):
                user_name = user.user_metadata.get("full_name", "User")
            else:
                user_name = getattr(user.user_metadata, "full_name", "User")
        session['user_name'] = user_name


        session['access_token'] = access_token


        return redirect(url_for('inventory'))


    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_name', None)
    session.pop('access_token', None)
    flash("You have been logged out.")
    return redirect(url_for('home'))


@app.route('/reports')
def reports():
    return render_template('reports.html')


if __name__ == '__main__':
    app.run(debug=True, port=8000)
