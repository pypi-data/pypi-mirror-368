"""
XPawn Client - Main client class for interacting with XPawn API
"""

import requests
from typing import Optional, Dict, Any


class XPawnError(Exception):
    """Base exception for XPawn API errors"""
    pass


class XPawnAPIError(XPawnError):
    """Exception raised for API-related errors"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)


class Client:
    """
    XPawn API Client
    
    A client for interacting with the XPawn API to retrieve prompts and other data.
    
    Args:
        api_key (str): Your XPawn API key
        base_url (str, optional): Base URL for the API. Defaults to 'https://prompt-api-205008120330.us-central1.run.app'
        timeout (int, optional): Request timeout in seconds. Defaults to 30
    
    Example:
        >>> from xpawn import xpawn
        >>> client = xpawn.Client(api_key='your-api-key')
        >>> response = client.get_prompt('prompt-id')
    """
    
    def __init__(
        self, 
        api_key: str, 
        base_url: str = "https://prompt-api-205008120330.us-central1.run.app",
        timeout: int = 30
    ):
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Set up default headers
        self._headers = {
            'accept': 'application/json',
            'X-Secret-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the XPawn API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json_data: JSON data to send in request body
            params: URL parameters
            
        Returns:
            dict: JSON response from the API
            
        Raises:
            XPawnAPIError: If the API request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self._headers,
                json=json_data,
                params=params,
                timeout=self.timeout
            )
            
            # Raise an exception for bad status codes
            response.raise_for_status()
            
            # Try to return JSON, fallback to text if JSON parsing fails
            try:
                return response.json()
            except ValueError:
                return {"response": response.text}
                
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                try:
                    error_data = e.response.json()
                    message = error_data.get('message', str(e))
                except ValueError:
                    message = str(e)
            else:
                status_code = None
                message = str(e)
            
            raise XPawnAPIError(f"API request failed: {message}", status_code)
    
    def get_prompt(self, prompt_id: str) -> Dict[str, Any]:
        """
        Retrieve a prompt by its ID
        
        Args:
            prompt_id (str): The ID of the prompt to retrieve
            
        Returns:
            dict: The prompt data from the API
            
        Raises:
            XPawnAPIError: If the API request fails
            ValueError: If prompt_id is empty or None
        
        Example:
            >>> client = Client(api_key='your-key')
            >>> prompt = client.get_prompt('prompt-123')
            >>> print(prompt)
        """
        if not prompt_id:
            raise ValueError("prompt_id is required and cannot be empty")
        
        json_data = {"id": prompt_id}
        return self._make_request("POST", "check-id", json_data=json_data)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the API
        
        Returns:
            dict: Health check response
        """
        return self._make_request("GET", "health_check")