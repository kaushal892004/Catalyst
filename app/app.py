
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from pymongo import MongoClient , ASCENDING
from bson.objectid import ObjectId
from datetime import timedelta
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import bcrypt
from flask_caching import Cache
# from flask_wtf.csrf import CSRFProtect
# from flask_cors import CORS
import nltk
from nltk.tokenize import word_tokenize
import json
from bson.json_util import dumps
import datetime




# Initialize Flask app------------------------------------------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = 'your_secret_key'
# csrf = CSRFProtect(app)
# cors = CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'bfb04044e0d800ef68fef96b656c0b5c18cfba233f16c402566d9118bd6c1e3f')

# Initialize cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})


# ------------------------------------------------------------------------------------------------------------

# MongoDB connection------------------------------------------------------------------------------------------------------------
client = MongoClient(os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client["Catalyst"]
users_collection = db["users"]
jobs_collection = db['jobs']
trainings_collection = db['trainings']
skill_assessment_collection = db['skill_assessment']
skills_collection = db['skills']
courses_collection = db['courses']
resumes_collection = db['resumes']
catalyst_community_collection = db['catalyst_community']
discussions_collection = db['discussion']

# ------------------------------------------------------------------------------------------------------------

# Ensure unique index on users collection for username------------------------------------------------------------------------------------------------------------
users_collection.create_index([("username", ASCENDING)], unique=True)

# ------------------------------------------------------------------------------------------------------------

# Initialize login manager------------------------------------------------------------------------------------------------------------
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'

# ------------------------------------------------------------------------------------------------------------

# Set session lifetime to a short duration to ensure sessions are not persisted------------------------------------------------------------------------------------------------------------
app.permanent_session_lifetime = timedelta(minutes=5)

# ------------------------------------------------------------------------------------------------------------

# User model for Flask-Login------------------------------------------------------------------------------------------------------------
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            self.username = user.get('username', 'N/A')
            self.skills = user.get('skills', [])
            self.certifications = user.get('certifications', [])
            self.badges = user.get('badges', [])
            self.skill_score = user.get('skill_score', 0)  # Assuming you have skill_score in your user document
        else:
            self.username = 'N/A'
            self.skills = []
            self.certifications = []
            self.badges = []
            self.skill_score = 0

@login_manager.user_loader
def load_user(user_id):
    # Fetch user from the database and return the User object
    return User(user_id)

# ------------------------------------------------------------------------------------------------------------

# Function to create a unique cache key per user------------------------------------------------------------------------------------------------------------
def make_cache_key(*args, **kwargs):
    return f"{current_user.get_id()}_{request.path}"

# ------------------------------------------------------------------------------------------------------------

# Home/Landing Page (after login)------------------------------------------------------------------------------------------------------------
# @app.route('/')
# @login_required
# @cache.cached(timeout=300, key_prefix=make_cache_key)
# def landing_page():
#     return render_template('landing_page.html')

# ------------------------------------------------------------------------------------------------------------

# Signup route------------------------------------------------------------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username already exists
        if users_collection.find_one({"username": username}):
            flash("Username already exists")
            return redirect(url_for('register'))

        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store the user data in the database with default fields for skills, certifications, and badges
        users_collection.insert_one({
            "username": username,
            "password": hashed_password,
            "skills": [],  # Empty list of skills initially
            "certifications": [],  # Empty list of certifications
            "badges": [],  # Empty list of badges
            "skill_score": 0  # Initialize skill_score if needed
        })

        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html')

# ------------------------------------------------------------------------------------------------------------

# Login route------------------------------------------------------------------------------------------------------------
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     # If the user is already authenticated, redirect them to the landing page
#     if current_user.is_authenticated:
#         return redirect(url_for('landing_page'))

#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password').encode('utf-8')  # Encoding password for bcrypt check

#         # Query user from the database
#         user = users_collection.find_one({"username": username})

#         # Check if the user exists and if the password matches
#         if user and bcrypt.checkpw(password, user['password']):
#             user_obj = User(str(user['_id']))  # Instantiate User with the user ID
#             login_user(user_obj)  # Log the user in with Flask-Login
#             flash('Login successful!', 'success')
#             return redirect(url_for('landing_page'))  # Redirect to the landing page after login

#         else:
#             flash('Invalid username or password', 'danger')  # Show flash message on login failure

#     return render_template('login.html')  # Render login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('landing_page'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password').encode('utf-8')  # Encoding password for bcrypt check

        # Query user from the database
        user = users_collection.find_one({"username": username})

        # Check if the user exists and if the password matches
        if user and bcrypt.checkpw(password, user['password']):
            user_obj = User(str(user['_id']))  # Instantiate User with the user ID
            login_user(user_obj)  # Log the user in with Flask-Login
            flash('Login successful!', 'success')
            return redirect(url_for('landing_page'))  # Redirect to the landing page after login

        else:
            flash('Invalid username or password', 'danger')  # Show flash message on login failure

    return render_template('login.html')  # Render login page

# ------------------------------------------------------------------------------------------------------------

# Logout route------------------------------------------------------------------------------------------------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!')
    return redirect(url_for('login'))

# ------------------------------------------------------------------------------------------------------------

@app.route('/')
def landing_page():
    return render_template('landing_page.html')

# Profile page to display user information-----------------------------------------------------------------------
# @app.route('/profile')
# @login_required
# def profile():
#     user = users_collection.find_one({"_id": ObjectId(current_user.id)})
#     if user:
#         # Ensure the profile is updated with the latest skills
#         current_user.skills = user.get('skills', [])
#         current_user.certifications = user.get('certifications', [])
#         current_user.badges = user.get('badges', [])
#         current_user.skill_score = user.get('skill_score', 0)  # Assuming you have skill_score field
#     return render_template('profile.html')


# ------------------------------------------------------------------------------------------------------------

# Internships page------------------------------------------------------------------------------------------------------------
@app.route('/internships')
@login_required
@cache.cached(timeout=300, key_prefix=make_cache_key)
def internships():
    return render_template('internships.html')

# ------------------------------------------------------------------------------------------------------------

# Jobs page------------------------------------------------------------------------------------------------------------
@app.route('/jobs')
@login_required
@cache.cached(timeout=300, key_prefix=make_cache_key)
def jobs():
    return render_template('jobs.html')

# ------------------------------------------------------------------------------------------------------------

# Learn page------------------------------------------------------------------------------------------------------------
@app.route('/learn')
@login_required
@cache.cached(timeout=300, key_prefix=make_cache_key)
def learn():
    return render_template('learn.html')

# ------------------------------------------------------------------------------------------------------------

# Practice page------------------------------------------------------------------------------------------------------------
@app.route('/practice')
@login_required
@cache.cached(timeout=300, key_prefix=make_cache_key)
def practice():
    return render_template('practice.html')

# ------------------------------------------------------------------------------------------------------------

# Compete page------------------------------------------------------------------------------------------------------------
@app.route('/compete')
@login_required
@cache.cached(timeout=300, key_prefix=make_cache_key)
def compete():
    return render_template('compete.html')

# ------------------------------------------------------------------------------------------------------------

# Mentorship page------------------------------------------------------------------------------------------------------------
@app.route('/mentorship')
@login_required
@cache.cached(timeout=300, key_prefix=make_cache_key)
def mentorship():
    return render_template('mentorship.html')

# ------------------------------------------------------------------------------------------------------------

# Dashboard page------------------------------------------------------------------------------------------------------------
# @app.route('/dashboard')
# @login_required
# @cache.cached(timeout=300, key_prefix=make_cache_key)
# def dashboard():
#     return render_template('dashboard.html')

# ---------------------------------------------------------------------------------------------------------------------------

# # Routes For The skill_assessment------------------------------------------------------------------------------------------
# def analyze_skill_gaps(user_skills, job_skills):
#     skill_gaps = []
#     for skill, required_proficiency in job_skills.items():
#         user_proficiency = user_skills.get(skill, 'None')
#         if user_proficiency != required_proficiency:
#             skill_gaps.append({
#                 "skill": skill,
#                 "required": required_proficiency,
#                 "current": user_proficiency
#             })
#     return skill_gaps

# def get_training_recommendations(skill_gaps):
#     recommendations = []
#     skills_needed = {gap['skill'] for gap in skill_gaps}
#     for skill in skills_needed:
#         trainings = trainings_collection.find({"skill": skill})
#         for training in trainings:
#             recommendations.append(training)
#     return recommendations

# @app.route('/skill_assessment', methods=['GET', 'POST'])
# @login_required
# def skill_assessment():
#     if request.method == 'POST':
#         desired_role = request.form.get('desired_role')
#         skills = request.form.getlist('skills[]')
#         proficiencies = request.form.getlist('proficiencies[]')
#         user_skills = dict(zip(skills, proficiencies))

#         job = jobs_collection.find_one({"title": desired_role})
#         if not job:
#             flash("Desired role not found.")
#             return redirect(url_for('skill_assessment'))

#         job_skills = job.get("required_skills", {})
#         skill_gaps = analyze_skill_gaps(user_skills, job_skills)
#         recommendations = get_training_recommendations(skill_gaps)

#         return render_template('skill_assessment.html', skill_gaps=skill_gaps, recommendations=recommendations)

#     return render_template('skill_assessment.html')

# ---------------------------------------------------------------------------------------------------------------------------

# 
# Mock function to get MCQ questions based on job role and skills

# Mock data for MCQ questions per role
# mcq_data = {
#     'Software Engineer': [
#         {
#             'question': 'Which programming language is mainly used in system-level programming?',
#             'options': ['Python', 'Java', 'C', 'Ruby'],
#             'correct': 'C'
#         },
#         {
#             'question': 'What does OOP stand for?',
#             'options': ['Object-Oriented Programming', 'Online Operating Process', 'Open Object Protocol'],
#             'correct': 'Object-Oriented Programming'
#         }
#     ],
#     'Data Scientist': [
#         {
#             'question': 'Which of the following is a supervised learning algorithm?',
#             'options': ['K-Means', 'Linear Regression', 'DBSCAN'],
#             'correct': 'Linear Regression'
#         },
#         {
#             'question': 'Which library is commonly used for data manipulation?',
#             'options': ['NumPy', 'Pandas', 'Matplotlib'],
#             'correct': 'Pandas'
#         }
#     ],
#     'Web Developer': [
#         {
#             'question': 'What does HTML stand for?',
#             'options': ['HyperText Markup Language', 'HighText Markup Language', 'HyperText Machine Language'],
#             'correct': 'HyperText Markup Language'
#         },
#         {
#             'question': 'Which CSS property controls the text size?',
#             'options': ['font-size', 'text-size', 'font-style'],
#             'correct': 'font-size'
#         }
#     ],
#     'Cybersecurity Analyst': [
#         {
#             'question': 'Which encryption technique is more secure?',
#             'options': ['Symmetric Key Encryption', 'Asymmetric Key Encryption'],
#             'correct': 'Asymmetric Key Encryption'
#         },
#         {
#             'question': 'What does VPN stand for?',
#             'options': ['Virtual Public Network', 'Virtual Private Network', 'Variable Public Network'],
#             'correct': 'Virtual Private Network'
#         }
#     ]
# }

# # Route for the skill assessment page
# @app.route('/skill_assessment', methods=['GET', 'POST'])
# def skill_assessment():
#     if request.method == 'GET':
#         return render_template('skill_assessment.html')
    
#     # Handle job role selection and skills entry
#     if request.method == 'POST':
#         job_role = request.form.get('job_role')
#         skills = request.form.get('skills')
        
#         # Save job role and skills in session
#         session['job_role'] = job_role
#         session['skills'] = skills
        
#         # Redirect to MCQ section after job role selection
#         return redirect(url_for('skill_assessment_questions'))


# # Route to fetch MCQ questions based on the selected job role
# @app.route('/fetch_mcq_questions', methods=['POST'])
# def fetch_mcq_questions():
#     # Get job role and skills from session
#     job_role = session.get('job_role')
    
#     # Fetch corresponding MCQ questions
#     questions = mcq_data.get(job_role, [])
    
#     # Return questions as JSON
#     return jsonify({'questions': questions})


# # Route to handle the skill assessment question submission and scoring
# @app.route('/submit_answers', methods=['POST'])
# def submit_answers():
#     answers = request.form.to_dict()  # Get the answers from the form
#     job_role = session.get('job_role')
    
#     # Fetch the correct answers for the selected role
#     questions = mcq_data.get(job_role, [])
#     score = 0
#     total_questions = len(questions)
    
#     # Calculate the user's score
#     for i, question in enumerate(questions):
#         user_answer = answers.get(f'q{i}')
#         correct_answer = question['correct']
#         if user_answer == correct_answer:
#             score += 1
    
#     # Determine if the score is above or below the threshold
#     threshold = total_questions // 2  # Define passing criteria (50% correct answers)
    
#     # If the score is below the threshold, recommend courses
#     if score < threshold:
#         # Example course recommendations (modify as needed)
#         recommended_courses = ['Introduction to Data Structures', 'Advanced Algorithms', 'Object-Oriented Programming']
#         return jsonify({
#             'score': score,
#             'totalQuestions': total_questions,
#             'threshold': threshold,
#             'courses': recommended_courses
#         })
#     else:
#         # If the score is above the threshold, no courses are recommended
#         return jsonify({
#             'score': score,
#             'totalQuestions': total_questions,
#             'threshold': threshold
#         })
# Render the skills assessment page
@app.route('/skills_assessment', methods=['GET'])
def skills_assessment():
    return render_template('skills_assessment.html')

# Handle job role submission
@app.route('/submit_job_role', methods=['POST'])
def submit_job_role():
    job_role = request.form.get('job_role')
    return jsonify({"message": f"Job role {job_role} selected!"})

# Handle skills submission and return MCQ questions based on skills
@app.route('/fetch_mcq_questions', methods=['POST'])
def fetch_mcq_questions():
    data = request.get_json()
    job_role = data['job_role']
    skills = data['skills']

    # Logic to fetch MCQ questions based on job role and skills
    questions = [
        {"question": "What is the time complexity of binary search?", "options": ["O(log n)", "O(n)", "O(n^2)", "O(1)"]},
        {"question": "Which data structure is used for LRU cache?", "options": ["LinkedList", "HashMap", "Stack", "Queue"]}
    ]

    return jsonify({"questions": questions})

# Handle MCQ answers and calculate score
@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    answers = request.form.to_dict()

    # Logic to calculate score
    correct_answers = {"q0": "O(log n)", "q1": "HashMap"}
    score = sum(1 for q, a in answers.items() if correct_answers.get(q) == a)

    total_questions = len(correct_answers)
    threshold = total_questions * 0.7
    recommended_courses = ["Advanced Algorithms", "Data Structures Masterclass"] if score < threshold else []

    return jsonify({"score": score, "totalQuestions": total_questions, "threshold": threshold, "courses": recommended_courses})







# ---------------------------------------------------------------------------------------------------------------------------

# profile page
@app.route('/profile', methods=['GET', 'POST'])
@login_required
@cache.cached(timeout=300, key_prefix=make_cache_key)
def profile():
    if request.method == 'POST':
        data = request.get_json()
        user_id = ObjectId(current_user.id)

        # Ensure the 'users' collection is accessed correctly
        users_collection = db["users"]

        users_collection.update_one(
            {"_id": user_id},
            {"$set": {
                "full_name": data.get('full_name', ''),
                "email": data.get('email', ''),
                "location": data.get('location', ''),
                "desired_role": data.get('desired_role', ''),
                "bio": data.get('bio', ''),
                "skills": data.get('skills', []),
                "experience": data.get('experience', '')
            }}
        )
        return jsonify({"message": "Profile updated successfully"}), 200

    users_collection = db["users"]
    user = users_collection.find_one({"_id": ObjectId(current_user.id)})
    if user:
        return render_template('profile.html', user=user)
    else:
        return "User not found", 404


@app.route('/')
@cache.cached(timeout=300, key_prefix=make_cache_key)
def home():
    return render_template('landing_page.html')


#ChatBot Route-------------------------------------------------------------------------------------------------------------

class ChatBot:
    def __init__(self, knowledge_base_file='knowledge_base.json'):
        self.knowledge_base_file = knowledge_base_file
        try:
            with open(self.knowledge_base_file, 'r') as f:
                self.knowledge_base = json.load(f)
        except FileNotFoundError:
            self.knowledge_base = {}
        
        # Variable to track the last question asked for learning purposes
        self.awaiting_response_for = None

    def learn_and_respond(self, user_input):
        # If we are waiting for a response to a previous question
        if self.awaiting_response_for:
            # Teach the bot the response to the last question
            self.teach_response(self.awaiting_response_for, user_input)
            self.awaiting_response_for = None  # Reset awaiting response flag
            return "Thank you! I've learned a new response."

        response = self.find_response(user_input)
        if response is None:
            # If no response is found, ask for the response to learn
            self.awaiting_response_for = user_input  # Set the question to wait for response
            return "I don't have a response. Please teach me a response."
        return response

    def find_response(self, user_input):
        for question in self.knowledge_base.get('questions', []):
            if question['question'].lower() == user_input.lower():
                return question['response']
        return None

    def teach_response(self, user_input, response):
        # Check if the question already exists, and update it instead of adding a duplicate
        for question in self.knowledge_base.get('questions', []):
            if question['question'].lower() == user_input.lower():
                question['response'] = response
                self.save_knowledge_base()
                return
        
        # Otherwise, add a new question-response pair
        new_question = {'question': user_input.lower(), 'response': response}
        if 'questions' not in self.knowledge_base:
            self.knowledge_base['questions'] = []
        self.knowledge_base['questions'].append(new_question)
        self.save_knowledge_base()

    def save_knowledge_base(self):
        with open(self.knowledge_base_file, 'w') as f:
            json.dump(self.knowledge_base, f, indent=4)  # Indent for pretty formatting

chatbot = ChatBot()

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    response = chatbot.learn_and_respond(user_message)
    return jsonify({'response': response})


# ---------------------------------------------------------------------------------------------------------------------------


# Route to render the courses page
@app.route('/courses')
@cache.cached(timeout=300, key_prefix=make_cache_key)
def courses_page():
    return render_template('courses.html')

# API endpoint to fetch filtered courses dynamically
@app.route('/api/courses', methods=['GET'])
@login_required
@cache.cached(timeout=300, key_prefix=make_cache_key)
def fetch_courses():
    subject = request.args.get('subject', 'all')
    role = request.args.get('role', 'all')

    query = {}
    if subject != 'all':
        query['subject'] = subject
    if role != 'all':
        query['roles'] = role

    courses = list(courses_collection.find(query))
    for course in courses:
        course['_id'] = str(course['_id'])  # Convert ObjectId to string

    return jsonify(courses)


#Dashboard routes -----------------------------------------------------------
@app.route('/dashboard')
@login_required
@cache.cached(timeout=300, key_prefix=make_cache_key)
def dashboard():
    try:
        user_id = current_user.get_id()  # Get the user ID from Flask-Login
        
        # Convert user_id to ObjectId if necessary
        if not ObjectId.is_valid(user_id):
            return redirect(url_for('landing_page'))
        
        user_id = ObjectId(user_id)
        user_collection = db.users  # Your MongoDB collection for users

        user_data = user_collection.find_one({"_id": user_id})
        if user_data is None:
            return redirect(url_for('landing_page'))  # Handle the case where user data is not found

        # Prepare data for rendering
        skill_assessment = {
            'skills_and_proficiencies': [
                # Example data
                ('Python', 80),
                ('Django', 70),
                ('Flask', 60),
            ]
        }

        return render_template('dashboard.html', user=user_data, skill_assessment=skill_assessment)
    
    except Exception as e:
        print(f"Error fetching user data: {e}")
        return redirect(url_for('landing_page'))

# -------------------------------------------------------------------------------


# # resume route------------------------------------------------------------------------------------------------------------
# @app.route('/resume')
# @login_required
# @cache.cached(timeout=300, key_prefix=make_cache_key)
# def resume():
#     return render_template('resume.html')



# # -------------------------------------------------------------------------------


# Resume Route-------------------------------------------------------------------------------

@app.route('/resume', methods=['GET'])
@login_required
@cache.cached(timeout=300, key_prefix=make_cache_key)
def resume():
    return render_template('resume.html')

@app.route('/save-resume', methods=['POST'])
def save_resume():
    data = request.json
    # Insert the resume data into MongoDB
    try:
        resumes_collection.insert_one(data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/view-resume/<email>', methods=['GET'])
def view_resume(email):
    # Fetch resume data by email
    resume = resumes_collection.find_one({'email': email})
    if resume:
        return render_template('view_resume.html', resume=resume)
    else:
        return "Resume not found", 404
    
# -----------------------------------------------------------------------------------------------------------------------

# Community and peer support route ---------------------------------------------------------------------------------------

@app.route('/community', methods=['GET'])
@login_required
@cache.cached(timeout=300, key_prefix=make_cache_key)
def community():
    return render_template('community.html')    

# Route to display the Community & Peer Support page
@app.route('/community', methods=['GET'])
@login_required
@cache.cached(timeout=300, key_prefix=make_cache_key)
def community_page():
    discussions = db.discussions.find()  # Assuming discussions is a MongoDB collection
    
    # Pass discussions to the template
    return render_template('community.html', discussions=discussions)

# Route to handle form submission via AJAX
@app.route('/community/post_discussion', methods=['POST'])
@login_required
@cache.cached(timeout=300, key_prefix=make_cache_key)
def post_discussion():
    data = request.get_json()

    # Insert the discussion into the MongoDB collection
    new_discussion = {
        "user_name": data['user_name'],
        "user_email": data['user_email'],
        "discussion": data['discussion'],
        "posted_at": datetime.utcnow()
    }

    # Insert into MongoDB
    discussions_collection.insert_one(new_discussion)
    
    return jsonify({"status": "success", "message": "Discussion posted successfully!"})

# Route to fetch recent discussions
@app.route('/community/get_discussions', methods=['GET'])
@login_required
@cache.cached(timeout=300, key_prefix=make_cache_key)
def get_discussions():
    discussions = list(discussions_collection.find().sort('posted_at', -1))  # Sort by the latest
    for discussion in discussions:
        discussion['_id'] = str(discussion['_id'])  # Convert ObjectId to string for JSON compatibility
    return jsonify(discussions)

@app.route('/delete-discussion/<discussion_id>', methods=['DELETE'])
@login_required
@cache.cached(timeout=300, key_prefix=make_cache_key)
def delete_discussion(discussion_id):
    try:
        # Find the discussion by its ObjectId and delete it
        result = db.discussions.delete_one({'_id': ObjectId(discussion_id)})
        
        if result.deleted_count == 1:
            return jsonify({'success': True, 'message': 'Discussion deleted successfully'}), 200
        else:
            return jsonify({'success': False, 'message': 'Discussion not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
# -----------------------------------------------------------------------------------------------------------------------

#roadmap route -------------------------------------------------------------------------------------------

# @app.route('/adaptive_learning')
# @login_required
# @cache.cached(timeout=300, key_prefix=make_cache_key)
# def adaptive_learning():
#     return render_template('adaptive_learning.html')
@app.route('/adaptive_learning')
def adaptive_learning():
    course_name = request.args.get('course_name')
    
    # Pass the course_name to the template
    return render_template('adaptive_learning.html', selected_course=course_name)
@app.route('/roadmap')
def roadmap():
    course = request.args.get('course')
    return render_template('adaptive_learning.html', course=course)

# -----------------------------------------------------------------------------------------

#skill certifiaction and verifiaction route -------------------------------------------------------------------------------------------

@app.route('/skills-verification')
@login_required
@cache.cached(timeout=300, key_prefix=make_cache_key)
def skills_verification():
    return render_template('skills_verification.html')

# @app.route('/assessment')
# @login_required
# @cache.cached(timeout=300, key_prefix=make_cache_key)
# def assessment():
#     subject = request.args.get('subject')
#     return render_template('assessment.html', subject=subject)

@app.route('/view-certification')
def view_certification():
    subject = request.args.get('subject')
    # Logic to display certification for the subject
    return render_template('certification.html', subject=subject)

@app.route('/view-badge')
def view_badge():
    badge = request.args.get('badge')
    # Logic to display badge for the specific skill
    return render_template('badge.html', badge=badge)

# -----------------------------------------------------------------------------------------

@app.route('/aws')
def aws():
    return render_template('aws.html')
@app.route('/kafka')
def kafka():
    return render_template('kafka.html')
@app.route('/docker')
def docker():
    return render_template('docker.html')
@app.route('/kubernetes')
def kubernetes():
    return render_template('kubernetes.html')

@app.route('/python')
def python():
    return render_template('python.html')









if __name__ == '__main__':
    app.run(debug=True, port=5002)
