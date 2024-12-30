import os
import pandas as pd
from typing import Dict, Any
from .nlp_utils import preprocess_text

class DataPipeline:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.raw_data_path = config['data_paths']['raw']
        self.processed_data_path = config['data_paths']['processed']

    def load_raw_data(self, source: str) -> pd.DataFrame:
        """Load raw data from specified source"""
        file_path = os.path.join(self.raw_data_path, f"{source}.csv")
        return pd.read_csv(file_path)

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess raw data"""
        # Text cleaning and preprocessing
        df['cleaned_text'] = df['text'].apply(preprocess_text)
        
        # Handle missing values
        df = df.dropna(subset=['cleaned_text'])
        
        return df

    def save_processed_data(self, df: pd.DataFrame, destination: str):
        """Save processed data"""
        file_path = os.path.join(self.processed_data_path, f"{destination}.csv")
        df.to_csv(file_path, index=False)

    def run_pipeline(self, source: str, destination: str):
        """Run complete data processing pipeline"""
        raw_data = self.load_raw_data(source)
        processed_data = self.preprocess_data(raw_data)
        self.save_processed_data(processed_data, destination)
