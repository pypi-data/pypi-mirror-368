import os
from typing import Optional, Dict, Any, Generator
import requests
import json
import time
from .endpoints.chat import PromptOptimizersChatCompletion
from .exceptions import APIError, RateLimitError, AuthenticationError

class PromptOptimizers:
    def __init__(
            self, 
            api_key: str, 
            optimization_type: str = "general", 
            base_url: str = "https://api.prompt-optimizers.com/v1",
            organization: Optional[str] = None,
            timeout: int = 60,
            max_retries: int = 3
            ):
        self.api_key = api_key or os.getenv("PROMPT_OPTIMIZERS_API_KEY")
        if not self.api_key:
            raise AuthenticationError("API key not provided")
        self.optimization_type = optimization_type
        self.base_url = base_url
        self.organization = organization
        self.timeout = timeout
        self.max_retries = max_retries
    
        # Initialize session with default headers
        self.session = requests.Session()
        self._setup_headers()
        
        # Initialize endpoint handlers
        self.chat = PromptOptimizersChatCompletion(self)

    def _setup_headers(self):
        """Setup default headers for all requests"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "PromptOptimizersClient/1.0.0"
        }
        
        if self.organization:
            headers["PromptOptimizers-Organization"] = self.organization
        
        self.session.headers.update(headers)
    
    def _make_request(
        self,
        endpoint: str,
        data: Dict[str, Any],
        method: str = "POST"
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic
        
        Args:
            endpoint: API endpoint
            data: Request data
            method: HTTP method
            
        Returns:
            Response data
            
        Raises:
            APIError: For API errors
            RateLimitError: For rate limit errors
            AuthenticationError: For auth errors
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                if method.upper() == "POST":
                    response = self.session.post(
                        url, 
                        json=data, 
                        timeout=self.timeout
                    )
                elif method.upper() == "GET":
                    response = self.session.get(
                        url, 
                        params=data, 
                        timeout=self.timeout
                    )
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                # Handle different status codes
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status_code == 429:
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"Rate limited. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise RateLimitError("Rate limit exceeded")
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    raise APIError(error_msg)
                    
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Request failed, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise APIError(f"Request failed: {str(e)}")
        
        raise APIError("Max retries exceeded")
    
    def _stream_request(
        self,
        endpoint: str,
        data: Dict[str, Any]
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Make streaming request
        
        Args:
            endpoint: API endpoint
            data: Request data
            
        Yields:
            Streaming response chunks
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            with self.session.post(
                url,
                json=data,
                timeout=self.timeout,
                stream=True
            ) as response:
                
                if response.status_code != 200:
                    raise APIError(f"HTTP {response.status_code}: {response.text}")
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            chunk_data = line[6:]  # Remove 'data: ' prefix
                            if chunk_data.strip() == '[DONE]':
                                break
                            try:
                                yield json.loads(chunk_data)
                            except json.JSONDecodeError:
                                continue
                                
        except requests.exceptions.RequestException as e:
            raise APIError(f"Streaming request failed: {str(e)}")