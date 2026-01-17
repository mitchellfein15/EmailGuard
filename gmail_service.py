"""
Gmail API Service Module

Handles all interactions with the Gmail API including:
- Fetching unread messages
- Retrieving email content
- Moving emails to trash
"""

import base64
import email
from email.header import decode_header
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time


class GmailClient:
    """Client for interacting with Gmail API."""
    
    def __init__(self, credentials):
        """
        Initialize Gmail client with authenticated credentials.
        
        Args:
            credentials: Authenticated credentials object from auth.py
        """
        try:
            self.service = build('gmail', 'v1', credentials=credentials)
        except Exception as e:
            raise ConnectionError(f"Failed to build Gmail service: {e}")
    
    def fetch_unread_messages(self, max_results=10):
        """
        Fetch unread email message IDs from Gmail.
        
        Args:
            max_results (int): Maximum number of messages to fetch (default: 10)
            
        Returns:
            list: List of message IDs (strings)
            
        Raises:
            HttpError: If API call fails (rate limits, connection errors, etc.)
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            message_ids = [msg['id'] for msg in messages]
            
            return message_ids
            
        except HttpError as error:
            if error.resp.status == 429:
                # Rate limit exceeded
                retry_after = error.resp.get('retry-after', 60)
                print(f"Rate limit exceeded. Waiting {retry_after} seconds...")
                time.sleep(int(retry_after))
                # Retry once
                return self.fetch_unread_messages(max_results)
            else:
                raise HttpError(
                    error.resp,
                    error.content,
                    f"Failed to fetch unread messages: {error}"
                )
        except Exception as e:
            raise ConnectionError(f"Connection error while fetching messages: {e}")
    
    def get_email_content(self, message_id):
        """
        Retrieve and decode email content.
        
        Args:
            message_id (str): Gmail message ID
            
        Returns:
            dict: Dictionary containing:
                - subject (str): Email subject
                - body (str): Email body (text/plain preferred, falls back to text/html)
                - snippet (str): Email snippet
                - from_email (str): Sender email address
                
        Raises:
            HttpError: If API call fails
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload'].get('headers', [])
            subject = ''
            from_email = ''
            
            for header in headers:
                if header['name'].lower() == 'subject':
                    subject = self._decode_header(header['value'])
                elif header['name'].lower() == 'from':
                    from_email = header['value']
            
            # Extract body
            body = self._extract_body(message['payload'])
            
            # Get snippet
            snippet = message.get('snippet', '')
            
            return {
                'subject': subject,
                'body': body,
                'snippet': snippet,
                'from_email': from_email
            }
            
        except HttpError as error:
            if error.resp.status == 429:
                retry_after = error.resp.get('retry-after', 60)
                print(f"Rate limit exceeded. Waiting {retry_after} seconds...")
                time.sleep(int(retry_after))
                # Retry once
                return self.get_email_content(message_id)
            else:
                raise HttpError(
                    error.resp,
                    error.content,
                    f"Failed to get email content for message {message_id}: {error}"
                )
        except Exception as e:
            raise ConnectionError(f"Connection error while getting email content: {e}")
    
    def _decode_header(self, header_value):
        """
        Decode email header value (handles encoded-words).
        
        Args:
            header_value (str): Raw header value
            
        Returns:
            str: Decoded header value
        """
        try:
            decoded_parts = decode_header(header_value)
            decoded_string = ''
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding)
                    else:
                        decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += part
            return decoded_string
        except Exception:
            return header_value
    
    def _extract_body(self, payload):
        """
        Extract email body from payload, handling multipart and encoded content.
        
        Args:
            payload: Message payload from Gmail API
            
        Returns:
            str: Decoded email body
        """
        body = ''
        
        # Check if message has parts (multipart)
        if 'parts' in payload:
            for part in payload['parts']:
                # Prefer text/plain over text/html
                mime_type = part.get('mimeType', '')
                if mime_type == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        body = self._decode_base64url(data)
                        break
                elif mime_type == 'text/html' and not body:
                    # Fallback to HTML if no plain text found
                    data = part.get('body', {}).get('data', '')
                    if data:
                        body = self._decode_base64url(data)
        else:
            # Single part message
            mime_type = payload.get('mimeType', '')
            if mime_type in ['text/plain', 'text/html']:
                data = payload.get('body', {}).get('data', '')
                if data:
                    body = self._decode_base64url(data)
        
        return body
    
    def _decode_base64url(self, data):
        """
        Decode base64url encoded string.
        
        Args:
            data (str): Base64url encoded string
            
        Returns:
            str: Decoded string
        """
        try:
            # Add padding if needed
            padding = 4 - len(data) % 4
            if padding != 4:
                data += '=' * padding
            
            # Replace URL-safe characters
            data = data.replace('-', '+').replace('_', '/')
            
            # Decode
            decoded_bytes = base64.b64decode(data)
            return decoded_bytes.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error decoding base64: {e}")
            return ''
    
    def move_to_trash(self, message_id):
        """
        Move email to trash by adding TRASH label and removing INBOX label.
        
        Args:
            message_id (str): Gmail message ID
            
        Returns:
            dict: Response from API
            
        Raises:
            HttpError: If API call fails
        """
        try:
            result = self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={
                    'addLabelIds': ['TRASH'],
                    'removeLabelIds': ['INBOX']
                }
            ).execute()
            
            return result
            
        except HttpError as error:
            if error.resp.status == 429:
                retry_after = error.resp.get('retry-after', 60)
                print(f"Rate limit exceeded. Waiting {retry_after} seconds...")
                time.sleep(int(retry_after))
                # Retry once
                return self.move_to_trash(message_id)
            else:
                raise HttpError(
                    error.resp,
                    error.content,
                    f"Failed to move message {message_id} to trash: {error}"
                )
        except Exception as e:
            raise ConnectionError(f"Connection error while moving to trash: {e}")
