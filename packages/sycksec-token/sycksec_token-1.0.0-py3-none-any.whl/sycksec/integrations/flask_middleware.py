"""Flask integration for SyckSec Community Edition"""
from flask import request, g
from functools import wraps
from .. import SyckSec

def create_sycksec_app(app, master_secret=None):
    """Initialize SyckSec with Flask app"""
    app.sycksec = SyckSec() if not master_secret else SyckSec.create_client(master_secret)
    return app.sycksec

def sycksec_required(f):
    """Decorator to require SyckSec token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('SyckSec '):
            return {'error': 'SyckSec token required'}, 401
        
        token = auth_header[8:]
        user_id = request.args.get('user_id') or request.json.get('user_id')
        
        if not user_id:
            return {'error': 'user_id required'}, 400
        
        try:
            from flask import current_app
            payload = current_app.sycksec.verify(token, user_id)
            g.sycksec_payload = payload
            return f(*args, **kwargs)
        except Exception as e:
            return {'error': f'Invalid token: {str(e)}'}, 401
    
    return decorated_function
