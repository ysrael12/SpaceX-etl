from pipeline import ETLPipeline

def main():
    # Configure pipeline
    pipeline = ETLPipeline(
        api_url='https://api.spacexdata.com/v3/',
        db_path='spacex.db'
    )
    
    # Define endpoints to process
    endpoints = {
        'landpads': 'landpads',
        'launchpads': 'launchpads',
        'rockets': 'rockets',
        'ships': 'ships'
    }
    
    # Run pipeline
    results = pipeline.run(endpoints)
    
    # Example: Query results
    print("\n" + "="*50)
    print("Sample Query Results:")
    print("="*50)
    rockets = pipeline.loader.query("SELECT * FROM rockets LIMIT 3")
    print(rockets)
    
    pipeline.close()

if __name__ == '__main__':
    main()