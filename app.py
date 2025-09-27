from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import json

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus_connect.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profiles'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'events'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'campus'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'projects'), exist_ok=True)

# Initialize SQLAlchemy
db.init_app(app)

# Import models after db initialization to avoid circular imports
from models import User, Student, Campus, Event, StudentProject

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'zip', 'rar'}

def save_profile_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{filename}"
        
        # Make sure images go inside /static/uploads/profiles
        save_path = os.path.join('static', 'uploads', 'profiles')
        os.makedirs(save_path, exist_ok=True)
        
        file_path = os.path.join(save_path, filename)
        file.save(file_path)

        return f"uploads/profiles/{filename}"  # Relative path inside static
    return None


def save_event_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{filename}"
        
        # Make sure images go inside /static/uploads/events
        save_path = os.path.join('static', 'uploads', 'events')
        os.makedirs(save_path, exist_ok=True)
        
        file_path = os.path.join(save_path, filename)
        file.save(file_path)

        return f"uploads/events/{filename}"  # Relative path inside static
    return None


def save_campus_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{filename}"
        
        # Make sure images go inside /static/uploads/campus
        save_path = os.path.join('static', 'uploads', 'campus')
        os.makedirs(save_path, exist_ok=True)
        
        file_path = os.path.join(save_path, filename)
        file.save(file_path)

        return f"uploads/campus/{filename}"  # Relative path inside static
    return None


def save_project_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{filename}"
        
        # Make sure files go inside /static/uploads/projects
        save_path = os.path.join('static', 'uploads', 'projects')
        os.makedirs(save_path, exist_ok=True)
        
        file_path = os.path.join(save_path, filename)
        file.save(file_path)

        return f"uploads/projects/{filename}"  # Relative path inside static
    return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password) and user.role == role:
            session['user_id'] = user.id
            session['role'] = user.role
            
            # Check if profile setup is needed
            if role == 'student':
                student = Student.query.filter_by(user_id=user.id).first()
                if not student or not student.first_name:
                    return redirect(url_for('profile_setup'))
                return redirect(url_for('student_dashboard'))
            else:
                campus = Campus.query.filter_by(user_id=user.id).first()
                if not campus or not campus.name:
                    return redirect(url_for('profile_setup'))
                return redirect(url_for('campus_dashboard'))
        else:
            flash('Invalid credentials or role. Please try again.')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        role = request.form.get('role')
        
        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('signup'))
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.')
            return redirect(url_for('signup'))
        
        # Create new user
        new_user = User(email=email, password=generate_password_hash(password), role=role)
        db.session.add(new_user)
        db.session.commit()
        
        # Create profile with required fields
        if role == 'student':
            new_profile = Student(user_id=new_user.id)
            db.session.add(new_profile)
        else:
            # Add a temporary name for Campus to satisfy NOT NULL constraint
            # This will be updated during profile setup
            new_profile = Campus(
                user_id=new_user.id,
                name="Pending Setup"  # Temporary name to satisfy NOT NULL constraint
            )
            db.session.add(new_profile)
        
        db.session.commit()
        
        # Log in the user and redirect to profile setup
        session['user_id'] = new_user.id
        session['role'] = role
        
        flash('Account created successfully! Please complete your profile.')
        return redirect(url_for('profile_setup'))
    
    return render_template('signup.html')

@app.route('/profile-setup', methods=['GET', 'POST'])
def profile_setup():
    if 'user_id' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        if session['role'] == 'student':
            student = Student.query.filter_by(user_id=user.id).first()
            
            # Update student profile
            student.first_name = request.form.get('first_name')
            student.last_name = request.form.get('last_name')
            student.bio = request.form.get('bio')
            student.university = request.form.get('university')
            student.field_of_study = request.form.get('field_of_study')
            student.graduation_year = request.form.get('graduation_year')
            student.skills = request.form.get('skills')
            student.location = request.form.get('location')
            student.linkedin = request.form.get('linkedin')
            student.github = request.form.get('github')
            # Handle profile image
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                image_path = save_profile_image(file)
                if image_path:
                    student.profile_image = image_path
            
            db.session.commit()
            flash('Profile setup completed!')
            return redirect(url_for('student_dashboard'))
        else:
            campus = Campus.query.filter_by(user_id=user.id).first()
            
            # Update campus profile
            campus.name = request.form.get('name')
            campus.description = request.form.get('description')
            campus.location = request.form.get('location')
            campus.website = request.form.get('website')
            campus.founded_year = request.form.get('founded_year')
            
            # Handle profile image
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                image_path = save_campus_image(file)
                if image_path:
                    campus.profile_image = image_path
            
            db.session.commit()
            flash('Campus profile setup completed!')
            return redirect(url_for('campus_dashboard'))
    
    return render_template('profile_setup.html', role=session['role'])
@app.route('/about')
def showabout():
    return render_template('about.html')

@app.route('/contact')
def showcontact():
    return render_template('contact.html')

@app.route('/student-dashboard/profile')
def student_profile():
    if 'user_id' not in session or session['role'] != 'student':
        flash('Please login as a student to access the profile.')
        return redirect(url_for('login'))
    
    # Get the student profile data
    student = Student.query.filter_by(user_id=session['user_id']).first()
    user = User.query.get(session['user_id'])

    # If profile is incomplete, redirect to profile setup
    if not student or not student.first_name:
        flash('Please complete your profile first.')
        return redirect(url_for('profile_setup'))
    
    # Fetch the student's projects
    projects = StudentProject.query.filter_by(student_id=student.id).all()
    
    # Add timestamp to prevent caching of profile images
    now = datetime.now().timestamp()
    
    
    return render_template('student_profile.html', student=student, user=user, projects=projects, now=now)

@app.route('/student-dashboard/profile/edit', methods=['GET', 'POST'])
def edit_student_profile():
    if 'user_id' not in session or session['role'] != 'student':
        flash('Please login as a student to edit your profile.')
        return redirect(url_for('login'))
    
    student = Student.query.filter_by(user_id=session['user_id']).first()
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        # Update student profile
        student.first_name = request.form.get('first_name')
        student.last_name = request.form.get('last_name')
        student.bio = request.form.get('bio')
        student.university = request.form.get('university')
        student.field_of_study = request.form.get('field_of_study')
        student.graduation_year = request.form.get('graduation_year')
        student.skills = request.form.get('skills')
        
        student.location = request.form.get('location')
        
        student.linkedin = request.form.get('linkedin')
        student.github = request.form.get('github')
        
        
        # Handle profile image
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            image_path = save_profile_image(file)
            if image_path:
                student.profile_image = image_path
        
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('student_profile'))
    
    return render_template('edit_student_profile.html', student=student, user=user)

@app.route('/campus-dashboard/profile')
def campus_profile():
    if 'user_id' not in session or session['role'] != 'campus':
        flash('Please login as a campus representative to access the profile.')
        return redirect(url_for('login'))
    
    # Get the campus profile data
    campus = Campus.query.filter_by(user_id=session['user_id']).first()
    user = User.query.get(session['user_id'])
    events = Event.query.filter_by(campus_id=campus.id).order_by(Event.date.desc()).all()
    
    # If profile is incomplete, redirect to profile setup
    if not campus or not campus.name:
        flash('Please complete your campus profile first.')
        return redirect(url_for('profile_setup'))
    now = datetime.now().timestamp()
    return render_template('campus_profile.html', campus=campus, user=user, events=events, now=now)

@app.route('/student-dashboard')
def student_dashboard():
    if 'user_id' not in session or session['role'] != 'student':
        flash('Please login as a student to access the dashboard.')
        return redirect(url_for('login'))
    
    student = Student.query.filter_by(user_id=session['user_id']).first()
    user = User.query.get(session['user_id'])
    

    # Get all events
    events = Event.query.order_by(Event.date.desc()).limit(6).all()
    
    # Get all campuses
    campuses = Campus.query.limit(4).all()
    
    return render_template('student_dashboard.html', student=student, events=events, campuses=campuses)

@app.route('/student-dashboard/resume')
def resume_builder():
    if 'user_id' not in session or session['role'] != 'student':
        flash('Please login as a student to access the resume builder.')
        return redirect(url_for('login'))
    
    student = Student.query.filter_by(user_id=session['user_id']).first()
    user = User.query.filter_by(id=session['user_id']).first()
    return render_template('resume_builder.html', student=student, user=user) 

@app.route('/student-dashboard/resume/download')
def download_resume():
    if 'user_id' not in session or session['role'] != 'student':
        flash('Please login as a student to download your resume.')
        return redirect(url_for('login'))
    
    # Logic to generate PDF will be handled by JavaScript on the client side 
    return redirect(url_for('resume_builder'))

@app.route('/search')
def search():
    if 'user_id' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))
    
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    
    students = []
    campuses = []
    events = []
    
    if query:
        if search_type in ['all', 'students']:
            students = Student.query.filter(
                (Student.first_name.contains(query)) | 
                (Student.last_name.contains(query)) |
                (Student.university.contains(query)) |
                (Student.field_of_study.contains(query))
            ).all()
        
        if search_type in ['all', 'campuses']:
            campuses = Campus.query.filter(
                (Campus.name.contains(query)) | 
                (Campus.location.contains(query)) |
                (Campus.description.contains(query))
            ).all()
        
        if search_type in ['all', 'events']:
            events = Event.query.filter(
                (Event.title.contains(query)) | 
                (Event.description.contains(query)) |
                (Event.event_type.contains(query)) |
                (Event.location.contains(query))
            ).all()
    
    return render_template('search.html', 
                          students=students, 
                          campuses=campuses, 
                          events=events, 
                          query=query,
                          search_type=search_type)

@app.route('/campus-dashboard')
def campus_dashboard():
    if 'user_id' not in session or session['role'] != 'campus':
        flash('Please login as a campus representative to access the dashboard.')
        return redirect(url_for('login'))
    
    campus = Campus.query.filter_by(user_id=session['user_id']).first()
    events = Event.query.filter_by(campus_id=campus.id).order_by(Event.date.desc()).all()
    
    return render_template('campus_dashboard.html', events=events, campus=campus)

@app.route('/campus-dashboard/event/add', methods=['GET', 'POST'])
def add_event():
    if 'user_id' not in session or session['role'] != 'campus':
        flash('Please login as a campus representative to add an event.')
        return redirect(url_for('login'))
    
    campus = Campus.query.filter_by(user_id=session['user_id']).first()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        event_type = request.form.get('event_type')
        date_str = request.form.get('date')
        location = request.form.get('location')
        form_url = request.form.get('form_url')
        
        # Convert date string to datetime
        try:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format.')
            return redirect(url_for('add_event'))
        
        new_event = Event(
            campus_id=campus.id,
            title=title,
            description=description,
            event_type=event_type,
            date=date,
            location=location,
            status='upcoming',
            form_url=form_url
        )
        
        # Handle event image
        if 'image' in request.files:
            file = request.files['image']
            image_path = save_event_image(file)
            if image_path:
                new_event.image = image_path
        
        db.session.add(new_event)
        db.session.commit()
        
        flash('Event added successfully!')
        return redirect(url_for('campus_dashboard'))
    
    # For GET requests, create an empty event object or pass None
    # Option 1: Create empty event object
    empty_event = {
        'title': '',
        'description': '',
        'event_type': '',
        'location': '',
        'form_url': '',
        'date': '',
        'status': 'upcoming'
    }
    
    return render_template('add_event.html', event=empty_event)

@app.route('/campus-dashboard/event/<int:event_id>/edit', methods=['GET', 'POST'])
def edit_event(event_id):
    if 'user_id' not in session or session['role'] != 'campus':
        flash('Please login as a campus representative to edit an event.')
        return redirect(url_for('login'))
    
    campus = Campus.query.filter_by(user_id=session['user_id']).first()
    event = Event.query.get_or_404(event_id)
    
    # Verify the event belongs to this campus
    if event.campus_id != campus.id:
        flash('You do not have permission to edit this event.')
        return redirect(url_for('campus_dashboard'))
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        event_type = request.form.get('event_type')
        location = request.form.get('location')
        status = request.form.get('status')
        form_url = request.form.get('form_url')
        date_str = request.form.get('date')
        
        # Validate required fields
        if not all([title, description, event_type, location, status, date_str]):
            flash('Please fill in all required fields.')
            return render_template('edit_event.html', event=event)
        
        # Convert date string to datetime
        try:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format. Please check the date and time.')
            return render_template('edit_event.html', event=event)
        
        try:
            # Update event fields
            event.title = title.strip()
            event.description = description.strip()
            event.event_type = event_type
            event.location = location.strip()
            event.status = status
            event.date = date
            event.form_url = form_url.strip() if form_url else None
            
            # Handle event image
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    image_path = save_event_image(file)
                    if image_path:
                        # Delete old image if it exists
                        if event.image:
                            try:
                                import os
                                old_image_path = os.path.join(app.static_folder, event.image)
                                if os.path.exists(old_image_path):
                                    os.remove(old_image_path)
                            except Exception as e:
                                print(f"Error deleting old image: {e}")
                        
                        event.image = image_path
            
            db.session.commit()
            flash('Event updated successfully!')
            return redirect(url_for('campus_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the event. Please try again.')
            print(f"Error updating event: {e}")
            return render_template('edit_event.html', event=event)
    
    # For GET requests, format the date for the datetime-local input
    if hasattr(event, 'date') and event.date:
        event.formatted_date = event.date.strftime('%Y-%m-%dT%H:%M')
    else:
        event.formatted_date = ''
    
    # Ensure form_url exists (for backward compatibility)
    if not hasattr(event, 'form_url'):
        event.form_url = None
    
    return render_template('edit_event.html', event=event)


# Also add the delete_event route if you don't have it already
@app.route('/campus-dashboard/event/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):
    if 'user_id' not in session or session['role'] != 'campus':
        flash('Please login as a campus representative to delete an event.')
        return redirect(url_for('login'))
    
    campus = Campus.query.filter_by(user_id=session['user_id']).first()
    event = Event.query.get_or_404(event_id)
    
    # Verify the event belongs to this campus
    if event.campus_id != campus.id:
        flash('You do not have permission to delete this event.')
        return redirect(url_for('campus_dashboard'))
    
    try:
        # Delete event image if it exists
        if event.image:
            try:
                import os
                image_path = os.path.join(app.static_folder, event.image)
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"Error deleting event image: {e}")
        
        # Delete the event
        db.session.delete(event)
        db.session.commit()
        
        flash('Event deleted successfully!')
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the event.')
        print(f"Error deleting event: {e}")
    
    return redirect(url_for('campus_dashboard'))

@app.route('/manage_registrations/<int:event_id>')
def manage_registrations(event_id):
    # Handle registration management
    pass

@app.route('/campus/<int:campus_id>')
def view_campus(campus_id):
    if 'user_id' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))
    
    campus = Campus.query.get_or_404(campus_id)
    events = Event.query.filter_by(campus_id=campus.id).order_by(Event.date.desc()).all()
    
    return render_template('view_campus.html', campus=campus, events=events)

@app.route('/student/<int:student_id>')
def view_student(student_id):
    if 'user_id' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))
    
    student = Student.query.get_or_404(student_id)
    
    return render_template('view_student.html', student=student)

@app.route('/event/<int:event_id>')
def view_event(event_id):
    if 'user_id' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))
    
    event = Event.query.get_or_404(event_id)
    campus = Campus.query.get(event.campus_id)
    
    return render_template('view_event.html', event=event, campus=campus)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.route('/student-dashboard/profile/upload_picture', methods=['POST'])
def upload_profile_picture():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    if 'profile_picture' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['profile_picture']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        if session['role'] == 'student':
            student = Student.query.filter_by(user_id=session['user_id']).first()
            if student:
                image_path = save_profile_image(file)
                if image_path:
                    student.profile_image = image_path
                    db.session.commit()
                    return jsonify({'success': True, 'image_path': image_path})
        else:
            campus = Campus.query.filter_by(user_id=session['user_id']).first()
            if campus:
                image_path = save_profile_image(file)
                if image_path:
                    campus.profile_image = image_path
                    db.session.commit()
                    return jsonify({'success': True, 'image_path': image_path})
    
    return jsonify({'error': 'Invalid file type or user not found'}), 400

@app.route('/student-dashboard/project/upload', methods=['POST'])
def upload_project():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    student = Student.query.filter_by(user_id=session['user_id']).first()
    
    title = request.form.get('title')
    description = request.form.get('description')
    
    if 'project_file' in request.files:
        file = request.files['project_file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join('uploads', 'projects', filename)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], 'projects', filename)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            file.save(full_path)
            
            project = StudentProject(
                student_id=student.id,
                title=title,
                description=description,
                file_path=file_path
            )
            db.session.add(project)
            db.session.commit()
            
            return jsonify({'success': True})
    
    return jsonify({'error': 'No file uploaded'}), 400

@app.route('/campus-dashboard/profile/upload_picture', methods=['POST'])
def upload_campus_profile_picture():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    if 'profile_picture' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['profile_picture']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        campus = Campus.query.filter_by(user_id=session['user_id']).first()
        if campus:
            image_path = save_campus_image(file)
            if image_path:
                campus.profile_image = image_path
                db.session.commit()
                return jsonify({'success': True, 'image_path': image_path})
    
    return jsonify({'error': 'Invalid file type'}), 400

# Add the missing route for edit_resume
@app.route('/student-dashboard/resume/edit', methods=['GET', 'POST'])
def edit_resume():
    if 'user_id' not in session or session['role'] != 'student':
        flash('Please login as a student to edit your resume.')
        return redirect(url_for('login'))
    
    student = Student.query.filter_by(user_id=session['user_id']).first()
    
    if request.method == 'POST':
        # Process the form data
        student.phone = request.form.get('phone')
        student.website = request.form.get('website')
        student.education = request.form.get('education')
        student.experience = request.form.get('experience')
        student.skills = request.form.get('skills')
        student.certifications = request.form.get('certifications')
        
        db.session.commit()

        flash('Resume updated successfully!')
        return redirect(url_for('resume_builder'))
    
    return render_template('edit_resume.html', student=student, user=User.query.get(session['user_id']))

@app.route('/download-project/<int:project_id>')
def download_project(project_id):
    if 'user_id' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))
    
    project = StudentProject.query.get_or_404(project_id)
    if project.file_path:
        return send_file(os.path.join('static', project.file_path), as_attachment=True)
    else:
        flash('No file available for this project.')
        return redirect(url_for('view_student', student_id=project.student_id))

# Add timestamp to template context for cache busting
@app.context_processor
def inject_now():
    return {'now': datetime.now().timestamp()}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
