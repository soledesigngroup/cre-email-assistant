import os
import pickle
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class GmailService:
    def __init__(self, credentials_path, token_path, scopes):
        """
        Initialize Gmail service with paths to credentials and token files
        
        Args:
            credentials_path: Path to the client_secret.json from Google Cloud Console
            token_path: Path where the authentication token will be stored
            scopes: List of API scopes required for the application
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.scopes = scopes
        self.service = None
    
    def get_authorization_url(self, redirect_uri):
        """Generate the authorization URL for OAuth flow"""
        flow = Flow.from_client_secrets_file(
            self.credentials_path, 
            scopes=self.scopes,
            redirect_uri=redirect_uri
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return authorization_url, state
    
    def fetch_token(self, state, redirect_uri, authorization_response):
        """Exchange authorization code for tokens"""
        flow = Flow.from_client_secrets_file(
            self.credentials_path,
            scopes=self.scopes,
            state=state,
            redirect_uri=redirect_uri
        )
        flow.fetch_token(authorization_response=authorization_response)
        
        # Save the credentials for future use
        with open(self.token_path, 'wb') as token:
            pickle.dump(flow.credentials, token)
        
        return flow.credentials
    
    def build_service(self):
        """Build and return the Gmail API service"""
        creds = None
        
        # Load credentials from the saved file if it exists
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh token if expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save the refreshed credentials
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # If no valid credentials, return None - user needs to authenticate
        if not creds or not creds.valid:
            return None
        
        # Build and return the service
        self.service = build('gmail', 'v1', credentials=creds)
        return self.service
    
    def list_messages(self, max_results=10, query=None):
        """List messages from the Gmail inbox"""
        if not self.service:
            self.build_service()
            
        if not self.service:
            raise Exception("Authentication required before listing messages")
            
        results = self.service.users().messages().list(
            userId='me', 
            maxResults=max_results,
            q=query
        ).execute()
        
        messages = results.get('messages', [])
        return messages
    
    def get_message(self, message_id):
        """Get a specific message by ID"""
        if not self.service:
            self.build_service()
            
        if not self.service:
            raise Exception("Authentication required before getting message")
            
        return self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
    
    def get_message_with_body(self, message_id):
        """
        Get a specific message by ID with its body content extracted
        
        Args:
            message_id: The ID of the message to retrieve
            
        Returns:
            dict: Message details including headers and body content
        """
        if not self.service:
            self.build_service()
            
        if not self.service:
            raise Exception("Authentication required before getting message")
            
        # Get the full message
        message = self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        # Extract headers
        headers = message.get('payload', {}).get('headers', [])
        header_data = {}
        
        # Get all headers
        for header in headers:
            header_data[header['name']] = header['value']
        
        # Get the email body
        body_content = self._extract_email_body(message)
        
        # Compile email data
        email_data = {
            'id': message['id'],
            'thread_id': message.get('threadId', ''),
            'subject': next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(No subject)'),
            'from': next((h['value'] for h in headers if h['name'].lower() == 'from'), '(Unknown sender)'),
            'to': next((h['value'] for h in headers if h['name'].lower() == 'to'), ''),
            'date': next((h['value'] for h in headers if h['name'].lower() == 'date'), ''),
            'body': body_content,
            'snippet': message.get('snippet', ''),
            'labels': message.get('labelIds', [])
        }
        
        return email_data
    
    def _extract_email_body(self, message):
        """
        Private method to extract email body content from a Gmail API message
        
        Args:
            message: Gmail API message object
            
        Returns:
            dict: Contains plain text and HTML versions of the message body
        """
        body = {
            'plain': '',
            'html': ''
        }
        
        payload = message.get('payload', {})
        
        # Function to decode base64 data
        def decode_base64(data):
            """Decode base64 data with URL-safe alphabet used by Gmail API"""
            if not data:
                return ''
            
            import base64
            # Replace URL-safe characters
            data = data.replace('-', '+').replace('_', '/')
            
            # Add padding if needed
            padding = len(data) % 4
            if padding:
                data += '=' * (4 - padding)
                
            try:
                return base64.b64decode(data).decode('utf-8')
            except Exception as e:
                print(f"Error decoding base64 data: {e}")
                return ''
        
        # Function to recursively extract parts
        def extract_parts(payload):
            # Check if this part has a body
            if 'body' in payload and payload['body'].get('data'):
                mime_type = payload.get('mimeType', '')
                body_data = decode_base64(payload['body'].get('data', ''))
                
                if 'text/plain' in mime_type:
                    body['plain'] = body_data
                elif 'text/html' in mime_type:
                    body['html'] = body_data
            
            # If this part has nested parts, process them
            if 'parts' in payload:
                for part in payload['parts']:
                    extract_parts(part)
        
        # Start extraction
        extract_parts(payload)
        
        return body
    
    def get_thread(self, thread_id):
        """Get a thread by ID"""
        if not self.service:
            self.build_service()
            
        if not self.service:
            raise Exception("Authentication required before getting thread")
            
        return self.service.users().threads().get(
            userId='me',
            id=thread_id
        ).execute()
    
    def get_thread_with_messages(self, thread_id):
        """
        Get a thread and all its messages with body content
        
        Args:
            thread_id: The ID of the thread to retrieve
            
        Returns:
            dict: Thread details including all messages with body content
        """
        if not self.service:
            self.build_service()
            
        if not self.service:
            raise Exception("Authentication required before getting thread")
        
        # Get the thread with all messages
        thread = self.service.users().threads().get(
            userId='me',
            id=thread_id
        ).execute()
        
        # Process each message in the thread
        processed_messages = []
        for message in thread.get('messages', []):
            # Extract headers
            headers = message.get('payload', {}).get('headers', [])
            
            # Get the email body
            body_content = self._extract_email_body(message)
            
            # Compile message data
            message_data = {
                'id': message['id'],
                'subject': next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(No subject)'),
                'from': next((h['value'] for h in headers if h['name'].lower() == 'from'), '(Unknown sender)'),
                'to': next((h['value'] for h in headers if h['name'].lower() == 'to'), ''),
                'date': next((h['value'] for h in headers if h['name'].lower() == 'date'), ''),
                'body': body_content,
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', [])
            }
            
            processed_messages.append(message_data)
        
        # Create thread summary
        thread_data = {
            'id': thread['id'],
            'messages': processed_messages,
            'message_count': len(processed_messages)
        }
        
        if processed_messages:
            thread_data['subject'] = processed_messages[0]['subject']
        
        return thread_data
    
    def search_messages(self, query, max_results=10):
        """Search for messages using Gmail query syntax"""
        if not self.service:
            self.build_service()
            
        if not self.service:
            raise Exception("Authentication required before searching messages")
            
        results = self.service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        return messages
        
    # Test function for connectivity
    def test_connection(self):
        """Test Gmail API connectivity"""
        print("Gmail API Connection Test")
        print("-----------------------")
        
        # Build the service
        service = self.build_service()
        
        if not service:
            print("Authentication required. Please run the authentication flow first.")
            return False
        
        # List 10 messages from inbox
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("No messages found.")
        else:
            print(f"Successfully retrieved {len(messages)} messages:")
            
            for i, msg in enumerate(messages, 1):
                message = service.users().messages().get(userId='me', id=msg['id']).execute()
                headers = message.get('payload', {}).get('headers', [])
                
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No subject)')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown sender)')
                
                print(f"{i}. From: {sender} | Subject: {subject}")
        
        print("\nTest completed successfully!")
        return True