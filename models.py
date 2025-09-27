
from extensions import db
from datetime import datetime
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student' or 'campus'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='user', uselist=False, cascade="all, delete-orphan")
    campus = db.relationship('Campus', backref='user', uselist=False, cascade="all, delete-orphan")

class StudentProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<StudentProject {self.title}>'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    bio = db.Column(db.Text)
    university = db.Column(db.String(100))
    field_of_study = db.Column(db.String(100))
    graduation_year = db.Column(db.Integer)
    profile_image = db.Column(db.String(255))
    skills = db.Column(db.String(500))  # Comma-separated list of skills
    
    # Contact information
    location = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    
    # Social links
    linkedin = db.Column(db.String(200))
    github = db.Column(db.String(200))
    
    # Resume data
    education = db.Column(db.Text)  # Store as JSON string
    experience = db.Column(db.Text)  # Store as JSON string
    certifications = db.Column(db.Text)  # Store as JSON string
    
    # Add relationship for projects
    projects = db.relationship('StudentProject', backref='student', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Student {self.first_name} {self.last_name}>'

class CampusPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campus_id = db.Column(db.Integer, db.ForeignKey('campus.id'), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CampusPhoto {self.id}>'

class Campus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    website = db.Column(db.String(200))
    founded_year = db.Column(db.Integer)
    profile_image = db.Column(db.String(200))
    
    # Relationships
    events = db.relationship('Event', backref='campus', lazy=True, cascade="all, delete-orphan")
    photos = db.relationship('CampusPhoto', backref='campus', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Campus {self.name}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campus_id = db.Column(db.Integer, db.ForeignKey('campus.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(50))  # Workshop, Conference, etc.
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    image = db.Column(db.String(200))
    status = db.Column(db.String(20), default='upcoming')  # upcoming, active, completed, canceled
    # Add this column to your Event model
    form_url = db.Column(db.String(200))  # URL for event registration or details
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Event {self.title}>'
