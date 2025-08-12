"""
Email functionality for the Possinote SDK.
"""

from typing import Dict, Any, List, Optional


class Email:
    """Email service for sending and managing emails."""
    
    def __init__(self, client):
        self.client = client
    
    def send(
        self, 
        recipient: str, 
        subject: str, 
        content: str, 
        sender_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a single email.
        
        Args:
            recipient: Recipient email address
            subject: Email subject
            content: Email content (HTML supported)
            sender_name: Optional sender name
            
        Returns:
            API response
        """
        data = {
            "recipient": recipient,
            "subject": subject,
            "content": content
        }
        
        # Add sender_name only if provided
        if sender_name:
            data["sender_name"] = sender_name
            
        return self.client.post("/emails/send", data)
    
    def send_bulk(
        self, 
        subject: str, 
        content: str, 
        recipients: List[str], 
        sender_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send bulk emails.
        
        Args:
            subject: Email subject
            content: Email content (HTML supported)
            recipients: List of recipient email addresses
            sender_name: Optional sender name
            
        Returns:
            API response
        """
        data = {
            "subject": subject,
            "content": content,
            "recipients": recipients
        }
        
        # Add sender_name only if provided
        if sender_name:
            data["sender_name"] = sender_name
            
        return self.client.post("/emails/bulk", data)
    
    def history(self, **params) -> Dict[str, Any]:
        """
        Get email history.
        
        Args:
            **params: Query parameters (page, per_page, status, date_filter, etc.)
            
        Returns:
            API response
        """
        return self.client.get("/emails/history", params)
