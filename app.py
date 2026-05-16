from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, Job, Skill
from nlp_utils import extract_skills, calculate_competitiveness, extract_text_from_file
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skillgap.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already registered.')
            return redirect(url_for('register'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your email and password.')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.name)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    jobs = []
    if request.method == 'POST':
        job_title = request.form.get('job_title')
        jobs = Job.query.filter(Job.job_title.contains(job_title)).all()
    return render_template('search.html', jobs=jobs)

@app.route('/compare/<int:job_id>', methods=['GET', 'POST'])
@login_required
def compare(job_id):
    market_job = Job.query.get_or_404(job_id)
    if request.method == 'POST':
        user_jd = request.form.get('user_jd', '').strip()
        
        # Check if a file was uploaded
        uploaded_file = request.files.get('resume_file')
        if uploaded_file and uploaded_file.filename:
            extracted_text = extract_text_from_file(uploaded_file)
            if extracted_text:
                user_jd = extracted_text
            else:
                flash('Could not read the uploaded file. Please try pasting your text instead.')
                return redirect(url_for('compare', job_id=job_id))
        
        if not user_jd:
            flash('Please paste your text or upload a resume file.')
            return redirect(url_for('compare', job_id=job_id))
        
        # Get predefined skills for matching
        all_skills = Skill.query.all()
        hard_skills = [s.skill_name.lower() for s in all_skills if s.type == 'Hard']
        soft_skills = [s.skill_name.lower() for s in all_skills if s.type == 'Soft']
        
        # Extract skills from user JD
        user_hard, user_soft = extract_skills(user_jd, hard_skills, soft_skills)
        user_all = user_hard + user_soft
        
        # Extract skills from market JD
        market_hard, market_soft = extract_skills(market_job.description, hard_skills, soft_skills)
        market_all = market_hard + market_soft
        
        # Calculations
        score = calculate_competitiveness(user_all, market_all)
        missing_skills = [s for s in market_all if s not in user_all]
        
        # Dynamic Certification Mapping
        skill_cert_map = {
            'aws': {"name": "AWS Certified Cloud Practitioner", "url": "https://aws.amazon.com/certification/certified-cloud-practitioner/"},
            'azure': {"name": "Microsoft Certified: Azure Fundamentals", "url": "https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/"},
            'python': {"name": "PCAP – Certified Associate in Python Programming", "url": "https://pythoninstitute.org/pcap"},
            'javascript': {"name": "Meta Front-End Developer Certificate", "url": "https://www.coursera.org/professional-certificates/meta-front-end-developer"},
            'react': {"name": "Meta Front-End Developer Certificate", "url": "https://www.coursera.org/professional-certificates/meta-front-end-developer"},
            'sql': {"name": "Google Data Analytics Professional", "url": "https://grow.google/certificates/data-analytics/"},
            'machine learning': {"name": "Google Machine Learning Professional", "url": "https://cloud.google.com/learn/certification/machine-learning-engineer"},
            'cybersecurity': {"name": "CompTIA Security+", "url": "https://www.comptia.org/certifications/security"},
            'scrum': {"name": "Certified ScrumMaster (CSM)", "url": "https://www.scrumalliance.org/get-certified/scrum-master-track/certified-scrummaster"},
            'project management': {"name": "Google Project Management Certificate", "url": "https://grow.google/certificates/project-management/"},
            'seo': {"name": "HubSpot SEO Certification", "url": "https://academy.hubspot.com/courses/seo-training"},
            'docker': {"name": "Docker Certified Associate", "url": "https://training.mirantis.com/certification/dca-certification-exam-study-guide/"},
            'kubernetes': {"name": "CKAD: Certified Kubernetes Application Developer", "url": "https://training.linuxfoundation.org/certification/certified-kubernetes-application-developer-ckad/"},
            'tensorflow': {"name": "TensorFlow Developer Certificate", "url": "https://www.tensorflow.org/certificate"}
        }

        suggested_certs = []
        added_cert_names = set()

        # Suggest based on missing skills
        for skill in missing_skills:
            skill_lower = skill.lower()
            if skill_lower in skill_cert_map:
                cert = skill_cert_map[skill_lower]
                if cert['name'] not in added_cert_names:
                    suggested_certs.append(cert)
                    added_cert_names.add(cert['name'])

        # Fallback if no specific certs found or too few
        if len(suggested_certs) < 2:
            defaults = [
                {"name": "Google Professional Skills", "url": "https://grow.google/certificates/"},
                {"name": "LinkedIn Learning Path", "url": "https://www.linkedin.com/learning/"}
            ]
            for d in defaults:
                if d['name'] not in added_cert_names and len(suggested_certs) < 3:
                    suggested_certs.append(d)
                    added_cert_names.add(d['name'])
        
        # Limit to 3-5 certs
        certifications = suggested_certs[:4]
        
        # Determine theme color based on job title
        job_lower = market_job.job_title.lower()
        if 'data' in job_lower or 'ml' in job_lower or 'ai' in job_lower:
            theme_color = "#6366f1" # Indigo for Data/AI
        elif 'web' in job_lower or 'frontend' in job_lower or 'backend' in job_lower:
            theme_color = "#10b981" # Emerald for Web
        elif 'security' in job_lower or 'cyber' in job_lower:
            theme_color = "#f43f5e" # Rose for Security
        else:
            theme_color = "#3b82f6" # Blue default
            
        salary_estimate = "₹8,50,000 - ₹18,00,000"
        
        return render_template('results.html', 
                               score=score, 
                               user_skills=user_all, 
                               market_skills=market_all,
                               missing_skills=missing_skills,
                               certifications=certifications,
                               salary=salary_estimate,
                               job_title=market_job.job_title,
                               theme_color=theme_color)
                               
    return render_template('compare.html', job=market_job)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
