from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from bson.objectid import ObjectId  # Ensure you have this import for ObjectId

main = Blueprint('main', __name__)

@main.route('/')
def landing_page():
    return render_template('landing_page.html')

@main.route('/dashboard')
def dashboard():
    user = {'username': 'JohnDoe'}
    return render_template('dashboard.html', user=user)

@main.route('/internships')
def internships():
    return render_template('internships.html')

@main.route('/jobs')
def jobs():
    return render_template('jobs.html')

@main.route('/skillgap')
def skillgap():
    return render_template('skillgap.html')

@main.route('/learn')
def learn():
    return render_template('learn.html')

@main.route('/practice')
def practice():
    return render_template('practice.html')

@main.route('/compete')
def compete():
    return render_template('compete.html')

@main.route('/mentorship')
def mentorship():
    return render_template('mentorship.html')

@main.route('/profile', methods=['GET', 'POST'])
@jwt_required()
def user_profile():
    user_id = get_jwt_identity()
    user = current_app.mongo.db.users.find_one({'_id': ObjectId(user_id)})
    
    if request.method == 'POST':
        profile_info = request.form.get('profile_info')
        current_app.mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'profile_info': profile_info}}
        )
        return redirect(url_for('main.user_profile'))
    
    return render_template('profile.html', user=user)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = current_app.mongo.db.users.find_one({'email': email})

        if user and current_app.bcrypt.check_password_hash(user['password'], password):
            access_token = create_access_token(identity=str(user['_id']))
            response = redirect(url_for('main.dashboard'))
            response.set_cookie('access_token', access_token)
            return response
        
        flash('Invalid email or password')
        return redirect(url_for('main.login'))

    return render_template('login.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = current_app.bcrypt.generate_password_hash(password).decode('utf-8')
        
        existing_user = current_app.mongo.db.users.find_one({'email': email})
        if existing_user:
            flash('Email address already exists')
            return redirect(url_for('main.signup'))
        
        new_user = {
            'username': username,
            'email': email,
            'password': hashed_password
        }
        current_app.mongo.db.users.insert_one(new_user)
        
        flash('Signup successful! Please log in.')
        return redirect(url_for('main.login'))
    
    return render_template('signup.html')

@main.route('/analyze_skills', methods=['GET', 'POST'])
@jwt_required()
def analyze_skills():
    user_id = get_jwt_identity()
    user = {'username': 'JohnDoe'}

    skills = request.form.get('skills').split(", ")

    job_requirements = ["Python", "Flask", "MongoDB", "Docker", "Kubernetes"]

    missing_skills = list(set(job_requirements) - set(skills))

    recommendations = []
    for skill in missing_skills:
        recommendations.append({
            "skill": skill,
            "course": f"Learn {skill} on Udemy",
            "job": f"Apply for {skill}-related jobs"
        })

    return jsonify({
        "gap_analysis": missing_skills,
        "recommendations": recommendations
    })

@main.route('/saved_opportunities')
@jwt_required()
def saved_opportunities():
    # Add your logic here
    return render_template('saved_opportunities.html')

@main.route('/applications')
@jwt_required()
def applications():
    # Add your logic here
    return render_template('applications.html')

@main.route('/learning_progress')
@jwt_required()
def learning_progress():
    # Add your logic here
    return render_template('learning_progress.html')

@main.route('/competitions')
@jwt_required()
def competitions():
    # Add your logic here
    return render_template('competitions.html')

