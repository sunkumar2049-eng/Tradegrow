from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from models import User
import uuid
from collections import defaultdict

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/auth/me', methods=['GET'])
def get_current_user():
    """Get current user data"""
    # Check for Flask-Login authentication first
    if current_user.is_authenticated:
        user_data = {
            'id': current_user.id,
            'username': current_user.full_name or current_user.email.split('@')[0],
            'email': current_user.email,
            'subscription_tier': current_user.subscription_tier,
            'is_admin': current_user.is_admin
        }
        
        # Get watchlists and sector data
        try:
            from financial_data_service import financial_service
            from data_service import get_watchlists_for_user
            watchlists = get_watchlists_for_user(current_user.id)
            sector_data = financial_service.get_sector_performance()
        except ImportError:
            # Fallback for testing
            watchlists = []
            sector_data = {}
        
        return jsonify({
            'user': user_data,
            'watchlists': watchlists,
            'sectorData': sector_data
        })
    
    # Check for mock authentication session
    mock_user_data = session.get('mock_user_data')
    if mock_user_data:
        user_data = {
            'id': mock_user_data['id'],
            'username': mock_user_data.get('full_name', mock_user_data['email'].split('@')[0]),
            'email': mock_user_data['email'],
            'subscription_tier': mock_user_data.get('subscription_tier', 'free'),
            'is_admin': mock_user_data.get('is_admin', False)
        }
        
        # For mock users, return minimal data
        watchlists = []
        sector_data = {}
        
        return jsonify({
            'user': user_data,
            'watchlists': watchlists,
            'sectorData': sector_data
        })
    
    return jsonify({'user': None}), 401

@api.route('/auth/login', methods=['POST'])
def api_login():
    """API endpoint for login"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        user_data = {
            'id': user.id,
            'username': user.full_name or user.email.split('@')[0],
            'email': user.email,
            'subscription_tier': user.subscription_tier,
            'is_admin': user.is_admin
        }
        return jsonify({'user': user_data, 'message': 'Login successful'})
    
    return jsonify({'error': 'Invalid email or password'}), 401


@api.route('/auth/signup', methods=['POST'])
def api_signup():
    """API endpoint for signup"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'error': 'Username, email and password are required'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'User with this email already exists'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 400
    
    # Create new user  
    user = User(
        email=email,
        password=password,
        full_name=username
    )
    
    db.session.add(user)
    db.session.commit()
    
    login_user(user)
    
    user_data = {
        'id': user.id,
        'username': user.full_name or user.email.split('@')[0],
        'email': user.email,
        'subscription_tier': user.subscription_tier,
        'is_admin': user.is_admin
    }
    
    return jsonify({'user': user_data, 'message': 'Account created successfully'})

@api.route('/auth/logout', methods=['POST'])
def api_logout():
    """API endpoint for logout - handles both regular and mock authentication"""
    # Try to logout Flask-Login user
    if current_user.is_authenticated:
        logout_user()
    
    # Clear mock session data
    session.pop('mock_user_id', None)
    session.pop('mock_user_data', None)
    session.pop('is_admin', None)
    
    return jsonify({'message': 'Logged out successfully'})

@api.route('/user/data', methods=['GET'])
@login_required
def get_user_data():
    """Get user dashboard data"""
    try:
        from data_service import get_watchlists_for_user, get_sector_data
        watchlists = get_watchlists_for_user(current_user.id)
        sector_data = get_sector_data()
    except ImportError:
        watchlists = []
        sector_data = {}
    
    user_data = {
        'id': current_user.id,
        'username': current_user.full_name or current_user.email.split('@')[0],
        'email': current_user.email,
        'subscription_tier': current_user.subscription_tier,
        'is_admin': current_user.is_admin
    }
    
    return jsonify({
        'user': user_data,
        'watchlists': watchlists,
        'sectorData': sector_data
    })

@api.route('/user/request-subscription', methods=['POST'])
@login_required
def request_subscription():
    """Request subscription upgrade"""
    data = request.get_json()
    tier = data.get('tier')
    
    if tier not in ['medium', 'pro']:
        return jsonify({'error': 'Invalid subscription tier'}), 400
    
    from models import SubscriptionRequest
    
    # Check if user already has a pending request
    existing_request = SubscriptionRequest.query.filter_by(
        user_id=current_user.id,
        status='pending'
    ).first()
    
    if existing_request:
        return jsonify({'error': 'You already have a pending subscription request'}), 400
    
    # Create new subscription request
    request_obj = SubscriptionRequest(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        tier=tier,
        status='pending'
    )
    
    db.session.add(request_obj)
    db.session.commit()
    
    return jsonify({'message': 'Subscription request submitted successfully'})

@api.route('/admin/users', methods=['GET'])
@login_required
def get_all_users():
    """Get all users (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    users = User.query.all()
    users_data = []
    
    for user in users:
        users_data.append({
            'id': user.id,
            'username': user.full_name or user.email.split('@')[0],
            'email': user.email,
            'subscription_tier': user.subscription_tier,
            'is_admin': user.is_admin,
            'created_at': user.created_at.isoformat() if user.created_at else None
        })
    
    return jsonify({'users': users_data})

@api.route('/admin/subscription-requests', methods=['GET'])
@login_required
def get_subscription_requests():
    """Get all subscription requests (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    from models import SubscriptionRequest
    
    requests = SubscriptionRequest.query.filter_by(status='pending').all()
    requests_data = []
    
    for req in requests:
        user = User.query.get(req.user_id)
        requests_data.append({
            'id': req.id,
            'user_id': req.user_id,
            'username': (user.full_name or user.email.split('@')[0]) if user else 'Unknown',
            'email': user.email if user else 'Unknown',
            'tier': req.tier,
            'status': req.status,
            'created_at': req.created_at.isoformat() if req.created_at else None
        })
    
    return jsonify({'requests': requests_data})

@api.route('/admin/subscription-requests/<request_id>/approve', methods=['POST'])
@login_required
def approve_subscription_request(request_id):
    """Approve a subscription request (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    from models import SubscriptionRequest
    
    req = SubscriptionRequest.query.get(request_id)
    if not req:
        return jsonify({'error': 'Request not found'}), 404
    
    if req.status != 'pending':
        return jsonify({'error': 'Request is not pending'}), 400
    
    # Update user subscription
    user = User.query.get(req.user_id)
    if user:
        user.subscription_tier = req.tier
    
    # Update request status
    req.status = 'approved'
    
    db.session.commit()
    
    return jsonify({'message': 'Subscription request approved successfully'})

@api.route('/admin/subscription-requests/<request_id>/reject', methods=['POST'])
@login_required
def reject_subscription_request(request_id):
    """Reject a subscription request (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    from models import SubscriptionRequest
    
    req = SubscriptionRequest.query.get(request_id)
    if not req:
        return jsonify({'error': 'Request not found'}), 404
    
    if req.status != 'pending':
        return jsonify({'error': 'Request is not pending'}), 400
    
    req.status = 'rejected'
    db.session.commit()
    
    return jsonify({'message': 'Subscription request rejected'})

# Stock screening and watchlist endpoints can be added here as needed

@api.route('/stocks/by-industry', methods=['GET'])
def get_stocks_by_industry():
    """Get stocks organized by sector and industry - user accessible"""
    try:
        # Import the mock stocks data from admin routes
        from admin_routes import MOCK_STOCKS
        
        # Group stocks by sector and industry
        industries = defaultdict(lambda: defaultdict(lambda: {'industry_code': '', 'stocks': []}))
        
        for stock in MOCK_STOCKS:
            sector = stock.get('sector', 'Unknown')
            industry_type = stock.get('industry_type', 'Unknown')
            industry_code = stock.get('industry_code', 'N/A')
            
            # Set industry code if not already set
            if not industries[sector][industry_type]['industry_code']:
                industries[sector][industry_type]['industry_code'] = industry_code
            
            # Add stock to industry
            industries[sector][industry_type]['stocks'].append({
                'symbol': stock['symbol'],
                'name': stock['name'],
                'price': stock['price'],
                'change_percent': stock.get('change_percent', 0)
            })
        
        # Convert defaultdict to regular dict for JSON serialization
        result = {}
        for sector, sector_industries in industries.items():
            result[sector] = {}
            for industry, industry_data in sector_industries.items():
                result[sector][industry] = {
                    'industry_code': industry_data['industry_code'],
                    'stocks': industry_data['stocks']
                }
        
        return jsonify({'industries': result})
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to load industry data: {str(e)}',
            'industries': {}
        }), 500