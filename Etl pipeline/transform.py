import pandas as pd
import json
from typing import Generator, Optional, List, Dict, Any

class DataTransformer:
    """Generic data transformer for converting records to DataFrames"""
    
    def __init__(self, records_generator: Generator[dict, None, None]):
        self.records_generator = records_generator
    
    def _flatten_dict(self, d: dict, parent_key: str = '', sep: str = '_') -> dict:
        """Flatten nested dictionaries"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert lists to JSON string
                items.append((new_key, json.dumps(v)))
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    def to_dataframe(self, selected_columns: Optional[List[str]] = None, flatten: bool = True) -> pd.DataFrame:
        """Convert generator to DataFrame with optional column selection and flattening"""
        try:
            records = list(self.records_generator)
            if not records:
                return pd.DataFrame()
            
            # Flatten nested structures
            if flatten:
                records = [self._flatten_dict(record) for record in records]
            
            df = pd.DataFrame(records)
            
            if selected_columns:
                # Only select columns that exist
                existing_cols = [col for col in selected_columns if col in df.columns]
                df = df[existing_cols]
            
            return df
        except Exception as e:
            print(f"Error transforming data: {e}")
            return pd.DataFrame()
    
    def apply_transformation(self, func):
        """Apply custom transformation function to records"""
        for record in self.records_generator:
            yield func(record)