"""
Mock Authentication System for Testing
Provides fake login/signup functionality when real OAuth isn't available
"""
from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, current_user
import uuid
from datetime import datetime

mock_auth_bp = Blueprint('mock_auth', __name__, url_prefix='/api/mock')

# Mock user database (in-memory for testing)
MOCK_USERS = {
    # Regular test users
    'demo@tradinggrow.com': {
        'id': 'demo-user-1',
        'email': 'demo@tradinggrow.com',
        'full_name': 'Demo User',
        'password': 'demo123',
        'subscription_tier': 'pro',
        'is_admin': False,
        'created_at': '2024-01-01T00:00:00Z'
    },
    'john@example.com': {
        'id': 'demo-user-2',
        'email': 'john@example.com',
        'full_name': 'John Smith',
        'password': 'password123',
        'subscription_tier': 'free',
        'is_admin': False,
        'created_at': '2024-01-15T10:30:00Z'
    },
    'sarah@example.com': {
        'id': 'demo-user-3',
        'email': 'sarah@example.com',
        'full_name': 'Sarah Johnson',
        'password': 'password123',
        'subscription_tier': 'medium',
        'is_admin': False,
        'created_at': '2024-02-01T14:20:00Z'
    },
    # Admin test users
    'admin@tradinggrow.com': {
        'id': 'admin-user-1',
        'email': 'admin@tradinggrow.com',
        'full_name': 'Admin User',
        'password': 'admin123',
        'subscription_tier': 'pro',
        'is_admin': True,
        'created_at': '2024-01-01T00:00:00Z'
    },
    'superadmin@tradinggrow.com': {
        'id': 'admin-user-2',
        'email': 'superadmin@tradinggrow.com',
        'full_name': 'Super Admin',
        'password': 'admin123',
        'subscription_tier': 'pro',
        'is_admin': True,
        'created_at': '2024-01-01T00:00:00Z'
    }
}

# Mock user class for Flask-Login compatibility
class MockUser:
    def __init__(self, user_data):
        self.id = user_data['id']
        self.email = user_data['email']
        self.full_name = user_data['full_name']
        self.subscription_tier = user_data['subscription_tier']
        self.is_admin = user_data['is_admin']
        self.created_at = user_data['created_at']
        self.password_hash = user_data.get('password_hash')
    
    def get_id(self):
        return self.id
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False

@mock_auth_bp.route('/login', methods=['POST'])
def mock_login():
    """Mock login endpoint"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({
            'success': False,
            'error': 'Email and password are required'
        }), 400
    
    # Check if user exists in mock database
    user_data = MOCK_USERS.get(email)
    if not user_data:
        return jsonify({
            'success': False,
            'error': 'Invalid email or password'
        }), 401
    
    # Check password (simple text comparison for demo)
    if user_data['password'] != password:
        return jsonify({
            'success': False,
            'error': 'Invalid email or password'
        }), 401
    
    # Create mock user object and log in
    mock_user = MockUser(user_data)
    
    # Store user in session for Flask-Login compatibility
    session['mock_user_id'] = user_data['id']
    session['mock_user_data'] = user_data
    
    return jsonify({
        'success': True,
        'message': 'Login successful (Mock Mode)',
        'user': {
            'id': user_data['id'],
            'email': user_data['email'],
            'username': user_data['full_name'],
            'full_name': user_data['full_name'],
            'subscription_tier': user_data['subscription_tier'],
            'is_admin': user_data['is_admin'],
            'created_at': user_data['created_at']
        },
        'mock_mode': True
    })

@mock_auth_bp.route('/signup', methods=['POST'])
def mock_signup():
    """Mock signup endpoint"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    username = data.get('username', '')
    
    if not email or not password:
        return jsonify({
            'success': False,
            'error': 'Email and password are required'
        }), 400
    
    # Check if user already exists
    if email in MOCK_USERS:
        return jsonify({
            'success': False,
            'error': 'User with this email already exists'
        }), 400
    
    # Create new mock user
    new_user_id = f'mock-user-{len(MOCK_USERS) + 1}'
    new_user_data = {
        'id': new_user_id,
        'email': email,
        'full_name': username or email.split('@')[0].title(),
        'password': password,
        'subscription_tier': 'free',
        'is_admin': False,
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    # Add to mock database
    MOCK_USERS[email] = new_user_data
    
    # Store user in session
    session['mock_user_id'] = new_user_data['id']
    session['mock_user_data'] = new_user_data
    
    return jsonify({
        'success': True,
        'message': 'Account created successfully (Mock Mode)',
        'user': {
            'id': new_user_data['id'],
            'email': new_user_data['email'],
            'username': new_user_data['full_name'],
            'full_name': new_user_data['full_name'],
            'subscription_tier': new_user_data['subscription_tier'],
            'is_admin': new_user_data['is_admin'],
            'created_at': new_user_data['created_at']
        },
        'mock_mode': True
    })

@mock_auth_bp.route('/admin/login', methods=['POST'])
def mock_admin_login():
    """Mock admin login endpoint"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({
            'success': False,
            'error': 'Email and password are required'
        }), 400
    
    # Check if user exists in mock database
    user_data = MOCK_USERS.get(email)
    if not user_data:
        return jsonify({
            'success': False,
            'error': 'Invalid admin credentials'
        }), 401
    
    # Check if user is admin
    if not user_data.get('is_admin', False):
        return jsonify({
            'success': False,
            'error': 'Access denied - Admin privileges required'
        }), 403
    
    # Check password (simple text comparison for demo)
    if user_data['password'] != password:
        return jsonify({
            'success': False,
            'error': 'Invalid admin credentials'
        }), 401
    
    # Store admin user in session
    session['mock_user_id'] = user_data['id']
    session['mock_user_data'] = user_data
    session['is_admin'] = True
    
    return jsonify({
        'success': True,
        'message': 'Admin login successful (Mock Mode)',
        'user': {
            'id': user_data['id'],
            'email': user_data['email'],
            'username': user_data['full_name'],
            'full_name': user_data['full_name'],
            'subscription_tier': user_data['subscription_tier'],
            'is_admin': user_data['is_admin'],
            'created_at': user_data['created_at']
        },
        'redirect': '/admin/dashboard',
        'mock_mode': True
    })

@mock_auth_bp.route('/logout', methods=['POST'])
def mock_logout():
    """Mock logout endpoint"""
    session.pop('mock_user_id', None)
    session.pop('mock_user_data', None)
    session.pop('is_admin', None)
    
    return jsonify({
        'success': True,
        'message': 'Logged out successfully',
        'mock_mode': True
    })

@mock_auth_bp.route('/user', methods=['GET'])
def mock_current_user():
    """Get current mock user information"""
    user_data = session.get('mock_user_data')
    
    if not user_data:
        return jsonify({
            'authenticated': False,
            'mock_mode': True
        })
    
    return jsonify({
        'authenticated': True,
        'user': {
            'id': user_data['id'],
            'email': user_data['email'],
            'username': user_data['full_name'],
            'full_name': user_data['full_name'],
            'subscription_tier': user_data['subscription_tier'],
            'is_admin': user_data['is_admin'],
            'created_at': user_data['created_at']
        },
        'mock_mode': True
    })

@mock_auth_bp.route('/test-users', methods=['GET'])
def get_test_users():
    """Get list of available test users for easy login"""
    test_users = []
    for email, user_data in MOCK_USERS.items():
        test_users.append({
            'email': email,
            'password': user_data['password'],
            'full_name': user_data['full_name'],
            'subscription_tier': user_data['subscription_tier'],
            'is_admin': user_data['is_admin']
        })
    
    return jsonify({
        'test_users': test_users,
        'mock_mode': True
    })