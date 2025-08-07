from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong, secure secret key
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# MongoDB setup
app.config['MONGO_URI'] = "mongodb://localhost:27017/ecommerce_db"  # MongoDB connection
mongo = PyMongo(app)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Home Route
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Store the user in MongoDB
        mongo.db.users.insert_one({
            'username': username,
            'password': password,  # For security, consider hashing passwords
            'role': role
        })

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = mongo.db.users.find_one({'username': username})

        if user and user['password'] == password:
            session['username'] = user['username']
            session['role'] = user['role']

            flash('Login successful!')

            # Redirect based on role
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password.')
    
    return render_template('login.html')

# Admin Dashboard Route
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'role' in session and session['role'] == 'admin':
        products = mongo.db.products.find()
        feedbacks = mongo.db.feedbacks.find()  # Fetch all feedbacks
        return render_template('admin_dashboard.html', products=products, feedbacks=feedbacks)
    else:
        flash('Unauthorized access.')
        return redirect(url_for('login'))

# Add Product Route (Admin Only)
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'role' in session and session['role'] == 'admin':
        if request.method == 'POST':
            category = request.form['category']
            product_name = request.form['product_name']
            quantity = request.form['quantity']
            quality = request.form['quality']
            price = request.form['price']

            # Handle image upload
            image_url = None
            if 'image' in request.files:
                file = request.files['image']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_url = url_for('static', filename='uploads/' + filename)

            # Insert product into the database
            mongo.db.products.insert_one({
                'category': category,
                'product_name': product_name,
                'quantity': quantity,
                'quality': quality,
                'price': price,
                'image_url': image_url
            })

            flash('Product added successfully!')
            return redirect(url_for('admin_dashboard'))
        return render_template('add_product.html')
    else:
        flash('Unauthorized access.')
        return redirect(url_for('login'))

# Edit Product Route (Admin Only)
@app.route('/edit_product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'role' in session and session['role'] == 'admin':
        product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
        if request.method == 'POST':
            # Handle image upload
            image_url = product['image_url']
            if 'image' in request.files:
                file = request.files['image']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_url = url_for('static', filename='uploads/' + filename)

            # Update the product
            mongo.db.products.update_one({'_id': ObjectId(product_id)}, {
                "$set": {
                    'product_name': request.form['product_name'],
                    'quantity': request.form['quantity'],
                    'quality': request.form['quality'],
                    'price': request.form['price'],
                    'image_url': image_url
                }
            })
            flash('Product updated successfully.')
            return redirect(url_for('admin_dashboard'))
        return render_template('edit_product.html', product=product)
    else:
        flash('Unauthorized access.')
        return redirect(url_for('login'))

# Delete Product Route (Admin Only)
@app.route('/delete_product/<product_id>', methods=['POST'])
def delete_product(product_id):
    if 'role' in session and session['role'] == 'admin':
        mongo.db.products.delete_one({"_id": ObjectId(product_id)})
        flash('Product deleted successfully.')
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Unauthorized access.')
        return redirect(url_for('login'))

# Delete Feedback Route (Admin Only)
@app.route('/delete_feedback/<feedback_id>', methods=['POST'])
def delete_feedback(feedback_id):
    if 'role' in session and session['role'] == 'admin':
        mongo.db.feedbacks.delete_one({"_id": ObjectId(feedback_id)})
        flash('Feedback deleted successfully.')
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Unauthorized access.')
        return redirect(url_for('login'))

# User Dashboard Route
@app.route('/user_dashboard')
def user_dashboard():
    if 'role' in session and session['role'] == 'user':
        products = mongo.db.products.find()
        return render_template('user_dashboard.html', products=products)
    else:
        flash('Unauthorized access.')
        return redirect(url_for('login'))

# View Product (User Only)
@app.route('/product/<product_id>')
def view_product(product_id):
    if 'role' in session and session['role'] == 'user':
        product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
        return render_template('view_product.html', product=product)
    else:
        flash('Unauthorized access.')
        return redirect(url_for('login'))

@app.route('/order/<product_id>', methods=['GET', 'POST'])
def order_product(product_id):
    if 'role' in session and session['role'] == 'user':
        if request.method == 'POST':
            name = request.form['name']
            contact = request.form['contact']
            address = request.form['address']
            quantity = int(request.form['quantity'])
            quality = request.form['quality']
            price = float(request.form['price'].replace('$', '').strip())  # Strip '$' and convert to float

            # Save order details to the database
            total_price = quantity * price

            mongo.db.orders.insert_one({
                'product_id': product_id,
                'name': name,
                'contact': contact,
                'address': address,
                'quantity': quantity,
                'quality': quality,
                'price': price,
                'total_price': total_price
            })

            flash('Order placed successfully!')
            return redirect(url_for('user_dashboard'))

        product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
        return render_template('order_form.html', product=product)
    else:
        flash('Unauthorized access.')
        return redirect(url_for('login'))

# Submit Feedback (User)
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        product_id = request.form['product_id']
        feedback_text = request.form['feedback']
        rating = request.form['rating']
        name = request.form['name']
        contact = request.form['contact']
        address = request.form['address']

        # Save feedback to the database
        mongo.db.feedbacks.insert_one({
            'product_id': product_id,
            'feedback': feedback_text,
            'rating': rating,
            'name': name,
            'contact': contact,
            'address': address
        })

        flash('Feedback submitted successfully.')
        return redirect(url_for('user_dashboard'))  # Redirect after successful submission
    else:
        # For GET requests, provide product list to the feedback form
        products = mongo.db.products.find()
        return render_template('feedback.html', products=products)

# Contact Route
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Save contact message to the database
        mongo.db.contact_messages.insert_one({
            'name': name,
            'email': email,
            'message': message
        })

        flash('Message sent successfully.')
        return redirect(url_for('home'))
    
    return render_template('contact.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        # Handle POST request
        pass
    elif request.method == 'GET':
        # Handle GET request (not recommended for logout)
        pass
    return redirect(url_for('login'))  # Redirect after logout
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)

