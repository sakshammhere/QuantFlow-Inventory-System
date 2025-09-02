from flask import Flask, render_template, request, redirect, url_for, flash, session
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import secrets
import re
from flask_mail import Mail, Message



secret_key = secrets.token_hex(32)  # 64 hex chars = 256 bits random



app = Flask(__name__)
app.secret_key = secret_key  # Needed for flash messages and sessions



supabase_url = "https://rdvwutmjprwxsmqojyfr.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJkdnd1dG1qcHJ3eHNtcW9qeWZyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU3NzgxMzgsImV4cCI6MjA3MTM1NDEzOH0.cKao31BA_cch-fMQMFe7smyrwIkZ4WES8HkCREixPnc"



# Supabase client without auth token for public requests
supabase: Client = create_client(supabase_url, supabase_key)



app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='guptasaksham0301@gmail.com',
    MAIL_PASSWORD='uxud pqvr brac eqvj'
)
mail = Mail(app)



# global INVENTORY not required since now inventory is created dynamically
INVENTORY = []  # This is left empty initially, and items are added through the add_item route.



# Function to create supabase client with current user's access token
def get_supabase_client():
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





@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject', '')





        message = request.form.get('message')





        if not name or not email or not message:
            flash('Please fill out all required fields.')
            return redirect(request.url)
        
        # email send algo here
        body = f''' New Contact Form Submission
        Name: {name}
        Email: {email}
        Subject: {subject}
        Message: {message}
        '''





        msg = Message(subject=f"Contact Form: {subject}",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=['guptasaksham0301@gmail.com'],
                      body=body)
        
        # Inserting data into Supabase contact_messages table
        try:
            print(f"Inserting contact_message for: {name}, {email}")
            result = supabase.table('contact_messages').insert({
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
                'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat()
            }).execute()





            if hasattr(result, "status_code") and result.status_code >= 400:
                flash(f"Failed to save your message to database: {result.data}")
                print(f"Insert error data: {result.data}")
                return redirect(request.url)
            else:
                print(f"Insert succeeded: {result.data}")
        except Exception as e:
            flash(f"Failed to save your message to database: {str(e)}")
            print(f"DB insert error: {e}")
            return redirect(request.url) 
        
        #try except for mail
        try:
            mail.send(msg)
            flash('Thank you for contacting us! Your message has been sent.')
        except Exception as e:
            flash('Failed to send your message. Please try again later.')
            print(f"Mail sending error: {e}")
        return redirect(request.url)





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
        # Handle duplicates items entered
        action = request.form.get('action')
        duplicate_id = request.form.get('duplicate_id')





        if action and duplicate_id:
            name = request.form.getlist('name[]')[0]
            quantity = request.form.getlist('quantity[]')[0]
            price = request.form.getlist('price[]')[0]
            try:
                quantity = int(quantity)
                price_val = float(price)
            except ValueError:
                flash("Invalid quantity or price.")
                return redirect(url_for('add_item'))
            if action == 'update':
                # Update only quantity and price





                try:
                    supabase_user.table('user_inventory').update({
                        "quantity": quantity,
                        "price": price_val
                    }).eq('id', int(duplicate_id)).eq('user_email', user_email).execute()
                    flash("Item updated successfully!")
                except Exception as e:
                    flash("Error updating item: " + str(e))
            elif action == 'replace':





                # Overwrite everything (including name, price, quantity)
                try:
                    supabase_user.table('user_inventory').update({
                        "name": name.strip(),
                        "quantity": quantity,
                        "price": price_val
                    }).eq('id', int(duplicate_id)).eq('user_email', user_email).execute()
                    flash("Item replaced successfully!")
                except Exception as e:
                    flash("Error replacing item: " + str(e))
            return redirect(url_for('inventory'))





        names = request.form.getlist('name[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')





        # Checking all items entered for duplicates
        for i, (name, qty, price) in enumerate(zip(names, quantities, prices)):
            if not name.strip():
                continue
            try:
                quantity = int(qty)
                price_val = float(price)
            except ValueError:
                continue



            # Query user's inventory for existing items(caps/smalls also checked)



            existing_items_resp = supabase_user.table('user_inventory') \
                .select("*").eq('user_email', user_email).execute()
            existing_items = existing_items_resp.data or []
            duplicate = next(
                (item for item in existing_items if item['name'].strip().lower() == name.strip().lower()), None
            )



            if duplicate:
                # ask what to do if duplicate found : update or replace
                return render_template(
                    'add_item.html',
                    duplicate_item=duplicate,
                    entered_name=name.strip(),
                    entered_quantity=quantity,
                    entered_price=price_val
                )
            else:
                data = {
                    "user_email": user_email,
                    "name": name.strip(),
                    "quantity": quantity,
                    "price": price_val,
                    "created_at": datetime.datetime.utcnow().isoformat()
                }
                # inserting data into user_inventory table using service key client
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

    # getting user's full name from Supabase 'user_details' table for hello,name display in navbar
        try:
            user_detail_response = supabase.table('user_details').select('name').eq('email_id', user.email).execute()
            if user_detail_response.data and len(user_detail_response.data) > 0:
                user_name = user_detail_response.data[0].get('name', 'User')
            else:
                user_name = "User"
        except Exception as e:
            print(f"Error fetching user name from database: {e}")
            user_name = "User"

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
    if not session.get('user_email'):
        flash("Please log in to view reports.")
        return redirect(url_for('login'))
    return render_template('reports.html')




@app.route('/edit-item/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    # Protect update so only logged-in users can access
    if not session.get('user_email'):
        flash("Please log in to edit items.")
        return redirect(url_for('login'))
    user_email = session['user_email']
    supabase_user = get_supabase_client()
    # getting the specific item
    
    try:
        response = supabase_user.table('user_inventory').select("*").eq('id', item_id).eq('user_email', user_email).execute()
        item = response.data[0] if response.data else None
    except Exception as e:
        item = None
        flash("Error fetching item: " + str(e))
    if not item:
        flash("Item not found.")
        return redirect(url_for('inventory'))
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        price = request.form['price']
        try:
            quantity = int(quantity)
            price = float(price)
            # Update item in database
            supabase_user.table('user_inventory').update({
                "name": name,
                "quantity": quantity,
                "price": price
            }).eq('id', item_id).eq('user_email', user_email).execute()
            flash("Item updated successfully!")
        except Exception as e:
            flash("Error updating item: " + str(e))
        return redirect(url_for('inventory'))
    return render_template('edit_item.html', item=item)



@app.route('/delete-item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    # Protect delete so only logged-in users can access
    if not session.get('user_email'):
        flash("Please log in to delete items.")
        return redirect(url_for('login'))
    user_email = session['user_email']
    supabase_user = get_supabase_client()
    try:
        supabase_user.table('user_inventory').delete().eq('id', item_id).eq('user_email', user_email).execute()
        flash("Item deleted successfully!")
    except Exception as e:
        flash("Error deleting item: " + str(e))
    return redirect(url_for('inventory'))



@app.route('/upload-file', methods=['GET', 'POST'])
def upload_file():
    if not session.get('user_email'):
        flash("Please log in to upload files.")
        return redirect(url_for('login'))
    if request.method == 'POST':
        # file upload here
        uploaded_file = request.files.get('file')
        if uploaded_file:
            # Processing the uploaded file
            pass
        flash("File uploaded successfully!")
        return redirect(url_for('inventory'))
    return render_template('upload_file.html')




if __name__ == '__main__':
    app.run(debug=True, port=8000)
