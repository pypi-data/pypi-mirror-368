"""
SMS functionality for the Possinote SDK.
"""

from typing import Dict, Any, List, Optional
from urllib.parse import urlencode


class SMS:
    """SMS service for sending and managing SMS messages."""
    
    def __init__(self, client):
        self.client = client
    
    def send(self, to: str, message: str, sender_id: str) -> Dict[str, Any]:
        """
        Send a single SMS message.
        
        Args:
            to: Recipient phone number (E.164 format)
            message: SMS message content
            sender_id: Pre-approved sender ID
            
        Returns:
            API response
        """
        data = {
            "sms": {
                "to": to,
                "message": message,
                "sender_id": sender_id
            }
        }
        return self.client.post("/sms/send", data)
    
    def send_bulk(self, sender_id: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Send bulk SMS messages.
        
        Args:
            sender_id: Pre-approved sender ID
            messages: List of message objects with 'recipient' and 'message' keys
            
        Returns:
            API response
        """
        data = {
            "bulk_sms": {
                "sender_id": sender_id,
                "messages": messages
            }
        }
        return self.client.post("/sms/bulk", data)
    
    def schedule(
        self, 
        recipient: str, 
        message: str, 
        sender_id: str, 
        scheduled_at: str
    ) -> Dict[str, Any]:
        """
        Schedule a single SMS message.
        
        Args:
            recipient: Recipient phone number (E.164 format)
            message: SMS message content
            sender_id: Pre-approved sender ID
            scheduled_at: ISO 8601 datetime string
            
        Returns:
            API response
        """
        data = {
            "scheduled_sms": {
                "recipient": recipient,
                "message": message,
                "sender_id": sender_id,
                "scheduled_at": scheduled_at
            }
        }
        return self.client.post("/sms/schedule", data)
    
    def schedule_bulk(self, sender_id: str, messages: List[Dict[str, str]], scheduled_at: str) -> Dict[str, Any]:
        """
        Schedule bulk SMS messages.
        
        Args:
            sender_id: Pre-approved sender ID
            messages: List of message objects with 'recipient' and 'message' keys
            scheduled_at: ISO 8601 datetime string
            
        Returns:
            API response
        """
        data = {
            "bulk_scheduled_sms": {
                "sender_id": sender_id,
                "messages": messages,
                "scheduled_at": scheduled_at
            }
        }
        return self.client.post("/sms/schedule-bulk", data)
    
    def history(self, **params) -> Dict[str, Any]:
        """
        Get SMS history.
        
        Args:
            **params: Query parameters (page, per_page, status, date_filter, etc.)
            
        Returns:
            API response
        """
        return self.client.get("/sms/history", params)
    
    def scheduled(self, **params) -> Dict[str, Any]:
        """
        Get scheduled SMS messages.
        
        Args:
            **params: Query parameters (page, per_page, status, date_filter, etc.)
            
        Returns:
            API response
        """
        return self.client.get("/sms/scheduled", params)
    
    def cancel_scheduled(self, sms_id: str) -> Dict[str, Any]:
        """
        Cancel a scheduled SMS message.
        
        Args:
            sms_id: ID of the scheduled SMS to cancel
            
        Returns:
            API response
        """
        return self.client.delete(f"/sms/scheduled/{sms_id}")
