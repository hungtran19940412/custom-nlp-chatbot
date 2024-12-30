from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import load_dataset
from typing import Dict, Tuple, Optional, List
import torch
import numpy as np
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class Chatbot:
    def __init__(
        self,
        model_name: str = "gpt2",
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        max_length: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ):
        """Initialize the chatbot with a pre-trained model."""
        self.device = device
        self.max_length = max_length
        self.temperature = temperature
        self.top_p = top_p
        
        # Load model and tokenizer
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
            logger.info(f"Loaded model {model_name} successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

        # Initialize metrics tracking
        self.metrics = {
            "total_requests": 0,
            "successful_responses": 0,
            "average_confidence": 0.0,
            "last_updated": datetime.now().isoformat()
        }

    async def generate_response(
        self,
        text: str,
        context: Optional[Dict] = None,
        language: str = "en"
    ) -> Tuple[str, float]:
        """Generate a response to the input text."""
        try:
            # Update metrics
            self.metrics["total_requests"] += 1
            
            # Prepare input text with context if available
            input_text = self._prepare_input(text, context)
            
            # Tokenize input
            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.max_length
            ).to(self.device)
            
            # Generate response
            outputs = self.model.generate(
                **inputs,
                max_length=self.max_length,
                temperature=self.temperature,
                top_p=self.top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(outputs)
            
            # Update metrics
            self.metrics["successful_responses"] += 1
            self.metrics["average_confidence"] = (
                (self.metrics["average_confidence"] * (self.metrics["successful_responses"] - 1) + confidence)
                / self.metrics["successful_responses"]
            )
            self.metrics["last_updated"] = datetime.now().isoformat()
            
            return response, confidence
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    async def train(
        self,
        dataset_path: str,
        model_type: str = "gpt2",
        epochs: int = 3,
        batch_size: int = 8
    ) -> str:
        """Fine-tune the model on a custom dataset."""
        try:
            # Load dataset
            dataset = load_dataset("text", data_files=dataset_path)
            
            # Tokenize dataset
            def tokenize_function(examples):
                return self.tokenizer(
                    examples["text"],
                    padding="max_length",
                    truncation=True,
                    max_length=self.max_length
                )
            
            tokenized_dataset = dataset.map(
                tokenize_function,
                batched=True,
                num_proc=4,
                remove_columns=dataset["train"].column_names
            )
            
            # Set up training arguments
            training_args = TrainingArguments(
                output_dir="./results",
                num_train_epochs=epochs,
                per_device_train_batch_size=batch_size,
                save_steps=500,
                save_total_limit=2,
            )
            
            # Initialize trainer
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False
            )
            
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=tokenized_dataset["train"],
                data_collator=data_collator,
            )
            
            # Start training
            trainer.train()
            
            # Save the fine-tuned model
            model_path = f"models/fine_tuned_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            trainer.save_model(model_path)
            
            return model_path
            
        except Exception as e:
            logger.error(f"Error during training: {str(e)}")
            raise

    def _prepare_input(self, text: str, context: Optional[Dict] = None) -> str:
        """Prepare input text with context for the model."""
        if not context:
            return text
            
        # Add relevant context to the input
        context_str = " ".join([
            f"{k}: {v}" for k, v in context.items()
            if k in ["previous_message", "topic", "user_intent"]
        ])
        
        return f"{context_str}\nCurrent message: {text}"

    def _calculate_confidence(self, outputs) -> float:
        """Calculate confidence score for the generated response."""
        # Simple confidence calculation based on output probabilities
        with torch.no_grad():
            logits = self.model(outputs).logits
            probs = torch.softmax(logits[:, -1], dim=-1)
            confidence = float(torch.max(probs).cpu().numpy())
        return confidence

    async def get_metrics(self) -> Dict:
        """Return current metrics."""
        return self.metrics

    def save_model(self, path: str):
        """Save the current model state."""
        try:
            self.model.save_pretrained(path)
            self.tokenizer.save_pretrained(path)
            
            # Save metrics
            with open(os.path.join(path, "metrics.json"), "w") as f:
                json.dump(self.metrics, f)
                
            logger.info(f"Model saved successfully to {path}")
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise

    def load_model(self, path: str):
        """Load a saved model state."""
        try:
            self.model = AutoModelForCausalLM.from_pretrained(path).to(self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(path)
            
            # Load metrics if available
            metrics_path = os.path.join(path, "metrics.json")
            if os.path.exists(metrics_path):
                with open(metrics_path, "r") as f:
                    self.metrics = json.load(f)
                    
            logger.info(f"Model loaded successfully from {path}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
