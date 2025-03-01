from flask import Flask, jsonify, send_from_directory
from flask_restful import Api
import os

def create_app():
    app = Flask(__name__, static_folder='static/dist')
    api = Api(app)
    
    # Set a secret key for session management
    app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
    
    # Register routes
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Register email routes
    from app.api.email_routes import register_email_routes
    register_email_routes(app)
    
    @app.route("/")
    def index():
        return send_from_directory('templates', 'index.html')
    
    @app.route("/api/health")
    def health_check():
        return jsonify({"status": "ok", "message": "CRE Email Assistant is running"})
    
    # Catch-all route to handle React Router
    @app.route('/<path:path>')
    def catch_all(path):
        if path.startswith('api/') or path.startswith('auth/'):
            return app.handle_http_exception(404)
        return send_from_directory('templates', 'index.html')
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)