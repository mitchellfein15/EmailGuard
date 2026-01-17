"""
Google OAuth 2.0 Authentication Module

Handles authentication with Gmail API using OAuth 2.0 flow.
Saves and loads token.json to avoid re-authenticating on every run.
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError


# Gmail API scopes required for the application
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def authenticate():
    """
    Authenticate with Gmail API using OAuth 2.0.
    
    This function:
    1. Loads credentials.json (from Google Cloud Console)
    2. Checks for existing token.json
    3. If token exists and is valid, uses it
    4. If not, initiates OAuth flow and saves token
    5. Returns authenticated Credentials object
    
    Returns:
        Credentials: Authenticated credentials object for Gmail API
        
    Raises:
        FileNotFoundError: If credentials.json is not found
        RefreshError: If token refresh fails
    """
    creds = None
    token_file = 'token.json'
    credentials_file = 'credentials.json'
    
    # Check if credentials.json exists
    if not os.path.exists(credentials_file):
        raise FileNotFoundError(
            f"'{credentials_file}' not found. "
            "Please download it from Google Cloud Console and place it in the project root."
        )
    
    # Load existing token if available
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error loading token.json: {e}")
            print("Will initiate new OAuth flow...")
            creds = None
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                print("Token expired and refresh failed. Initiating new OAuth flow...")
                creds = None
        
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
        print(f"Authentication successful. Token saved to {token_file}")
    
    return creds
