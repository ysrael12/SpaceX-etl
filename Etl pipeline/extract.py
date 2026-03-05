import requests
from typing import Generator, Any, Optional

class APIExtractor:
    """Generic API data extractor with support for authentication"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        
    def _get_headers(self) -> dict:
        """Build request headers"""
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers
    
    def fetch(self, endpoint: str) -> Generator[dict, None, None]:
        """Fetch data from API and yield records"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            data = response.json()
            
            # Handle both list and dict responses
            if isinstance(data, list):
                for record in data:
                    yield record
            else:
                yield data
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {endpoint}: {e}")
        finally:
            pass
    
    def close(self):
        """Close session"""
        self.session.close()