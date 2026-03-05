import sqlite3
import pandas as pd
from typing import Optional, Literal
from pathlib import Path
from sqlalchemy import create_engine, text

class DatabaseLoader:
    """Generic database loader for SQLite"""
    
    def __init__(self, db_path: str = 'data.db'):
        self.db_path = db_path
        self._ensure_db_exists()
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
    
    def _ensure_db_exists(self):
        """Create database directory if needed"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame for SQLite compatibility"""
        # Convert problematic types to strings
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    # Try to keep as is if possible
                    df[col] = df[col].astype(str)
                except:
                    df[col] = df[col].astype(str)
        
        # Replace NaN and None with appropriate values
        df = df.fillna('')
        return df
    
    def save(self, df: pd.DataFrame, table_name: str, if_exists: Literal['fail', 'replace', 'append', 'delete_rows'] = 'replace') -> str:
        """Save DataFrame to SQLite with detailed error handling"""
        try:
            # Sanitize table name
            table_name = table_name.replace('/', '_').replace('-', '_').lower()
            
            # Clean dataframe
            df = self._clean_dataframe(df)
            
            print(f"  Saving {len(df)} rows to table '{table_name}'")
            print(f"  Columns: {list(df.columns)}")
            
            # Use sqlalchemy for better error messages
            with self.engine.connect() as conn:
                df.to_sql(table_name, conn, if_exists=if_exists, index=False)
                conn.commit()
            
            return f"✓ Loaded {len(df)} records into '{table_name}'"
            
        except Exception as e:
            print(f"  Full error: {type(e).__name__}")
            print(f"  Message: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"✗ Error loading '{table_name}': {str(e)[:100]}"
    
    def query(self, sql: str) -> pd.DataFrame:
        """Execute SQL query and return results"""
        try:
            with self.engine.connect() as conn:
                df = pd.read_sql_query(sql, conn)
            return df
        except Exception as e:
            print(f"Error querying database: {e}")
            return pd.DataFrame()
    
    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """Get table schema information"""
        query = f"PRAGMA table_info({table_name})"
        return self.query(query)

