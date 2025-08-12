"""
Main client for the Possinote SDK.
"""

import requests
from typing import Dict, Any, Optional
from .exceptions import (
    PossinoteError,
    AuthenticationError,
    PaymentRequiredError,
    RateLimitError,
    ValidationError,
    APIError,
)
from .sms import SMS
from .email_service import Email
from .scheduling import Scheduling


class Client:
    """Main client for interacting with the PossiNote API."""
    
    BASE_URL = "https://notifyapi.possitech.net/api/v1"
    
    def __init__(self, api_key: str):
        """
        Initialize the Possinote client.
        
        Args:
            api_key: Your PossiNote API key
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })
        
        # Initialize service modules
        self.sms = SMS(self)
        self.email = Email(self)
        self.scheduling = Scheduling(self)
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            
        Returns:
            API response as dictionary
            
        Raises:
            Various PossinoteError subclasses based on response status
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params
            )
            
            return self._handle_response(response)
            
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.
        
        Args:
            response: HTTP response object
            
        Returns:
            Response data as dictionary
            
        Raises:
            Various PossinoteError subclasses based on response status
        """
        if response.status_code in (200, 201):
            return response.json()
        
        try:
            error_data = response.json()
            error_message = error_data.get("error", "Unknown error")
        except ValueError:
            error_message = "Unknown error"
        
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif response.status_code == 402:
            raise PaymentRequiredError(error_message)
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        elif response.status_code == 400:
            raise ValidationError(error_message)
        else:
            raise APIError(f"API request failed with status {response.status_code}: {error_message}")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request."""
        return self._make_request("POST", endpoint, data=data)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request."""
        return self._make_request("PUT", endpoint, data=data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint)
