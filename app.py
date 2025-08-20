from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

global INVENTORY
INVENTORY = [] #This is left empty initially, and items are added through the add_item route.

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/inventory')
def inventory():
    return render_template('inventory.html', inventory=INVENTORY)

@app.route('/add-item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        names = request.form.getlist('name[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')

        for name, qty, price in zip(names, quantities, prices):
            if not name.strip():  #checks if name is not empty
                continue
            try:
                quantity = int(qty)       #checks if quantity is a valid integer
                price_val = float(price)  #checks if price is a valid float
            except ValueError:
                continue

            #checks if item already exists, if not starts id from 1, otherwise continues incrementing
            new_id = INVENTORY[-1]['id'] + 1 if INVENTORY else 1
            INVENTORY.append({'id': new_id, 'name': name.strip(), 'quantity': quantity, 'price': price_val})

        return redirect(url_for('inventory'))
    else:
        return render_template('add_item.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
