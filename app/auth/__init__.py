from flask import Blueprint, redirect, request, url_for, session, jsonify
import os

# Allow OAuth over HTTP for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from app.services.gmail_service import GmailService

# Create a Blueprint for auth routes
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Initialize the Gmail service
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
credentials_path = os.path.join(os.path.dirname(__file__), '..', '..', 'client_secret.json')
token_path = os.path.join(os.path.dirname(__file__), '..', '..', 'token.pickle')

gmail_service = GmailService(
    credentials_path=credentials_path,
    token_path=token_path,
    scopes=SCOPES
)

@auth_bp.route('/login')
def login():
    """Generate authorization URL and redirect user"""
    # Generate authorization URL and redirect user
    callback_url = url_for('auth.callback', _external=True)
    auth_url, state = gmail_service.get_authorization_url(callback_url)
    session['state'] = state
    return redirect(auth_url)

@auth_bp.route('/callback')
def callback():
    """Handle the OAuth2 callback"""
    # Handle the OAuth2 callback
    state = session.get('state')
    callback_url = url_for('auth.callback', _external=True)
    gmail_service.fetch_token(
        state=state,
        redirect_uri=callback_url,
        authorization_response=request.url
    )
    return redirect(url_for('auth.emails'))

@auth_bp.route('/emails')
def emails():
    """List emails from the inbox"""
    # Check if the service is authenticated
    service = gmail_service.build_service()
    if not service:
        return redirect(url_for('auth.login'))
    
    # Retrieve messages
    try:
        messages = gmail_service.list_messages(max_results=10)
        message_list = []
        
        for msg in messages:
            # Get message details
            message = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = message.get('payload', {}).get('headers', [])
            
            # Extract subject and sender
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(No subject)')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '(Unknown sender)')
            
            message_list.append({
                'id': msg['id'],
                'thread_id': message.get('threadId', ''),
                'subject': subject,
                'sender': sender,
                'snippet': message.get('snippet', '')
            })
        
        return jsonify({
            "status": "success", 
            "count": len(messages),
            "emails": message_list
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@auth_bp.route('/emails/<email_id>')
def email_detail(email_id):
    """Get details for a specific email"""
    # Check if the service is authenticated
    service = gmail_service.build_service()
    if not service:
        return redirect(url_for('auth.login'))
    
    try:
        # Get message details
        message = service.users().messages().get(userId='me', id=email_id).execute()
        headers = message.get('payload', {}).get('headers', [])
        
        # Extract header information
        email_data = {
            'id': message['id'],
            'thread_id': message.get('threadId', ''),
            'subject': next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(No subject)'),
            'from': next((h['value'] for h in headers if h['name'].lower() == 'from'), '(Unknown sender)'),
            'to': next((h['value'] for h in headers if h['name'].lower() == 'to'), ''),
            'date': next((h['value'] for h in headers if h['name'].lower() == 'date'), ''),
            'snippet': message.get('snippet', ''),
            'labels': message.get('labelIds', [])
        }
        
        return jsonify({
            "status": "success",
            "email": email_data
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@auth_bp.route('/emails/<email_id>/content')
def email_content(email_id):
    """Get a specific email with its full content"""
    # Check if the service is authenticated
    service = gmail_service.build_service()
    if not service:
        return redirect(url_for('auth.login'))
    
    try:
        # Get the message with body content
        email_data = gmail_service.get_message_with_body(email_id)
        
        return jsonify({
            "status": "success",
            "email": email_data
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@auth_bp.route('/threads')
def threads():
    """List email threads"""
    # Check if the service is authenticated
    service = gmail_service.build_service()
    if not service:
        return redirect(url_for('auth.login'))
    
    try:
        # List threads
        results = service.users().threads().list(
            userId='me',
            maxResults=10
        ).execute()
        
        threads = results.get('threads', [])
        thread_list = []
        
        for thread in threads:
            # Get basic thread details
            thread_data = service.users().threads().get(
                userId='me',
                id=thread['id']
            ).execute()
            
            # Get messages in thread
            messages = thread_data.get('messages', [])
            
            if messages:
                # Get first message details for summary
                first_message = messages[0]
                headers = first_message.get('payload', {}).get('headers', [])
                
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(No subject)')
                
                thread_list.append({
                    'id': thread['id'],
                    'subject': subject,
                    'message_count': len(messages),
                    'snippet': first_message.get('snippet', '')
                })
        
        return jsonify({
            "status": "success",
            "count": len(thread_list),
            "threads": thread_list
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@auth_bp.route('/threads/<thread_id>')
def thread_detail(thread_id):
    """Get a thread with all its messages"""
    # Check if the service is authenticated
    service = gmail_service.build_service()
    if not service:
        return redirect(url_for('auth.login'))
    
    try:
        # Get the thread with all messages
        thread_data = gmail_service.get_thread_with_messages(thread_id)
        
        return jsonify({
            "status": "success",
            "thread": thread_data
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@auth_bp.route('/search')
def search():
    """Search for emails"""
    # Get query parameter
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({"status": "error", "message": "Search query is required"})
    
    # Check if the service is authenticated
    service = gmail_service.build_service()
    if not service:
        return redirect(url_for('auth.login'))
    
    try:
        # Search for messages
        messages = gmail_service.search_messages(query, max_results=10)
        
        message_list = []
        for msg in messages:
            # Get message details
            message = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = message.get('payload', {}).get('headers', [])
            
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(No subject)')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '(Unknown sender)')
            
            message_list.append({
                'id': msg['id'],
                'thread_id': message.get('threadId', ''),
                'subject': subject,
                'sender': sender,
                'snippet': message.get('snippet', '')
            })
        
        return jsonify({
            "status": "success",
            "count": len(message_list),
            "query": query,
            "emails": message_list
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@auth_bp.route('/test')
def test_connection():
    """Simple route to test the Gmail API connection"""
    success = gmail_service.test_connection()
    return jsonify({
        "status": "success" if success else "error",
        "message": "Gmail API connection test completed"
    })