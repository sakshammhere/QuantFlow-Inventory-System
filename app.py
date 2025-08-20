from flask import Flask, render_template

app = Flask(__name__)

INVENTORY = [
    {"id": 1, "name": "Item A", "quantity": 10, "price": 300},
    {"id": 2, "name": "Item B", "quantity": 5, "price": 400},
    {"id": 3, "name": "Item C", "quantity": 0, "price": 150},
]

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

@app.route('/add-item')
def add_item():
    return render_template('add_item.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
