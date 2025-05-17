from flask import Flask, request, redirect, session, render_template_string, g
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database setup
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('marketplace.db')
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Create products table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products 
        (id INTEGER PRIMARY KEY, name TEXT, description TEXT, price REAL, category TEXT)
        ''')
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users 
        (id INTEGER PRIMARY KEY, username TEXT, password TEXT)
        ''')
        
        # Add sample products
        cursor.execute("DELETE FROM products")
        products = [
            (1, "Smartphone X", "Latest smartphone with amazing features", 899.99, "Electronics"),
            (2, "Laptop Pro", "Professional laptop for developers", 1299.99, "Electronics"),
            (3, "Coffee Maker", "Automatic coffee maker", 89.99, "Appliances"),
            (4, "Blender", "High-speed blender", 49.99, "Appliances"),
            (5, "Running Shoes", "Comfortable shoes for runners", 79.99, "Clothing"),
            (6, "T-shirt", "Cotton t-shirt", 19.99, "Clothing"),
            (7, "Headphones", "Noise-cancelling headphones", 199.99, "Electronics"),
            (8, "Smart Watch", "Fitness tracking watch", 149.99, "Electronics"),
            (9, "Toaster", "2-slice toaster", 29.99, "Appliances"),
            (10, "Jeans", "Classic blue jeans", 59.99, "Clothing")
        ]
        cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", products)
        
        # Add users
        cursor.execute("DELETE FROM users")
        users = [
            (1, "administrator", "c4ptain5ecur3"),
            (2, "user1", "password123"),
            (3, "guest", "guest")
        ]
        cursor.executemany("INSERT INTO users VALUES (?, ?, ?)", users)
        
        db.commit()

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login - Vulnerable Marketplace</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 500px;
            margin: 0 auto;
            padding: 20px;
        }
        .container {
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 5px;
        }
        .warning {
            background-color: #fff3cd;
            color: #856404;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            box-sizing: border-box;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .error {
            color: red;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔐 Login to Marketplace</h2>
        
        <div class="warning">
            <strong>Educational Notice:</strong> This application contains intentional vulnerabilities 
            for educational purposes. Do not use in production environments.
        </div>
        
        {% if error %}
        <p class="error">{{ error }}</p>
        {% endif %}
        
        <form method="POST" action="">
            <div>
                <input type="text" name="username" placeholder="Username" required>
            </div>
            <div>
                <input type="password" name="password" placeholder="Password" required>
            </div>
            <div>
                <button type="submit">Login</button>
            </div>
        </form>
        
        <p style="margin-top: 20px;">
            <a href="/marketplace">Continue to marketplace without login</a>
        </p>
    </div>
</body>
</html>
"""

MARKETPLACE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Vulnerable Marketplace</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #ddd;
        }
        .warning {
            background-color: #fff3cd;
            color: #856404;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .filters {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .filter-form {
            display: flex;
            gap: 10px;
        }
        .filter-form select {
            padding: 8px;
        }
        .filter-form button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
        }
        .products {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
        }
        .product {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
        }
        .product h3 {
            margin-top: 0;
        }
        .product .price {
            font-weight: bold;
            color: #28a745;
        }
        .category-badge {
            display: inline-block;
            background-color: #6c757d;
            color: white;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 0.8em;
            margin-top: 5px;
        }
        .debug-panel {
            margin-top: 20px;
            padding: 10px;
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Marketplace Products</h1>
        {% if username %}
            <div>
                Logged in as: <strong>{{ username }}</strong>
                <a href="/logout" style="margin-left: 10px;">(Logout)</a>
            </div>
        {% else %}
            <div>
                <a href="/">Login</a>
            </div>
        {% endif %}
    </div>
    
    <div class="warning">
        <strong>Educational Notice:</strong> This application contains intentional vulnerabilities 
        for educational purposes. Do not use in production environments.
    </div>
    
    <div class="filters">
        <form class="filter-form" method="GET">
            <label for="category">Filter by category:</label>
            <select name="category" id="category">
                <option value="">All Categories</option>
                <option value="Electronics" {% if selected_category == 'Electronics' %}selected{% endif %}>Electronics</option>
                <option value="Appliances" {% if selected_category == 'Appliances' %}selected{% endif %}>Appliances</option>
                <option value="Clothing" {% if selected_category == 'Clothing' %}selected{% endif %}>Clothing</option>
            </select>
            <button type="submit">Apply Filter</button>
        </form>
    </div>
    
    {% if products %}
        <div class="products">
            {% for product in products %}
                <div class="product">
                    <h3>{{ product[0] }}</h3>
                    <p>{{ product[1] }}</p>
                    <p class="price">${{ product[2] }}</p>
                    <span class="category-badge">{{ product[3] }}</span>
                </div>
            {% endfor %}
        </div>
    {% else %}
        <p>No products found.</p>
    {% endif %}
    
    {% if show_debug %}
        <div class="debug-panel">
            <h4>SQL Query Executed:</h4>
            <pre>{{ query_executed }}</pre>
        </div>
    {% endif %}
</body>
</html>
"""

ADMIN_PANEL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Panel - Vulnerable Marketplace</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #ddd;
        }
        .warning {
            background-color: #fff3cd;
            color: #856404;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .success-banner {
            background-color: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: bold;
        }
        .panel {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 10px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Admin Panel</h1>
        <div>
            Logged in as: <strong>{{ username }}</strong>
            <a href="/logout" style="margin-left: 10px;">(Logout)</a>
        </div>
    </div>
    
    <div class="warning">
        <strong>Educational Notice:</strong> This application contains intentional vulnerabilities 
        for educational purposes. Do not use in production environments.
    </div>
    
    <div class="success-banner">
        🎉 Congratulations! You successfully exploited the SQL injection vulnerability! 🎉
    </div>
    
    <div class="panel">
        <h2>User Management</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Password</th>
                </tr>
            </thead>
            <tbody>
                {% for user in users %}
                <tr>
                    <td>{{ user['id'] }}</td>
                    <td>{{ user['username'] }}</td>
                    <td>{{ user['password'] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <p><a href="/marketplace">Back to Marketplace</a></p>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            
            if user:
                session['username'] = user['username']
                session['user_id'] = user['id']
                
                if username == 'administrator':
                    return redirect('/admin')
                else:
                    return redirect('/marketplace')
            else:
                error = "Invalid credentials! Please try again."
        except sqlite3.Error as e:
            error = f"Database error: {str(e)}"
        
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/marketplace')
def marketplace():
    # Get selected category filter
    category = request.args.get('category', '')
    
    db = get_db()
    cursor = db.cursor()
    
    # Vulnerable code - SQL Injection in category filter
    query = "SELECT name, description, price, category FROM products"
    
    if category:
        # This is where the vulnerability exists - direct string concatenation
        query += f" WHERE category = '{category}'"
    
    show_debug = 'debug' in request.args
    
    try:
        cursor.execute(query)
        products = cursor.fetchall()
    except sqlite3.Error as e:
        # This allows SQL errors to be shown to the user, aiding in SQL injection development
        return f"SQL Error: {str(e)}<br><a href='/marketplace'>Go back</a>"
    
    username = session.get('username')
    return render_template_string(
        MARKETPLACE_TEMPLATE, 
        products=products, 
        selected_category=category,
        username=username,
        show_debug='debug' in request.args,
        query_executed=query if show_debug else None
    )

@app.route('/admin')
def admin_panel():
    if session.get('username') != 'administrator':
        return redirect('/')
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    return render_template_string(ADMIN_PANEL_TEMPLATE, username='administrator', users=users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True, host='0.0.0.0', port=5000)