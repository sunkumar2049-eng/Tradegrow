from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
import datetime
import csv
import io

admin_bp = Blueprint('admin', __name__)

def require_admin_session():
    """Check if user is logged in as admin in session"""
    user_data = session.get('mock_user_data')
    if not user_data or not user_data.get('is_admin', False):
        return False
    return True

# Mock data for admin functionality
MOCK_USERS = [
    {
        'id': '1',
        'email': 'admin@tradinggrow.com',
        'full_name': 'Admin User',
        'subscription_tier': 'pro',
        'is_admin': True,
        'created_at': '2024-01-01T00:00:00Z'
    },
    {
        'id': '2',
        'email': 'demo@tradinggrow.com',
        'full_name': 'Demo User',
        'subscription_tier': 'pro',
        'is_admin': False,
        'created_at': '2024-01-15T00:00:00Z'
    },
    {
        'id': '3',
        'email': 'user1@example.com',
        'full_name': 'John Smith',
        'subscription_tier': 'medium',
        'is_admin': False,
        'created_at': '2024-02-01T00:00:00Z'
    },
    {
        'id': '4',
        'email': 'user2@example.com',
        'full_name': 'Jane Doe',
        'subscription_tier': 'free',
        'is_admin': False,
        'created_at': '2024-02-15T00:00:00Z'
    },
    {
        'id': '5',
        'email': 'user3@example.com',
        'full_name': 'Bob Wilson',
        'subscription_tier': 'free',
        'is_admin': False,
        'created_at': '2024-03-01T00:00:00Z'
    }
]

MOCK_STOCKS = [
    {
        'id': '1',
        'symbol': 'AAPL',
        'name': 'Apple Inc.',
        'sector': 'Technology',
        'industry_type': 'Consumer Electronics',
        'industry_code': 'TECH001',
        'price': 175.50,
        'change_percent': 2.3
    },
    {
        'id': '2',
        'symbol': 'GOOGL',
        'name': 'Alphabet Inc.',
        'sector': 'Technology',
        'industry_type': 'Internet Services',
        'industry_code': 'TECH002',
        'price': 2850.25,
        'change_percent': -1.2
    },
    {
        'id': '3',
        'symbol': 'MSFT',
        'name': 'Microsoft Corporation',
        'sector': 'Technology',
        'industry_type': 'Software',
        'industry_code': 'TECH003',
        'price': 420.15,
        'change_percent': 1.8
    },
    {
        'id': '4',
        'symbol': 'TSLA',
        'name': 'Tesla Inc.',
        'sector': 'Consumer',
        'industry_type': 'Electric Vehicles',
        'industry_code': 'AUTO001',
        'price': 245.80,
        'change_percent': -3.5
    },
    {
        'id': '5',
        'symbol': 'HD',
        'name': 'Home Depot Inc.',
        'sector': 'Wholesale Distributors',
        'industry_type': 'Home Improvement',
        'industry_code': 'RETAIL001',
        'price': 320.45,
        'change_percent': 1.5
    },
    {
        'id': '6',
        'symbol': 'LOW',
        'name': 'Lowe\'s Companies',
        'sector': 'Wholesale Distributors',
        'industry_type': 'Home Improvement',
        'industry_code': 'RETAIL002',
        'price': 225.80,
        'change_percent': 0.8
    },
    {
        'id': '7',
        'symbol': 'JPM',
        'name': 'JPMorgan Chase',
        'sector': 'Financials',
        'industry_type': 'Banking',
        'industry_code': 'FIN001',
        'price': 145.30,
        'change_percent': -0.5
    },
    {
        'id': '8',
        'symbol': 'BAC',
        'name': 'Bank of America',
        'sector': 'Financials',
        'industry_type': 'Banking',
        'industry_code': 'FIN002',
        'price': 35.75,
        'change_percent': 1.2
    }
]

MOCK_SUBSCRIPTION_REQUESTS = [
    {
        'id': '1',
        'user_id': '3',
        'user_name': 'John Smith',
        'user_email': 'user1@example.com',
        'current_tier': 'medium',
        'requested_tier': 'pro',
        'created_at': '2024-03-15T10:00:00Z'
    }
]

@admin_bp.route('/admin/login')
def admin_login():
    """Admin login page"""
    return render_template('spa.html')

@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard page"""
    if not require_admin_session():
        return redirect('/admin/login')
    return render_template('spa.html')

@admin_bp.route('/admin/logout', methods=['GET', 'POST'])
def admin_logout():
    """Admin logout endpoint"""
    session.pop('mock_user_id', None)
    session.pop('mock_user_data', None)
    session.pop('is_admin', None)
    
    # Return JSON for AJAX requests, redirect for direct browser access
    if request.method == 'POST' or request.headers.get('Content-Type') == 'application/json':
        return jsonify({'message': 'Logged out successfully'})
    else:
        return redirect('/admin/login')

# API Endpoints

@admin_bp.route('/admin/api/dashboard-data')
def admin_dashboard_data():
    """Get admin dashboard statistics"""
    if not require_admin_session():
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify({
        'success': True,
        'data': {
            'stats': {
                'total_users': len(MOCK_USERS),
                'pro_users': len([u for u in MOCK_USERS if u['subscription_tier'] == 'pro']),
                'medium_users': len([u for u in MOCK_USERS if u['subscription_tier'] == 'medium']),
                'free_users': len([u for u in MOCK_USERS if u['subscription_tier'] == 'free']),
                'total_screenings': 89
            },
            'screenings': [
                {
                    'id': 1,
                    'name': 'High Growth Stocks',
                    'results_count': 23,
                    'created_at': '2024-03-15T10:00:00Z'
                },
                {
                    'id': 2,
                    'name': 'Value Stocks',
                    'results_count': 18,
                    'created_at': '2024-03-14T15:30:00Z'
                }
            ]
        }
    })

@admin_bp.route('/admin/api/users')
def get_all_users():
    """Get all users for admin management"""
    if not require_admin_session():
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify({
        'success': True,
        'users': MOCK_USERS
    })

@admin_bp.route('/admin/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user information"""
    if not require_admin_session():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    # Find and update user in mock data
    for user in MOCK_USERS:
        if user['id'] == user_id:
            user.update({
                'email': data.get('email', user['email']),
                'full_name': data.get('full_name', user['full_name']),
                'subscription_tier': data.get('subscription_tier', user['subscription_tier']),
                'is_admin': data.get('is_admin', user['is_admin'])
            })
            return jsonify({'success': True, 'message': 'User updated successfully'})
    
    return jsonify({'error': 'User not found'}), 404

@admin_bp.route('/admin/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    if not require_admin_session():
        return jsonify({'error': 'Unauthorized'}), 401
    
    global MOCK_USERS
    MOCK_USERS = [u for u in MOCK_USERS if u['id'] != user_id]
    
    return jsonify({'success': True, 'message': 'User deleted successfully'})

@admin_bp.route('/admin/api/users/<user_id>/subscription', methods=['PUT'])
def update_user_subscription(user_id):
    """Update user subscription tier"""
    if not require_admin_session():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    new_tier = data.get('subscription_tier')
    
    # Find and update user subscription
    for user in MOCK_USERS:
        if user['id'] == user_id:
            user['subscription_tier'] = new_tier
            return jsonify({'success': True, 'message': f'Subscription updated to {new_tier}'})
    
    return jsonify({'error': 'User not found'}), 404

@admin_bp.route('/admin/api/subscription-requests')
def get_subscription_requests():
    """Get all pending subscription requests"""
    if not require_admin_session():
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify({
        'success': True,
        'requests': MOCK_SUBSCRIPTION_REQUESTS
    })

@admin_bp.route('/admin/api/subscription-requests/<request_id>/<action>', methods=['POST'])
def handle_subscription_request(request_id, action):
    """Approve or reject subscription request"""
    if not require_admin_session():
        return jsonify({'error': 'Unauthorized'}), 401
    
    global MOCK_SUBSCRIPTION_REQUESTS
    
    # Find the request
    request_obj = None
    for req in MOCK_SUBSCRIPTION_REQUESTS:
        if req['id'] == request_id:
            request_obj = req
            break
    
    if not request_obj:
        return jsonify({'error': 'Request not found'}), 404
    
    if action == 'approve':
        # Update user subscription
        for user in MOCK_USERS:
            if user['id'] == request_obj['user_id']:
                user['subscription_tier'] = request_obj['requested_tier']
                break
        
        # Remove request
        MOCK_SUBSCRIPTION_REQUESTS = [r for r in MOCK_SUBSCRIPTION_REQUESTS if r['id'] != request_id]
        
        return jsonify({
            'success': True, 
            'message': f"Subscription upgraded to {request_obj['requested_tier']}"
        })
    
    elif action == 'reject':
        # Remove request
        MOCK_SUBSCRIPTION_REQUESTS = [r for r in MOCK_SUBSCRIPTION_REQUESTS if r['id'] != request_id]
        
        return jsonify({
            'success': True,
            'message': 'Subscription request rejected'
        })
    
    return jsonify({'error': 'Invalid action'}), 400

@admin_bp.route('/admin/api/bulk-upgrade', methods=['POST'])
def bulk_upgrade_users():
    """Bulk upgrade users from one tier to another"""
    if not require_admin_session():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    from_tier = data.get('from_tier')
    to_tier = data.get('to_tier')
    
    updated_count = 0
    for user in MOCK_USERS:
        if user['subscription_tier'] == from_tier and not user.get('is_admin', False):
            user['subscription_tier'] = to_tier
            updated_count += 1
    
    return jsonify({
        'success': True,
        'message': f'Upgraded {updated_count} users from {from_tier} to {to_tier}',
        'updated_count': updated_count
    })

@admin_bp.route('/admin/api/stocks', methods=['GET'])
def get_all_stocks():
    """Get all stocks for management"""
    return jsonify({
        'success': True,
        'stocks': MOCK_STOCKS
    })

@admin_bp.route('/admin/api/stocks/by-industry', methods=['GET'])
def get_stocks_by_industry():
    """Get stocks organized by industry"""
    industry_groups = {}
    
    for stock in MOCK_STOCKS:
        industry_type = stock.get('industry_type', 'Other')
        industry_code = stock.get('industry_code', 'N/A')
        sector = stock.get('sector', 'Other')
        
        # Group by sector first, then by industry type
        if sector not in industry_groups:
            industry_groups[sector] = {}
        
        if industry_type not in industry_groups[sector]:
            industry_groups[sector][industry_type] = {
                'industry_code': industry_code,
                'stocks': []
            }
        
        industry_groups[sector][industry_type]['stocks'].append(stock)
    
    return jsonify({
        'success': True,
        'industries': industry_groups,
        'total_stocks': len(MOCK_STOCKS)
    })

@admin_bp.route('/admin/api/stocks', methods=['POST'])
def add_stock():
    """Add a new stock"""
    if not require_admin_session():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    new_stock = {
        'id': str(len(MOCK_STOCKS) + 1),
        'symbol': data.get('symbol', '').upper(),
        'name': data.get('name', ''),
        'sector': data.get('sector', ''),
        'price': float(data.get('price', 0)),
        'change_percent': float(data.get('change_percent', 0))
    }
    
    MOCK_STOCKS.append(new_stock)
    
    return jsonify({
        'success': True,
        'message': 'Stock added successfully',
        'stock': new_stock
    })

@admin_bp.route('/admin/api/stocks/<stock_id>', methods=['DELETE'])
def delete_stock(stock_id):
    """Delete a stock"""
    if not require_admin_session():
        return jsonify({'error': 'Unauthorized'}), 401
    
    global MOCK_STOCKS
    MOCK_STOCKS = [s for s in MOCK_STOCKS if s['id'] != stock_id]
    
    return jsonify({
        'success': True,
        'message': 'Stock removed successfully'
    })

@admin_bp.route('/admin/api/stocks/<stock_id>/price', methods=['PUT'])
def update_stock_price(stock_id):
    """Update stock price"""
    if not require_admin_session():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    new_price = float(data.get('price', 0))
    
    for stock in MOCK_STOCKS:
        if stock['id'] == stock_id:
            old_price = stock['price']
            stock['price'] = new_price
            # Calculate change percentage
            if old_price > 0:
                stock['change_percent'] = ((new_price - old_price) / old_price) * 100
            return jsonify({'success': True, 'message': 'Stock price updated'})
    
    return jsonify({'error': 'Stock not found'}), 404

@admin_bp.route('/admin/api/stocks/bulk-upload', methods=['POST'])
def bulk_upload_stocks():
    """Bulk upload stocks from CSV file"""
    if not require_admin_session():
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'csvFile' not in request.files:
        return jsonify({'error': 'No CSV file provided'}), 400
    
    file = request.files['csvFile']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename or not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV file'}), 400
    
    try:
        # Read CSV file content
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        processed_count = 0
        error_count = 0
        errors = []
        
        global MOCK_STOCKS
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start from 2 to account for header
            try:
                # Validate required fields
                required_fields = ['symbol', 'name', 'sector', 'price']
                missing_fields = [field for field in required_fields if not row.get(field, '').strip()]
                
                if missing_fields:
                    error_count += 1
                    errors.append(f"Row {row_num}: Missing required fields: {', '.join(missing_fields)}")
                    continue
                
                # Process the stock data
                stock_data = {
                    'id': str(len(MOCK_STOCKS) + processed_count + 1),
                    'symbol': row['symbol'].strip().upper(),
                    'name': row['name'].strip(),
                    'sector': row['sector'].strip(),
                    'industry_type': row.get('industry_type', '').strip(),
                    'industry_code': row.get('industry_code', '').strip(),
                    'price': float(row['price']),
                    'change_percent': float(row.get('change_percent', 0))
                }
                
                # Check for duplicate symbols
                existing_stock = next((s for s in MOCK_STOCKS if s['symbol'] == stock_data['symbol']), None)
                if existing_stock:
                    # Update existing stock
                    existing_stock.update(stock_data)
                    existing_stock['id'] = existing_stock['id']  # Keep original ID
                else:
                    # Add new stock
                    MOCK_STOCKS.append(stock_data)
                
                processed_count += 1
                
            except ValueError as e:
                error_count += 1
                errors.append(f"Row {row_num}: Invalid data format - {str(e)}")
            except Exception as e:
                error_count += 1
                errors.append(f"Row {row_num}: Error processing row - {str(e)}")
        
        # Prepare response
        response_data = {
            'success': True,
            'message': f'CSV processed successfully! {processed_count} stocks processed.',
            'processed': processed_count,
            'errors': error_count,
            'total_stocks': len(MOCK_STOCKS)
        }
        
        if errors:
            response_data['error_details'] = errors[:10]  # Limit to first 10 errors
            
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to process CSV file: {str(e)}'
        }), 500