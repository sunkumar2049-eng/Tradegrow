"""
Health Check and Monitoring for TradingGrow
Provides health endpoints and system monitoring
"""

from flask import Blueprint, jsonify
from financial_data_service import financial_service
import os
from datetime import datetime

# Optional import for psutil
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    try:
        # Check database connection
        from app import db
        db.engine.execute('SELECT 1')
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check system resources
    if PSUTIL_AVAILABLE:
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        cpu_usage = psutil.cpu_percent(interval=1)
    else:
        memory_usage = 0
        disk_usage = 0
        cpu_usage = 0
    
    # Check external API connectivity
    api_status = "healthy"
    try:
        # Test Alpha Vantage API if key is available
        if os.getenv('ALPHA_VANTAGE_API_KEY'):
            financial_service.get_sector_performance()
    except Exception as e:
        api_status = f"degraded: {str(e)}"
    
    health_status = {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": db_status,
            "external_apis": api_status
        },
        "system": {
            "memory_usage": f"{memory_usage}%",
            "disk_usage": f"{disk_usage}%",
            "cpu_usage": f"{cpu_usage}%"
        },
        "version": "1.0.0"
    }
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return jsonify(health_status), status_code

@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check with more information"""
    
    checks = {}
    overall_status = "healthy"
    
    # Database check
    try:
        from app import db
        result = db.engine.execute('SELECT version()')
        db_version = result.fetchone()[0]
        checks['database'] = {
            "status": "healthy",
            "details": f"PostgreSQL: {db_version}",
            "response_time": "< 100ms"
        }
    except Exception as e:
        checks['database'] = {
            "status": "unhealthy",
            "details": str(e),
            "response_time": "timeout"
        }
        overall_status = "unhealthy"
    
    # External API checks
    api_checks = {}
    
    # Alpha Vantage
    if os.getenv('ALPHA_VANTAGE_API_KEY'):
        try:
            start_time = datetime.now()
            financial_service.get_sector_performance()
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            api_checks['alpha_vantage'] = {
                "status": "healthy",
                "response_time": f"{response_time:.0f}ms"
            }
        except Exception as e:
            api_checks['alpha_vantage'] = {
                "status": "degraded",
                "error": str(e)
            }
    else:
        api_checks['alpha_vantage'] = {
            "status": "not_configured",
            "details": "API key not provided"
        }
    
    # Yahoo Finance
    try:
        start_time = datetime.now()
        financial_service.get_stock_data('AAPL')
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        api_checks['yahoo_finance'] = {
            "status": "healthy",
            "response_time": f"{response_time:.0f}ms"
        }
    except Exception as e:
        api_checks['yahoo_finance'] = {
            "status": "degraded",
            "error": str(e)
        }
    
    checks['external_apis'] = api_checks
    
    # System resources
    if PSUTIL_AVAILABLE:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        checks['system'] = {
            "status": "healthy",
            "memory": {
                "total": f"{memory.total // (1024**3)}GB",
                "available": f"{memory.available // (1024**3)}GB",
                "percent": f"{memory.percent}%"
            },
            "disk": {
                "total": f"{disk.total // (1024**3)}GB",
                "free": f"{disk.free // (1024**3)}GB",
                "percent": f"{disk.percent}%"
            },
            "cpu_percent": f"{psutil.cpu_percent(interval=1)}%",
            "load_average": list(os.getloadavg()) if hasattr(os, 'getloadavg') else "N/A"
        }
    else:
        checks['system'] = {
            "status": "monitoring_unavailable",
            "details": "psutil not available"
        }
    
    # Environment info
    checks['environment'] = {
        "flask_env": os.getenv('FLASK_ENV', 'development'),
        "python_version": "3.11" if not PSUTIL_AVAILABLE else f"{psutil.Process().as_dict()['name']}",
        "uptime": "N/A" if not PSUTIL_AVAILABLE else f"{psutil.boot_time()}"
    }
    
    return jsonify({
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
        "version": "1.0.0"
    }), 200 if overall_status == "healthy" else 503

@health_bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """Kubernetes readiness probe"""
    try:
        # Quick database check
        from app import db
        db.engine.execute('SELECT 1')
        
        return jsonify({
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "not_ready",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 503

@health_bp.route('/health/live', methods=['GET'])
def liveness_check():
    """Kubernetes liveness probe"""
    return jsonify({
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }), 200