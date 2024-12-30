import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, Any
from .nlp_utils import preprocess_text

class ResponseGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.models = {}
        self.tokenizers = {}
        
    def load_model(self, model_type: str):
        """Load pre-trained model and tokenizer"""
        model_path = os.path.join(
            self.config['model_paths'][model_type]
        )
        
        self.models[model_type] = AutoModelForSequenceClassification.from_pretrained(
            model_path
        ).to(self.device)
        
        self.tokenizers[model_type] = AutoTokenizer.from_pretrained(
            model_path
        )

    def generate_response(self, query: str, model_type: str) -> str:
        """Generate response for given query"""
        if model_type not in self.models:
            self.load_model(model_type)
            
        # Preprocess query
        processed_query = preprocess_text(query)
        
        # Tokenize input
        inputs = self.tokenizers[model_type](
            processed_query,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(self.device)
        
        # Get model predictions
        with torch.no_grad():
            outputs = self.models[model_type](**inputs)
            logits = outputs.logits
            predicted_class = torch.argmax(logits, dim=-1).item()
            
        # Get response based on predicted class
        return self.config['responses'][model_type][predicted_class]

    def handle_financial_query(self, query: str) -> str:
        """Handle financial-related queries"""
        return self.generate_response(query, 'financial')

    def handle_support_query(self, query: str) -> str:
        """Handle customer support queries"""
        return self.generate_response(query, 'support')
