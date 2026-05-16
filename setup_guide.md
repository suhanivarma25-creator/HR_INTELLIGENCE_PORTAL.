# Skill-Gap HR Intelligence Portal - Setup Guide

This project is a Flask-based web application that uses NLP to analyze job descriptions and provide a skill-gap analysis.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation Steps

1. **Install Dependencies**
   Open your terminal/command prompt and run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Seed the Database**
   Run the following command to create the database and populate it with sample data:
   ```bash
   python seed_db.py
   ```

3. **Run the Application**
   Start the Flask development server:
   ```bash
   python app.py
   ```

4. **Access the App**
   Open your browser and navigate to:
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Features

- **User Authentication**: Secure register and login system.
- **Job Search**: Search for job titles in the system's database.
- **Skill Extraction**: Uses NLP (NLTK) to find Hard and Soft skills from text.
- **Comparison Engine**: Compares your pasted job description/resume against the market standard.
- **Analytics Dashboard**: Visualizes your competitiveness score and skill distribution using Chart.js.
- **Insights**: Provides missing skills and salary estimates.

## File Structure

- `app.py`: Main Flask application core and routes.
- `models.py`: Database schema definitions (SQLAlchemy).
- `nlp_utils.py`: Text processing and skill extraction logic.
- `seed_db.py`: Script to populate the database with initial data.
- `templates/`: HTML files using Jinja2 templates.
- `static/css/style.css`: Custom styling for a premium look.
- `requirements.txt`: Python package dependencies.
