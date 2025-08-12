"""
Scheduling functionality for the Possinote SDK.
"""

from typing import Dict, Any, List, Optional


class Scheduling:
    """Scheduling service for managing scheduled emails."""
    
    def __init__(self, client):
        self.client = client
    
    def schedule_email(
        self, 
        recipient: str, 
        subject: str, 
        content: str, 
        scheduled_at: str, 
        sender_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule a single email.
        
        Args:
            recipient: Recipient email address
            subject: Email subject
            content: Email content (HTML supported)
            scheduled_at: ISO 8601 datetime string
            sender_name: Optional sender name
            
        Returns:
            API response
        """
        data = {
            "scheduled_email": {
                "recipient": recipient,
                "subject": subject,
                "content": content,
                "scheduled_at": scheduled_at,
                "sender_name": sender_name
            }
        }
        return self.client.post("/emails/schedule", data)
    
    def schedule_bulk_emails(
        self, 
        subject: str, 
        content: str, 
        recipients: List[str], 
        scheduled_at: str, 
        sender_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule bulk emails.
        
        Args:
            subject: Email subject
            content: Email content (HTML supported)
            recipients: List of recipient email addresses
            scheduled_at: ISO 8601 datetime string
            sender_name: Optional sender name
            
        Returns:
            API response
        """
        data = {
            "bulk_scheduled_email": {
                "subject": subject,
                "content": content,
                "recipients": recipients,
                "scheduled_at": scheduled_at,
                "sender_name": sender_name
            }
        }
        return self.client.post("/emails/schedule-bulk", data)
    
    def schedule_multiple_emails(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Schedule multiple individual emails.
        
        Args:
            emails: List of email objects with recipient, subject, content, scheduled_at, and optional sender_name
            
        Returns:
            API response
        """
        data = {
            "emails": emails
        }
        return self.client.post("/emails/schedule-bulk-individual", data)
    
    def scheduled_emails(self, **params) -> Dict[str, Any]:
        """
        Get scheduled emails.
        
        Args:
            **params: Query parameters (page, per_page, status, date_filter, etc.)
            
        Returns:
            API response
        """
        return self.client.get("/emails/scheduled", params)
    
    def cancel_scheduled_email(self, email_id: str) -> Dict[str, Any]:
        """
        Cancel a scheduled email.
        
        Args:
            email_id: ID of the scheduled email to cancel
            
        Returns:
            API response
        """
        return self.client.delete(f"/emails/scheduled/{email_id}")
