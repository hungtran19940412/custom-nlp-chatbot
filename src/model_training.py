import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)
from datasets import Dataset
from sklearn.model_selection import train_test_split
from .data_pipeline import DataPipeline
from .nlp_utils import preprocess_text
from typing import Dict, Any

class ModelTrainer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.data_pipeline = DataPipeline(config)
        
    def load_dataset(self, source: str) -> Dataset:
        """Load and preprocess dataset"""
        # Load processed data
        file_path = os.path.join(
            self.config['data_paths']['processed'],
            f"{source}.csv"
        )
        df = pd.read_csv(file_path)
        
        # Split into train and test
        train_df, test_df = train_test_split(
            df,
            test_size=0.2,
            random_state=42
        )
        
        return Dataset.from_pandas(train_df), Dataset.from_pandas(test_df)

    def initialize_model(self, model_name: str):
        """Initialize model and tokenizer"""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=self.config['num_labels']
        ).to(self.device)

    def tokenize_data(self, dataset: Dataset) -> Dataset:
        """Tokenize dataset"""
        return dataset.map(
            lambda x: self.tokenizer(
                x['cleaned_text'],
                padding=True,
                truncation=True
            ),
            batched=True
        )

    def train_model(self, train_dataset: Dataset, val_dataset: Dataset):
        """Train model using HuggingFace Trainer"""
        training_args = TrainingArguments(
            output_dir=self.config['model_output_dir'],
            evaluation_strategy="epoch",
            learning_rate=2e-5,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            num_train_epochs=3,
            weight_decay=0.01,
            save_strategy="epoch",
            load_best_model_at_end=True,
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
        )

        trainer.train()
        return trainer

    def save_model(self, trainer: Trainer, model_name: str):
        """Save trained model"""
        output_dir = os.path.join(
            self.config['model_output_dir'],
            model_name
        )
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)

    def train(self, model_name: str, source: str):
        """Complete training pipeline"""
        # Load and preprocess data
        train_dataset, val_dataset = self.load_dataset(source)
        
        # Initialize model
        self.initialize_model(model_name)
        
        # Tokenize data
        train_dataset = self.tokenize_data(train_dataset)
        val_dataset = self.tokenize_data(val_dataset)
        
        # Train model
        trainer = self.train_model(train_dataset, val_dataset)
        
        # Save model
        self.save_model(trainer, source)
