from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId
from datetime import timedelta
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import bcrypt
from flask_caching import Cache

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', '80e357a8449a0cd8ca642f0c0cc3b9fd6a3f45b62b09321422fd896dbe6b03e1')

# Initialize cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# MongoDB connection
client = MongoClient(os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client["Catalyst"]
users_collection = db["users"]
jobs_collection = db['jobs']
trainings_collection = db['trainings']


# Ensure unique index on users collection for username
users_collection.create_index([("username", ASCENDING)], unique=True)

# Initialize login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'

# Set session lifetime to a short duration to ensure sessions are not persisted
app.permanent_session_lifetime = timedelta(minutes=1)

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(str(user['_id']))
    return None

# Home/Landing Page (after login)
@app.route('/')
@login_required
@cache.cached(timeout=60)
def landing_page():
    return render_template('landing_page.html', username=current_user.id)

# Signup route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username already exists
        if users_collection.find_one({"username": username}):
            return "Username already exists"
        else:
            # Hash the password using bcrypt
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            # Store the hashed password in the database
            users_collection.insert_one({
                "username": username,
                "password": hashed_password
            })
            return redirect(url_for('login'))

    return render_template('register.html')



# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = users_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            login_user(User(str(user['_id'])))
            flash('Login successful!')
            return redirect(url_for('landing_page'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!')
    return redirect(url_for('login'))

# Profile page
@app.route('/profile')
@login_required
@cache.cached(timeout=60)
def profile():
    return render_template('profile.html')

# Internships page
@app.route('/internships')
@login_required
@cache.cached(timeout=60)
def internships():
    return render_template('internships.html')

# Jobs page
@app.route('/jobs')
@login_required
@cache.cached(timeout=60)
def jobs():
    return render_template('jobs.html')

# Learn page
@app.route('/learn')
@login_required
@cache.cached(timeout=60)
def learn():
    return render_template('learn.html')

# Practice page
@app.route('/practice')
@login_required
@cache.cached(timeout=60)
def practice():
    return render_template('practice.html')

# Compete page
@app.route('/compete')
@login_required
@cache.cached(timeout=60)
def compete():
    return render_template('compete.html')

# Mentorship page
@app.route('/mentorship')
@login_required
@cache.cached(timeout=60)
def mentorship():
    return render_template('mentorship.html')

# Dashboard page
@app.route('/dashboard')
@login_required
@cache.cached(timeout=60)
def dashboard():
    return render_template('dashboard.html')

def analyze_skill_gaps(user_skills, job_skills):
    skill_gaps = []
    for skill, required_proficiency in job_skills.items():
        user_proficiency = user_skills.get(skill, 'None')
        if user_proficiency != required_proficiency:
            skill_gaps.append({
                "skill": skill,
                "required": required_proficiency,
                "current": user_proficiency
            })
    return skill_gaps

def get_training_recommendations(skill_gaps):
    recommendations = []
    skills_needed = {gap['skill'] for gap in skill_gaps}
    for skill in skills_needed:
        trainings = trainings_collection.find({"skill": skill})
        for training in trainings:
            recommendations.append(training)
    return recommendations

@app.route('/skill_assessment', methods=['GET', 'POST'])
def skill_assessment():
    if request.method == 'POST':
        desired_role = request.form.get('desired_role')
        skills = request.form.getlist('skills[]')
        proficiencies = request.form.getlist('proficiencies[]')
        user_skills = dict(zip(skills, proficiencies))

        job = jobs_collection.find_one({"title": desired_role})
        if not job:
            flash("Desired role not found.")
            return redirect(url_for('skill_assessment'))

        job_skills = job.get("required_skills", {})
        skill_gaps = analyze_skill_gaps(user_skills, job_skills)
        recommendations = get_training_recommendations(skill_gaps)

        return render_template('skill_assessment.html', skill_gaps=skill_gaps, recommendations=recommendations)

    return render_template('skill_assessment.html')


# Main function to run the app
if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5001)))
