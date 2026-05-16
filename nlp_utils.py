import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('stopwords')

def preprocess_text(text):
    # Lowercase
    text = text.lower()
    # Remove special characters
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Tokenization
    tokens = word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [w for w in tokens if not w in stop_words]
    return filtered_tokens

def extract_skills(text, hard_skills, soft_skills):
    tokens = preprocess_text(text)
    found_hard = []
    found_soft = []

    for token in tokens:
        if token in hard_skills and token not in found_hard:
            found_hard.append(token)
        elif token in soft_skills and token not in found_soft:
            found_soft.append(token)
            
    return found_hard, found_soft

def extract_text_from_file(file_storage):
    """Extract text from uploaded PDF or DOCX file."""
    filename = file_storage.filename.lower()
    
    if filename.endswith('.pdf'):
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_storage)
            text = ''
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + ' '
            return text.strip()
        except Exception as e:
            return None
    
    elif filename.endswith('.docx'):
        try:
            from docx import Document
            doc = Document(file_storage)
            text = ' '.join([para.text for para in doc.paragraphs])
            return text.strip()
        except Exception as e:
            return None
    
    elif filename.endswith('.txt'):
        try:
            text = file_storage.read().decode('utf-8')
            return text.strip()
        except Exception as e:
            return None
    
    return None

def calculate_competitiveness(user_skills, market_skills):
    if not market_skills:
        return 0
    matched_skills = [s for s in user_skills if s in market_skills]
    score = (len(matched_skills) / len(market_skills)) * 100
    return round(score, 2)
