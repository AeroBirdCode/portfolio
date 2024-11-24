from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Check if environment variables are loaded correctly (this is where to print)

app = Flask(__name__)

# Set a random secret key for the session (ensure it's kept secret)
app.config['SECRET_KEY'] = os.urandom(24)

# Fetch admin password from the environment variable
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')  # Get admin password from .env

# Flask-Mail configuration (load sensitive data from environment variables)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Gmail address
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # App-specific password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')  # Sender email

# Initialize Flask-Mail
mail = Mail(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'  # Use SQLite or change to MySQL/PostgreSQL URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ContactMessage model
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)

# Create the tables if they don't already exist
with app.app_context():
    db.create_all()  # This will create the tables for all models



@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Get password from the form
        password = request.form.get('password')
        
        # Check if the entered password matches the one stored in the .env file
        if password == ADMIN_PASSWORD:              
            messages = ContactMessage.query.all()  # Retrieve all messages from the database
            
            return render_template('admin.html', messages=messages)  # If password is correct, show the admin panel
        else:
            # If password is incorrect, show an error message
            flash('Incorrect password. Please try again.', 'danger')
            return redirect(url_for('admin'))
    
    # If no password is entered, show the login form
    return render_template('admin_login.html')

#@app.route('/admin_page')
#def admin_page():
  #  return render_template('admin.html')


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/certificates')
def certificates():
    return render_template('certificates.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    # Print the form data for debugging
    print(f"Form data received: Name: {name}, Email: {email}, Message: {message}")

    
    # Send email to the admin  (optional)----> The data will be stored in database
    msg = Message(f"New message from {name}", recipients=["mohamedhakim1901@gmail.com"])
    msg.body = f"Message from {name} ({email}):\n\n{message}"
    try:
        mail.send(msg)
        flash('Your message has been sent successfully!', 'success')
    except Exception as e:
        flash(f"Failed to send message. Error: {str(e)}", 'danger')
    
    # Store message in the database
    new_message = ContactMessage(name=name, email=email, message=message)
    db.session.add(new_message)
    db.session.commit()


    # Print the newly added message
    print(f"Message saved to the database: {new_message.name}, {new_message.email}, {new_message.message}")
    
    
    return redirect(url_for('contact'))

# Starting the app
if __name__ == '__main__':
    app.run(debug=True)
