from flask import Blueprint, jsonify, request, current_app
from flask_restful import Resource, Api

from app.services.email_pipeline import EmailPipeline

# Create a blueprint for email-related routes
email_bp = Blueprint('email', __name__, url_prefix='/api/emails')
api = Api(email_bp)

class ProcessEmailsResource(Resource):
    """API resource for processing emails"""
    
    def post(self):
        """Process new emails and create capsules"""
        # Get parameters from request
        data = request.get_json() or {}
        max_emails = data.get('max_emails', 10)
        
        # Initialize the email pipeline
        pipeline = EmailPipeline()
        
        # Check if Gmail service is authenticated
        if not pipeline.is_authenticated():
            return jsonify({
                "success": False,
                "error": "Gmail service not authenticated",
                "message": "Please authenticate with Gmail first"
            }), 401
        
        # Process emails
        result = pipeline.process_emails(max_emails)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "processed_emails": result["processed_emails"],
                "created_capsules": result["created_capsules"],
                "message": f"Successfully processed {result['processed_emails']} emails and created {result['created_capsules']} capsules"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Unknown error"),
                "message": "Failed to process emails"
            }), 500

class EmailResource(Resource):
    """API resource for individual emails"""
    
    def get(self, email_id):
        """Get a specific email by ID"""
        # Initialize the email pipeline
        pipeline = EmailPipeline()
        
        # Check if Gmail service is authenticated
        if not pipeline.is_authenticated():
            return jsonify({
                "success": False,
                "error": "Gmail service not authenticated",
                "message": "Please authenticate with Gmail first"
            }), 401
        
        # Get the email
        email_model = pipeline.email_processor.get_email_by_id(email_id)
        
        if email_model:
            return jsonify({
                "success": True,
                "email": email_model.to_dict()
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Email not found",
                "message": f"Email with ID {email_id} not found"
            }), 404

class ThreadEmailsResource(Resource):
    """API resource for emails in a thread"""
    
    def get(self, thread_id):
        """Get all emails in a thread"""
        # Initialize the email pipeline
        pipeline = EmailPipeline()
        
        # Check if Gmail service is authenticated
        if not pipeline.is_authenticated():
            return jsonify({
                "success": False,
                "error": "Gmail service not authenticated",
                "message": "Please authenticate with Gmail first"
            }), 401
        
        # Get the emails in the thread
        emails = pipeline.email_processor.get_emails_by_thread(thread_id)
        
        return jsonify({
            "success": True,
            "thread_id": thread_id,
            "emails": [email.to_dict() for email in emails],
            "count": len(emails)
        }), 200

# Register the resources with the API
api.add_resource(ProcessEmailsResource, '/process')
api.add_resource(EmailResource, '/<string:email_id>')
api.add_resource(ThreadEmailsResource, '/thread/<string:thread_id>')

# Function to register the blueprint with the Flask app
def register_email_routes(app):
    app.register_blueprint(email_bp) 