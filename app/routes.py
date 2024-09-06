from flask import Blueprint, render_template , request , redirect

main = Blueprint('main', __name__)

@main.route('/')
def landing_page():
    return render_template('landing_page.html')

@main.route('/dashboard')
def dashboard():
    # Replace `user` with actual user data fetching logic
    user = {'username': 'JohnDoe'}
    return render_template('dashboard.html', user=user)

@main.route('/internships')
def internships():
    # Replace with actual logic to get internship data
    return render_template('internships.html')

@main.route('/jobs')
def jobs():
    return render_template('jobs.html')

@main.route('/learn')
def learn():
    # Replace with actual logic to get learning resources
    return render_template('learn.html')

@main.route('/practice')
def practice():
    # Replace with actual logic to get practice resources
    return render_template('practice.html')

@main.route('/compete')
def compete():
    # Replace with actual logic to get competition data
    return render_template('compete.html')

@main.route('/mentorship')
def mentorship():
    # Replace with actual logic to get mentorship data
    return render_template('mentorship.html')

@main.route('/profile')
def profile():
    return render_template('profile.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic here
        return redirect(url_for('profile'))  # Redirect to profile or any other page after login
    return render_template('login.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle signup logic here
        return redirect(url_for('profile'))  # Redirect to profile or any other page after signup
    return render_template('signup.html')