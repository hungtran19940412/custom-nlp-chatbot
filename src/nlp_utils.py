import re
import string
from typing import List
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Initialize NLP resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text: str) -> str:
    """Preprocess text through cleaning and normalization"""
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    
    # Tokenize text
    tokens = word_tokenize(text)
    
    # Remove stopwords and lemmatize
    processed_tokens = [
        lemmatizer.lemmatize(token) 
        for token in tokens 
        if token not in stop_words
    ]
    
    return ' '.join(processed_tokens)

def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    """Extract top N keywords from text"""
    processed_text = preprocess_text(text)
    tokens = word_tokenize(processed_text)
    
    # Get frequency distribution
    freq_dist = nltk.FreqDist(tokens)
    
    # Return most common tokens
    return [word for word, freq in freq_dist.most_common(top_n)]
