from extract import APIExtractor
from transform import DataTransformer
from load import DatabaseLoader
from typing import List, Optional, Dict, Callable

class ETLPipeline:
    """Generic ETL Pipeline for API → Database"""
    
    def __init__(
        self, 
        api_url: str, 
        db_path: str = 'data.db',
        api_key: Optional[str] = None
    ):
        self.extractor = APIExtractor(api_url, api_key)
        self.loader = DatabaseLoader(db_path)
        self.transformations: Dict[str, Callable] = {}
    
    def register_transformation(self, endpoint: str, func: Callable):
        """Register a custom transformation for an endpoint"""
        self.transformations[endpoint] = func
    
    def process_endpoint(
        self, 
        endpoint: str, 
        table_name: str,
        selected_columns: Optional[List[str]] = None,
        flatten: bool = True,
        verbose: bool = True
    ) -> str:
        """Process single endpoint through ETL pipeline"""
        
        if verbose:
            print(f"\n{'='*50}")
            print(f"Processing: {endpoint}")
            print(f"{'='*50}")
        
        try:
            # Extract
            records = self.extractor.fetch(endpoint)
            
            # Apply custom transformation if registered
            if endpoint in self.transformations:
                records = self.transformations[endpoint](records)
            
            # Transform
            transformer = DataTransformer(records)
            df = transformer.to_dataframe(selected_columns, flatten=flatten)
            
            if df.empty:
                return f"⚠ No data for {endpoint}"
            
            if verbose:
                print(f"Records: {len(df)}")
                print(f"Columns: {list(df.columns)}")
                print(df.head())
            
            # Load
            return self.loader.save(df, table_name)
            
        except Exception as e:
            print(f"✗ Pipeline error for {endpoint}: {e}")
            import traceback
            traceback.print_exc()
            return f"✗ Failed to process {endpoint}"
    
    def run(self, endpoints: Dict[str, str], **kwargs):
        """Run pipeline for multiple endpoints"""
        results = {}
        
        for endpoint, table_name in endpoints.items():
            results[endpoint] = self.process_endpoint(endpoint, table_name, **kwargs)
            print(results[endpoint])
        
        return results
    
    def close(self):
        """Close resources"""
        self.extractor.close()