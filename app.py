from flask import Flask, render_template, request, redirect, url_for, flash, session
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import secrets


secret_key = secrets.token_hex(32)  # 64 hex chars = 256 bits random


app = Flask(__name__)
app.secret_key = secret_key  # Needed for flash messages and sessions


supabase_url = "https://rdvwutmjprwxsmqojyfr.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJkdnd1dG1qcHJ3eHNtcW9qeWZyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU3NzgxMzgsImV4cCI6MjA3MTM1NDEzOH0.cKao31BA_cch-fMQMFe7smyrwIkZ4WES8HkCREixPnc"
supabase: Client = create_client(supabase_url, supabase_key)


global INVENTORY
INVENTORY = []  # This is left empty initially, and items are added through the add_item route.


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
    return render_template('inventory.html', inventory=INVENTORY)


@app.route('/add-item', methods=['GET', 'POST'])
def add_item():
    if not session.get('user_email'):
        flash("Please log in to add items.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        names = request.form.getlist('name[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')

        for name, qty, price in zip(names, quantities, prices):
            if not name.strip():  # checks if name is not empty
                continue
            try:
                quantity = int(qty)       # checks if quantity is a valid integer
                price_val = float(price)  # checks if price is a valid float
            except ValueError:
                continue

            # checks if item already exists, if not starts id from 1, otherwise continues incrementing
            new_id = INVENTORY[-1]['id'] + 1 if INVENTORY else 1
            INVENTORY.append({'id': new_id, 'name': name.strip(), 'quantity': quantity, 'price': price_val})

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

        # Check if email already exists in user_details table
        existing_user = supabase.table('user_details').select("*").eq('email_id', email).execute()
        if existing_user.data:
            flash("Email already registered. Please login.")
            return redirect(url_for('login'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert new user with created_at timestamp and name
        data = {
            "name": name,
            "email_id": email,
            "password": hashed_password,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        supabase.table('user_details').insert(data).execute()

        flash("Signup successful! Please login.")
        return render_template('signup.html', show_login_link=True)

    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        # Query user from user_details table by email(unique)
        user_response = supabase.table('user_details').select("*").eq('email_id', email).execute()
        user_data = user_response.data

        if not user_data:
            flash("No account found with this email. Please sign up.")
            return redirect(url_for('signup'))

        user = user_data[0]

        # Verify password hash
        if not check_password_hash(user['password'], password):
            flash("Incorrect password. Please try again.")
            return redirect(url_for('login'))

        flash("Login successful!")
        session['user_email'] = email                    # Saves user session
        session['user_name'] = user.get('name', 'User') 
        return redirect(url_for('inventory'))

    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_name', None)
    flash("You have been logged out.")
    return redirect(url_for('home'))


@app.route('/reports')
def reports():
    return render_template('reports.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
