from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length
from model import User
from flask_login import login_user
from bson.objectid import ObjectId
from flask_login import LoginManager
import random


# Flask app initialization
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Secret key for session handling


# Initialize LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# MongoDB Atlas connection setup
uri = "mongodb+srv://namansehwal:UUpHBWqGx7KXFaJ5@cluster0.qgjqnha.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
new_client = MongoClient(uri, server_api=ServerApi('1'))

db = client['User']
users_collection = db['Auth']

new_db = new_client['MedicalDatabase']
medical_collection = new_db['MedicalInfo']

# Flask-WTF form classes
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])

class MedicalInfoForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    age = StringField('Age', validators=[InputRequired()])
    sex = StringField('Sex', validators=[InputRequired()])
    blood_group = StringField('Blood Group', validators=[InputRequired()])
    height = StringField('Height', validators=[InputRequired()])
    weight = StringField('Weight', validators=[InputRequired()])
    allergies = StringField('Allergies', validators=[InputRequired()])
    diabetic_status = StringField('Diabetic Status', validators=[InputRequired()])

@login_manager.user_loader
def load_user(user_id):
    # Convert the `user_id` to an ObjectId if you are using MongoDB
    user_id = ObjectId(user_id)

    # Query the database for a user with the given user_id
    user_data = users_collection.find_one({'_id': user_id})

    # If user data is found, return a User instance
    if user_data:
        return User(user_data)

    # If no user is found, return None
    return None


# Route for home
@app.route('/')
def home():
    return render_template('index.html')

# Route for signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()  # Initialize the form
    if form.validate_on_submit():
        # Form submission handling
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # Check if the user already exists
        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            flash('Email already exists')
            return redirect(url_for('signup'))

        # Hash the password and save the new user
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password
        })

        flash('Account created! Please log in.')
        return redirect(url_for('login'))

    # Pass the form to the template
    return render_template('signup.html', form=form)

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Initialize the form
    if form.validate_on_submit():
        # Form submission handling
        email = form.email.data
        password = form.password.data
        
        # Find the user by email
        user_data = users_collection.find_one({'email': email})
        if user_data and check_password_hash(user_data['password'], password):
            # User authentication
            user_instance = User(user_data)
            login_user(user_instance)
            flash('Login successful!')
            return redirect(url_for('profile'))

        flash('Invalid email or password.')
        return redirect(url_for('login'))

    # Pass the form to the template
    return render_template('login.html', form=form)

# Route for logout
@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('home'))

indian_patient_names = [
    'Amit Sharma',
    'Priya Patel',
    'Rohit Singh',
    'Sneha Gupta',
    'Rahul Verma',
    'Pooja Rao',
    'Suresh Desai',
    'Neha Choudhury',
    'Deepak Khan',
    'Riya Reddy',
    'Vijay Sharma',
    'Anjali Patel',
    'Rajesh Singh',
    'Nisha Gupta',
    'Pradeep Verma',
    'Kavita Rao',
    'Anil Desai',
    'Shruti Choudhury',
    'Sandeep Khan',
    'Aarti Reddy'
]

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = MedicalInfoForm()
    user_id = current_user.get_id()  # Get current user's ID

    # Fetch medical information from the new cluster
    medical_info = medical_collection.find_one({'user_id': user_id})

    # Populate the form with existing data
    if request.method == 'GET':
        if medical_info:  # Check if medical_info is not None
            form.name.data = medical_info.get('name', '')
            form.age.data = medical_info.get('age', '')
            form.sex.data = medical_info.get('sex', '')
            form.blood_group.data = medical_info.get('blood_group', '')
            form.height.data = medical_info.get('height', '')
            form.weight.data = medical_info.get('weight', '')
            form.allergies.data = medical_info.get('allergies', '')
            form.diabetic_status.data = medical_info.get('diabetic_status', '')
        else:
            # If no medical information is found, populate form fields with empty strings
            form.name.data = ''
            form.age.data = ''
            form.sex.data = ''
            form.blood_group.data = ''
            form.height.data = ''
            form.weight.data = ''
            form.allergies.data = ''
            form.diabetic_status.data = ''

    # Handle form submission
    if form.validate_on_submit():
        # Update medical information in the new cluster
        medical_info_data = {
            'user_id': user_id,
            'name': form.name.data,
            'age': form.age.data,
            'sex': form.sex.data,
            'blood_group': form.blood_group.data,
            'height': form.height.data,
            'weight': form.weight.data,
            'allergies': form.allergies.data,
            'diabetic_status': form.diabetic_status.data,
        }
        
        # Update user's medical information in the new cluster
        medical_collection.update_one(
            {'user_id': user_id},
            {'$set': medical_info_data},
            upsert=True  # Use upsert=True to insert if it doesn't exist
        )
        
        flash('Medical information updated successfully!')
        return redirect(url_for('profile'))

    hospitals_info = [
        {
            'name': 'AIIMS (All India Institute of Medical Sciences)',
            'address': 'Ansari Nagar, New Delhi, Delhi 110029',
            'contact': '011 2658 8500',
            'description': 'AIIMS is a premier medical institution known for its world-class healthcare and medical research.'
        },
        {
            'name': 'Apollo Hospital',
            'address': 'Sarita Vihar, Mathura Rd, New Delhi, Delhi 110076',
            'contact': '011 2692 5858',
            'description': 'Apollo Hospital is a leading healthcare provider offering a wide range of medical services and specialties.'
        },
        {
            'name': 'Max Super Specialty Hospital',
            'address': '1, Press Enclave Rd, Mandir Marg, Saket, New Delhi, Delhi 110017',
            'contact': '011 2651 5050',
            'description': 'Max Hospital is known for its advanced medical facilities and high-quality patient care.'
        },
        {
            'name': 'Fortis Hospital',
            'address': 'B-22, Okhla Rd, New Delhi, Delhi 110025',
            'contact': '011 4713 4444',
            'description': 'Fortis Hospital provides comprehensive healthcare services with a strong focus on patient safety and care.'
        },
        {
            'name': 'Sir Ganga Ram Hospital',
            'address': 'Rajinder Nagar, New Delhi, Delhi 110060',
            'contact': '011 4225 5225',
            'description': 'Sir Ganga Ram Hospital is known for its medical expertise and state-of-the-art facilities.'
        },
        {
            'name': 'BLK Super Specialty Hospital',
            'address': 'Pusa Rd, Radial Road Number 6, New Delhi, Delhi 110005',
            'contact': '011 3040 3040',
            'description': 'BLK Hospital offers a wide range of specialized healthcare services with cutting-edge technology.'
        },
        {
            'name': 'Primus Super Specialty Hospital',
            'address': '2, Chandragupta Marg, Chanakyapuri, New Delhi, Delhi 110021',
            'contact': '011 6620 6620',
            'description': 'Primus Hospital is known for its world-class healthcare services and highly experienced medical staff.'
        },
        {
            'name': 'Moolchand Medcity Hospital',
            'address': 'Lajpat Nagar III, New Delhi, Delhi 110024',
            'contact': '011 4200 0000',
            'description': 'Moolchand Medcity Hospital offers top-notch healthcare facilities and a team of expert physicians.'
        },
        {
            'name': 'Holy Family Hospital',
            'address': 'Okhla Rd, Opposite Hari Nagar Ashram, New Delhi, Delhi 110025',
            'contact': '011 2683 6232',
            'description': 'Holy Family Hospital provides quality healthcare services and has a reputation for compassionate patient care.'
        },
        {
            'name': 'Indraprastha Apollo Hospital',
            'address': 'Mathura Rd, Sukhdev Vihar, New Delhi, Delhi 110076',
            'contact': '011 2692 5858',
            'description': 'Indraprastha Apollo Hospital is a multi-specialty hospital known for its excellence in medical care.'
        },
        {
            'name': 'Artemis Hospital',
            'address': 'Gurgaon, Delhi NCR',
            'contact': '0124 6767 767',
            'description': 'Artemis Hospital offers comprehensive healthcare services and advanced medical technology.'
        },
        {
            'name': 'Jaypee Hospital',
            'address': 'Noida, Delhi NCR',
            'contact': '0120 2470 300',
            'description': 'Jaypee Hospital provides top-quality medical care and advanced healthcare facilities.'
        },
        # Add more hospitals with details as needed
    ]    

    medications = [
        'Paracetamol',
        'Ibuprofen',
        'Amoxicillin',
        'Metformin',
        'Amlodipine',
        'Atorvastatin',
        'Cetirizine',
        'Azithromycin',
        'Losartan',
        'Omeprazole'
    ]
    
    # Randomly generate 30 prescriptions using Indian patient names
    prescriptions_list = []
    for i in range(30):
        prescription = {
            'patient_name': random.choice(indian_patient_names),
            'medication': random.choice(medications),
            'dosage': f'{random.randint(1, 2)} tablets',
            'frequency': f'{random.randint(1, 3)} times a day',
            'doctor_name': f'Dr. {random.choice(indian_patient_names).split()[0]}',
            'date': f'2024-0{random.randint(1, 9)}-{random.randint(1, 30)}'
        }
        prescriptions_list.append(prescription)
    return render_template('profile.html', form=form, user=current_user, hospitals_info=hospitals_info,prescriptions_list=prescriptions_list)


# Run the application
if __name__ == '__main__':
    app.run(debug=True)
