from flask import Flask, render_template_string, session, redirect, url_for, request, g
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

# Initialize the database when the app starts
init_db()

MARKETPLACE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MarketHub - Marketplace</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #1A1A1A;
            line-height: 1.6;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #ddd;
        }
        .logo {
            font-size: 1.8rem;
            font-weight: 700;
            color: #4CAF50;
        }
        .logo span {
            color: #2196F3;
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
            align-items: center;
        }
        .filter-form select {
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }
        .filter-form button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .filter-form button:hover {
            background-color: #3e8e41;
        }
        .products {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
        }
        .product {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .product:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .product h3 {
            margin-top: 0;
            color: #4CAF50;
        }
        .product .price {
            font-weight: bold;
            color: #FF5722;
            font-size: 1.2rem;
        }
        .category-badge {
            display: inline-block;
            background-color: #2196F3;
            color: white;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 0.8em;
            margin-top: 5px;
        }
        .user-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .logout-btn {
            background: none;
            border: none;
            color: #FF5722;
            cursor: pointer;
            text-decoration: underline;
        }
        .section-title {
            text-align: center;
            margin-bottom: 2rem;
        }
        .section-title h2 {
            font-size: 2rem;
            color: #4CAF50;
            position: relative;
            display: inline-block;
            padding-bottom: 1rem;
        }
        .section-title h2:after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 3px;
            background: #FF5722;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Market<span>Hub</span></div>
        {% if username %}
            <div class="user-info">
                Welcome, <strong>{{ username }}</strong>
                <form action="{{ url_for('logout') }}" method="post" style="display: inline;">
                    <button type="submit" class="logout-btn">Logout</button>
                </form>
            </div>
        {% else %}
            <div>
                <a href="{{ url_for('login') }}" style="color: #4CAF50; text-decoration: none; font-weight: 600;">Login</a>
            </div>
        {% endif %}
    </div>
    
    <div class="section-title">
        <h2>Marketplace Products</h2>
    </div>
    
    <div class="filters">
        <form class="filter-form" method="GET" action="{{ url_for('marketplace') }}">
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
        <p style="text-align: center;">No products found.</p>
    {% endif %}
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MarketHub | Login</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #F5F7FA;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .login-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            padding: 2rem;
            width: 100%;
            max-width: 400px;
        }
        .logo {
            text-align: center;
            font-size: 2rem;
            font-weight: 700;
            color: #4CAF50;
            margin-bottom: 1.5rem;
        }
        .logo span {
            color: #2196F3;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }
        .form-group input {
            width: 100%;
            padding: 0.8rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
        }
        .btn {
            width: 100%;
            padding: 0.8rem;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .btn:hover {
            background-color: #3e8e41;
        }
        .error {
            color: #FF5722;
            margin-bottom: 1rem;
            text-align: center;
        }
        .register-link {
            text-align: center;
            margin-top: 1.5rem;
        }
        .register-link a {
            color: #2196F3;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">Market<span>Hub</span></div>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        <form method="POST" action="{{ url_for('process_login') }}">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
        
        <div class="register-link">
            Don't have an account? <a href="{{ url_for('register') }}">Register here</a>
        </div>
    </div>
</body>
</html>
"""

REGISTER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MarketHub | Register</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #F5F7FA;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .register-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            padding: 2rem;
            width: 100%;
            max-width: 400px;
        }
        .logo {
            text-align: center;
            font-size: 2rem;
            font-weight: 700;
            color: #4CAF50;
            margin-bottom: 1.5rem;
        }
        .logo span {
            color: #2196F3;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }
        .form-group input {
            width: 100%;
            padding: 0.8rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
        }
        .btn {
            width: 100%;
            padding: 0.8rem;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .btn:hover {
            background-color: #3e8e41;
        }
        .error {
            color: #FF5722;
            margin-bottom: 1rem;
            text-align: center;
        }
        .login-link {
            text-align: center;
            margin-top: 1.5rem;
        }
        .login-link a {
            color: #2196F3;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="register-container">
        <div class="logo">Market<span>Hub</span></div>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        <form method="POST" action="{{ url_for('process_register') }}">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div class="form-group">
                <label for="confirm_password">Confirm Password</label>
                <input type="password" id="confirm_password" name="confirm_password" required>
            </div>
            <button type="submit" class="btn">Register</button>
        </form>
        
        <div class="login-link">
            Already have an account? <a href="{{ url_for('login') }}">Login here</a>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    # Redirect to marketplace if already logged in
    if 'username' in session:
        return redirect(url_for('marketplace'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MarketHub | Online Marketplace</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #4CAF50;
            --secondary: #FF5722;
            --accent: #2196F3;
            --light: #F5F7FA;
            --dark: #1A1A1A;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            color: var(--dark);
            line-height: 1.6;
        }
        
        header {
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: fixed;
            width: 100%;
            z-index: 1000;
        }
        
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 5%;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--primary);
        }
        
        .logo span {
            color: var(--accent);
        }
        
        .nav-links a {
            color: var(--dark);
            text-decoration: none;
            margin-left: 2rem;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .nav-links a:hover {
            color: var(--primary);
        }
        
        .login-btn {
            background: var(--primary);
            color: white;
            padding: 0.6rem 1.5rem;
            border-radius: 30px;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .login-btn:hover {
            background: var(--secondary);
            transform: translateY(-2px);
        }
        
        .hero {
            background: linear-gradient(rgba(76, 175, 80, 0.8), rgba(76, 175, 80, 0.8)), url('https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80');
            background-size: cover;
            background-position: center;
            height: 100vh;
            display: flex;
            align-items: center;
            color: white;
            text-align: center;
            padding: 0 5%;
        }
        
        .hero-content {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .hero h1 {
            font-size: 3.5rem;
            margin-bottom: 1rem;
        }
        
        .hero p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
        
        .cta-btn {
            background: white;
            color: var(--primary);
            padding: 0.8rem 2rem;
            border-radius: 30px;
            text-decoration: none;
            font-weight: 700;
            font-size: 1.1rem;
            display: inline-block;
            transition: all 0.3s;
        }
        
        .cta-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            background: var(--accent);
            color: white;
        }
        
        section {
            padding: 5rem 5%;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .section-title {
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .section-title h2 {
            font-size: 2.5rem;
            color: var(--primary);
            position: relative;
            display: inline-block;
            padding-bottom: 1rem;
        }
        
        .section-title h2:after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 3px;
            background: var(--secondary);
        }
        
        .categories {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }
        
        .category-card {
            background: white;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            transition: transform 0.3s;
            text-align: center;
        }
        
        .category-card:hover {
            transform: translateY(-10px);
        }
        
        .category-card i {
            font-size: 2.5rem;
            color: var(--accent);
            margin-bottom: 1.5rem;
        }
        
        .stats {
            background: var(--light);
            text-align: center;
            padding: 4rem 0;
        }
        
        .stats-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .stat-item h3 {
            font-size: 3rem;
            color: var(--primary);
            margin-bottom: 0.5rem;
        }
        
        .testimonials {
            background: var(--primary);
            color: white;
        }
        
        .testimonial-slider {
            max-width: 800px;
            margin: 0 auto;
            text-align: center;
        }
        
        .featured-products {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
        }
        
        .product-card {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        
        .product-card:hover {
            transform: translateY(-5px);
        }
        
        .product-image {
            height: 200px;
            background-size: cover;
            background-position: center;
        }
        
        .product-info {
            padding: 1.5rem;
        }
        
        .product-price {
            color: var(--secondary);
            font-weight: bold;
            font-size: 1.2rem;
            margin: 0.5rem 0;
        }
        
        footer {
            background: var(--dark);
            color: white;
            padding: 3rem 5%;
            text-align: center;
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .footer-links a {
            color: white;
            text-decoration: none;
        }
        
        .social-icons {
            margin-bottom: 2rem;
        }
        
        .social-icons a {
            color: white;
            margin: 0 0.5rem;
            font-size: 1.2rem;
        }
        
        @media (max-width: 768px) {
            .navbar {
                flex-direction: column;
                padding: 1rem;
            }
            
            .nav-links {
                margin-top: 1rem;
            }
            
            .hero h1 {
                font-size: 2.5rem;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="navbar">
            <div class="logo">Market<span>Hub</span></div>
            <div class="nav-links">
                <a href="#categories">Categories</a>
                <a href="#products">Featured Products</a>
                <a href="#about">About Us</a>
                <a href="{{ url_for('login') }}" class="login-btn">Login / Register</a>
            </div>
        </div>
    </header>

    <section class="hero">
        <div class="hero-content">
            <h1>Discover Amazing Products</h1>
            <p>Join our growing marketplace of buyers and sellers. Find unique items or sell your own with our easy-to-use platform.</p>
            <a href="{{ url_for('marketplace') }}" class="cta-btn">Browse Marketplace</a>
        </div>
    </section>

    <section id="categories">
        <div class="section-title">
            <h2>Popular Categories</h2>
        </div>
        <div class="categories">
            <div class="category-card">
                <i class="fas fa-tshirt"></i>
                <h3>Fashion</h3>
                <p>Discover the latest trends in clothing, shoes, and accessories from top sellers.</p>
            </div>
            <div class="category-card">
                <i class="fas fa-laptop"></i>
                <h3>Electronics</h3>
                <p>Find great deals on gadgets, computers, and home electronics.</p>
            </div>
            <div class="category-card">
                <i class="fas fa-home"></i>
                <h3>Home & Garden</h3>
                <p>Everything you need to make your home beautiful and functional.</p>
            </div>
        </div>
    </section>

    <section id="products">
        <div class="section-title">
            <h2>Featured Products</h2>
        </div>
        <div class="featured-products">
            <div class="product-card">
                <div class="product-image" style="background-image: url('https://images.unsplash.com/photo-1546868871-7041f2a55e12?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60');"></div>
                <div class="product-info">
                    <h3>Wireless Headphones</h3>
                    <p>Premium sound quality with noise cancellation</p>
                    <div class="product-price">$129.99</div>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image" style="background-image: url('https://images.unsplash.com/photo-1523275335684-37898b6baf30?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60');"></div>
                <div class="product-info">
                    <h3>Smart Watch</h3>
                    <p>Track your fitness and stay connected</p>
                    <div class="product-price">$199.99</div>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image" style="background-image: url('https://images.unsplash.com/photo-1594035910387-fea47794261f?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60');"></div>
                <div class="product-info">
                    <h3>Handmade Ceramic Mug</h3>
                    <p>Unique artisan pottery for your morning coffee</p>
                    <div class="product-price">$24.99</div>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image" style="background-image: url('https://images.unsplash.com/photo-1547949003-9792a18a2601?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60');"></div>
                <div class="product-info">
                    <h3>Leather Backpack</h3>
                    <p>Stylish and durable for everyday use</p>
                    <div class="product-price">$89.99</div>
                </div>
            </div>
        </div>
    </section>

    <section class="stats">
        <div class="stats-container">
            <div class="stat-item">
                <h3>50K+</h3>
                <p>Active Sellers</p>
            </div>
            <div class="stat-item">
                <h3>2M+</h3>
                <p>Products Listed</p>
            </div>
            <div class="stat-item">
                <h3>10M+</h3>
                <p>Happy Customers</p>
            </div>
            <div class="stat-item">
                <h3>100%</h3>
                <p>Secure Payments</p>
            </div>
        </div>
    </section>

    <section id="about">
        <div class="section-title">
            <h2>About MarketHub</h2>
        </div>
        <div style="max-width: 800px; margin: 0 auto; text-align: center;">
            <p>MarketHub connects buyers and sellers in a vibrant online marketplace. Our mission is to make buying and selling online simple, secure, and enjoyable for everyone.</p>
            <p>Whether you're looking for unique handmade items or the latest gadgets, or want to turn your passion into a business, MarketHub is the place for you.</p>
        </div>
    </section>

    <section class="testimonials">
        <div class="section-title">
            <h2>What Our Users Say</h2>
        </div>
        <div class="testimonial-slider">
            <p>"I've been selling my handmade jewelry on MarketHub for 2 years now, and it's completely transformed my small business. The platform is easy to use and the community is wonderful!"</p>
            <p><strong>— Emily Rodriguez, Artisan Jewelry Designer</strong></p>
        </div>
    </section>

    <footer id="contact">
        <div class="footer-links">
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
            <a href="#">Sell on MarketHub</a>
            <a href="{{ url_for('login') }}">Seller Dashboard</a>
        </div>
        <div class="social-icons">
            <a href="#"><i class="fab fa-twitter"></i></a>
            <a href="#"><i class="fab fa-linkedin"></i></a>
            <a href="#"><i class="fab fa-facebook"></i></a>
            <a href="#"><i class="fab fa-instagram"></i></a>
        </div>
        <p>&copy; 2025 MarketHub. All rights reserved.</p>
    </footer>
</body>
</html>
''')

@app.route('/marketplace')
def marketplace():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get selected category filter
    category = request.args.get('category', '')
    
    db = get_db()
    cursor = db.cursor()
    
    # Vulnerable code - SQL Injection in category filter
    query = "SELECT name, description, price, category FROM products"
    
    if category:
        # This is where the vulnerability exists - direct string concatenation
        query += f" WHERE category = '{category}'"
    
    try:
        cursor.execute(query)
        products = cursor.fetchall()
    except sqlite3.Error as e:
        # This allows SQL errors to be shown to the user, aiding in SQL injection development
        return f"SQL Error: {str(e)}<br><a href='/marketplace'>Go back</a>"
    
    return render_template_string(
        MARKETPLACE_TEMPLATE, 
        products=products, 
        selected_category=category,
        username=session.get('username')
    )

@app.route('/login')
def login():
    if 'username' in session:
        return redirect(url_for('marketplace'))
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/register')
def register():
    if 'username' in session:
        return redirect(url_for('marketplace'))
    return render_template_string(REGISTER_TEMPLATE)

@app.route('/process_login', methods=['POST'])
def process_login():
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
                return redirect(url_for('marketplace'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error="Invalid credentials! Please try again.")
    except sqlite3.Error as e:
        return render_template_string(LOGIN_TEMPLATE, error=f"Database error: {str(e)}")

@app.route('/process_register', methods=['POST'])
def process_register():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    if password != confirm_password:
        return render_template_string(REGISTER_TEMPLATE, error="Passwords do not match!")
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return render_template_string(REGISTER_TEMPLATE, error="Username already exists!")
        
        # Insert new user
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        db.commit()
        
        session['username'] = username
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        session['user_id'] = user['id']
        
        return redirect(url_for('marketplace'))
    except sqlite3.Error as e:
        return render_template_string(REGISTER_TEMPLATE, error=f"Database error: {str(e)}")

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
def admin_panel():
    if session.get('username') != 'administrator':
        return redirect('/')
    
    db = get_db()
    cursor = db.cursor()
    
    # Get all users with their credit card info
    # Modified query to match your actual database schema
    cursor.execute("""
        SELECT id, username, credit_card_hash, created_at, last_login, status
        FROM users
        ORDER BY id
    """)
    users = cursor.fetchall()
    
    # Get total sales amount
    cursor.execute("SELECT SUM(total_price) FROM sales")
    total_sales_amount = cursor.fetchone()[0] or 0  # Handle None case
    
    # Get total number of sales
    cursor.execute("SELECT COUNT(*) FROM sales")
    total_sales_count = cursor.fetchone()[0]
    
    # Get total number of products
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]
    
    # Get total number of users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    # Get monthly sales data for chart
    cursor.execute("""
        SELECT strftime('%Y-%m', sale_date) as month, SUM(total_price) as total
        FROM sales
        GROUP BY month
        ORDER BY month
    """)
    monthly_sales = cursor.fetchall()
    
    # Get sales by category
    cursor.execute("""
        SELECT p.category, SUM(s.total_price) as total
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.category
        ORDER BY total DESC
    """)
    sales_by_category = cursor.fetchall()
    
    # Get top selling products
    cursor.execute("""
        SELECT p.name, SUM(s.quantity) as total_quantity
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.id
        ORDER BY total_quantity DESC
        LIMIT 5
    """)
    top_products = cursor.fetchall()
    
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE,
                                 users=users,
                                 total_sales_amount=total_sales_amount,
                                 total_sales_count=total_sales_count,
                                 total_products=total_products,
                                 total_users=total_users,
                                 monthly_sales=monthly_sales,
                                 sales_by_category=sales_by_category,
                                 top_products=top_products)

# Admin dashboard template
ADMIN_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MarketHub | Admin Dashboard</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js"></script>
    <style>
        :root {
            --primary: #4CAF50;
            --secondary: #FF5722;
            --accent: #2196F3;
            --danger: #f44336;
            --warning: #ff9800;
            --success: #4caf50;
            --light: #F5F7FA;
            --dark: #1A1A1A;
            --gray: #757575;
            --card-bg: #ffffff;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            color: var(--dark);
            line-height: 1.6;
        }
        
        .container {
            display: flex;
            min-height: 100vh;
        }
        
        .sidebar {
            width: 250px;
            background-color: var(--dark);
            color: white;
            padding: 20px 0;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
        }
        
        .sidebar-header {
            padding: 0 20px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .logo span {
            color: var(--accent);
        }
        
        .sidebar-menu {
            padding: 20px 0;
        }
        
        .menu-title {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--gray);
            padding: 10px 20px;
            margin-top: 10px;
        }
        
        .sidebar-menu ul {
            list-style: none;
        }
        
        .sidebar-menu li {
            margin-bottom: 5px;
        }
        
        .sidebar-menu a {
            display: flex;
            align-items: center;
            padding: 10px 20px;
            color: #e0e0e0;
            text-decoration: none;
            transition: all 0.3s;
        }
        
        .sidebar-menu a:hover, .sidebar-menu a.active {
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
            border-left: 4px solid var(--primary);
        }
        
        .sidebar-menu a i {
            margin-right: 10px;
            width: 20px;
            text-align: center;
        }
        
        .main-content {
            flex: 1;
            padding: 20px;
            margin-left: 250px;
        }
        
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .page-title {
            font-size: 1.8rem;
            font-weight: 500;
        }
        
        .user-info {
            display: flex;
            align-items: center;
        }
        
        .user-info img {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 10px;
        }
        
        .cards-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }
        
        .card-icon {
            width: 50px;
            height: 50px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 15px;
            color: white;
            font-size: 1.5rem;
        }
        
        .bg-primary {
            background-color: var(--primary);
        }
        
        .bg-secondary {
            background-color: var(--secondary);
        }
        
        .bg-accent {
            background-color: var(--accent);
        }
        
        .bg-danger {
            background-color: var(--danger);
        }
        
        .card-value {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .card-label {
            color: var(--gray);
            font-size: 0.9rem;
        }
        
        .charts-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .chart-card {
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .chart-title {
            font-size: 1.2rem;
            margin-bottom: 15px;
            color: var(--dark);
        }
        
        .table-container {
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow-x: auto;
        }
        
        .table-title {
            font-size: 1.2rem;
            margin-bottom: 15px;
            color: var(--dark);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        
        th {
            background-color: #f9f9f9;
            font-weight: 600;
        }
        
        tr:hover {
            background-color: #f5f5f5;
        }
        
        .status {
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .status-active {
            background-color: rgba(76, 175, 80, 0.1);
            color: var(--success);
        }
        
        .status-inactive {
            background-color: rgba(117, 117, 117, 0.1);
            color: var(--gray);
        }
        
        .status-suspended {
            background-color: rgba(255, 152, 0, 0.1);
            color: var(--warning);
        }
        
        .button {
            display: inline-block;
            padding: 8px 15px;
            border-radius: 4px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .button-view {
            background-color: var(--accent);
            color: white;
        }
        
        .button-edit {
            background-color: var(--warning);
            color: white;
        }
        
        .button-delete {
            background-color: var(--danger);
            color: white;
        }
        
        .pagination {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        
        .pagination a {
            color: var(--dark);
            padding: 8px 12px;
            margin: 0 5px;
            border-radius: 4px;
            text-decoration: none;
            transition: background-color 0.3s;
        }
        
        .pagination a:hover {
            background-color: #f5f5f5;
        }
        
        .pagination a.active {
            background-color: var(--primary);
            color: white;
        }
        
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: pointer;
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 200px;
            background-color: rgba(0, 0, 0, 0.8);
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        
        @media (max-width: 1024px) {
            .charts-container {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 768px) {
            .container {
                flex-direction: column;
            }
            
            .sidebar {
                width: 100%;
                height: auto;
                position: relative;
            }
            
            .main-content {
                margin-left: 0;
            }
            
            .cards-container {
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <div class="sidebar-header">
                <div class="logo">Market<span>Hub</span></div>
                <p>Admin Dashboard</p>
            </div>
            
            <div class="sidebar-menu">
                <span class="menu-title">Main</span>
                <ul>
                    <li><a href="#" class="active"><i class="fas fa-tachometer-alt"></i> Dashboard</a></li>
                    <li><a href="#"><i class="fas fa-users"></i> Users</a></li>
                    <li><a href="#"><i class="fas fa-box"></i> Products</a></li>
                    <li><a href="#"><i class="fas fa-shopping-cart"></i> Orders</a></li>
                </ul>
                
                <span class="menu-title">Reports</span>
                <ul>
                    <li><a href="#"><i class="fas fa-chart-bar"></i> Sales Reports</a></li>
                    <li><a href="#"><i class="fas fa-file-invoice-dollar"></i> Financial Reports</a></li>
                    <li><a href="#"><i class="fas fa-flag"></i> User Activity</a></li>
                </ul>
                
                <span class="menu-title">Settings</span>
                <ul>
                    <li><a href="#"><i class="fas fa-cog"></i> General Settings</a></li>
                    <li><a href="#"><i class="fas fa-shield-alt"></i> Security</a></li>
                    <li><a href="{{ url_for('logout') }}"><i class="fas fa-sign-out-alt"></i> Logout</a></li>
                </ul>
            </div>
        </div>
        
        <div class="main-content">
            <div class="page-header">
                <h1 class="page-title">Admin Dashboard</h1>
                <div class="user-info">
                    <img src="/api/placeholder/40/40" alt="Admin">
                    <div>
                        <p>Administrator</p>
                        <small>Super Admin</small>
                    </div>
                </div>
            </div>
            
            <div class="cards-container">
                <div class="card">
                    <div class="card-icon bg-primary">
                        <i class="fas fa-dollar-sign"></i>
                    </div>
                    <div class="card-value">${{ '{:,.2f}'.format(total_sales_amount) }}</div>
                    <div class="card-label">Total Sales</div>
                </div>
                
                <div class="card">
                    <div class="card-icon bg-secondary">
                        <i class="fas fa-shopping-bag"></i>
                    </div>
                    <div class="card-value">{{ '{:,}'.format(total_sales_count) }}</div>
                    <div class="card-label">Orders</div>
                </div>
                
                <div class="card">
                    <div class="card-icon bg-accent">
                        <i class="fas fa-box"></i>
                    </div>
                    <div class="card-value">{{ '{:,}'.format(total_products) }}</div>
                    <div class="card-label">Products</div>
                </div>
                
                <div class="card">
                    <div class="card-icon bg-danger">
                        <i class="fas fa-users"></i>
                    </div>
                    <div class="card-value">{{ '{:,}'.format(total_users) }}</div>
                    <div class="card-label">Users</div>
                </div>
            </div>
            
            <div class="charts-container">
                <div class="chart-card">
                    <h2 class="chart-title">Monthly Sales</h2>
                    <canvas id="monthlySalesChart"></canvas>
                </div>
                
                <div class="chart-card">
                    <h2 class="chart-title">Sales by Category</h2>
                    <canvas id="categorySalesChart"></canvas>
                </div>
                
                <div class="chart-card">
                    <h2 class="chart-title">Top Selling Products</h2>
                    <canvas id="topProductsChart"></canvas>
                </div>
                
                <div class="chart-card">
                    <h2 class="chart-title">User Registration Trend</h2>
                    <canvas id="userRegistrationChart"></canvas>
                </div>
            </div>
            
            <div class="table-container">
                <h2 class="table-title">User Information (Including Credit Card Data)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Credit Card Hash (MD5)</th>
                            <th>Created</th>
                            <th>Last Login</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for user in users %}
                        <tr>
                            <td>{{ user[0] }}</td>
                            <td>{{ user[1] }}</td>
                            <td>
                                <div class="tooltip">
                                    {{ user[2] }}
                                    <span class="tooltiptext">Vulnerable MD5 hash!</span>
                                </div>
                            </td>
                            <td>{{ user[3] }}</td>
                            <td>{{ user[4] }}</td>
                            <td>
                                {% if user[5] == 'active' %}
                                <span class="status status-active">Active</span>
                                {% elif user[5] == 'inactive' %}
                                <span class="status status-inactive">Inactive</span>
                                {% else %}
                                <span class="status status-suspended">Suspended</span>
                                {% endif %}
                            </td>
                            <td>
                                <button class="button button-view"><i class="fas fa-eye"></i></button>
                                <button class="button button-edit"><i class="fas fa-edit"></i></button>
                                <button class="button button-delete"><i class="fas fa-trash"></i></button>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                <div class="pagination">
                    <a href="#" class="active">1</a>
                    <a href="#">2</a>
                    <a href="#">3</a>
                    <a href="#">4</a>
                    <a href="#">5</a>
                    <a href="#">Next</a>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Monthly Sales Chart
        var monthlySalesCtx = document.getElementById('monthlySalesChart').getContext('2d');
        var monthlySalesChart = new Chart(monthlySalesCtx, {
            type: 'line',
            data: {
                labels: [{% for month in monthly_sales %}'{{ month[0] }}',{% endfor %}],
                datasets: [{
                    label: 'Total Sales ($)',
                    data: [{% for month in monthly_sales %}{{ month[1] }},{% endfor %}],
                    backgroundColor: 'rgba(76, 175, 80, 0.2)',
                    borderColor: '#4CAF50',
                    borderWidth: 2,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
        
        // Category Sales Chart
        var categorySalesCtx = document.getElementById('categorySalesChart').getContext('2d');
        var categorySalesChart = new Chart(categorySalesCtx, {
            type: 'doughnut',
            data: {
                labels: [{% for category in sales_by_category %}'{{ category[0] }}',{% endfor %}],
                datasets: [{
                    data: [{% for category in sales_by_category %}{{ category[1] }},{% endfor %}],
                    backgroundColor: [
                        '#4CAF50',
                        '#FF5722',
                        '#2196F3',
                        '#9C27B0',
                        '#FFC107'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        
        // Top Products Chart
        var topProductsCtx = document.getElementById('topProductsChart').getContext('2d');
        var topProductsChart = new Chart(topProductsCtx, {
            type: 'bar',
            data: {
                labels: [{% for product in top_products %}'{{ product[0] }}',{% endfor %}],
                datasets: [{
                    label: 'Units Sold',
                    data: [{% for product in top_products %}{{ product[1] }},{% endfor %}],
                    backgroundColor: '#2196F3'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        // User Registration Trend Chart (simulated data)
        var userRegistrationCtx = document.getElementById('userRegistrationChart').getContext('2d');
        var userRegistrationChart = new Chart(userRegistrationCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'New Users',
                    data: [5, 8, 12, 15, 10, 7, 9, 11, 14, 16, 18, 20],
                    backgroundColor: 'rgba(255, 87, 34, 0.2)',
                    borderColor: '#FF5722',
                    borderWidth: 2,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        // Tooltip functionality
        const tooltips = document.querySelectorAll('.tooltip');
        tooltips.forEach(tooltip => {
            tooltip.addEventListener('mouseover', function() {
                this.querySelector('.tooltiptext').style.visibility = 'visible';
                this.querySelector('.tooltiptext').style.opacity = '1';
            });
            
            tooltip.addEventListener('mouseout', function() {
                this.querySelector('.tooltiptext').style.visibility = 'hidden';
                this.querySelector('.tooltiptext').style.opacity = '0';
            });
        });
        
        // Action buttons functionality
        const viewButtons = document.querySelectorAll('.button-view');
        viewButtons.forEach(button => {
            button.addEventListener('click', function() {
                const userId = this.closest('tr').querySelector('td:first-child').textContent;
                alert('Viewing user with ID: ' + userId);
                // Here you would redirect to a user details page
            });
        });
        
        const editButtons = document.querySelectorAll('.button-edit');
        editButtons.forEach(button => {
            button.addEventListener('click', function() {
                const userId = this.closest('tr').querySelector('td:first-child').textContent;
                alert('Editing user with ID: ' + userId);
                // Here you would redirect to a user edit page
            });
        });
        
        const deleteButtons = document.querySelectorAll('.button-delete');
        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                const userId = this.closest('tr').querySelector('td:first-child').textContent;
                const userName = this.closest('tr').querySelector('td:nth-child(2)').textContent;
                if (confirm('Are you sure you want to delete user ' + userName + ' (ID: ' + userId + ')?')) {
                    alert('User deleted successfully!');
                    // Here you would send an AJAX request to delete the user
                }
            });
        });
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)