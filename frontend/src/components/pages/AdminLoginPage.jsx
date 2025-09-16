import React, { useState } from 'react';

const AdminLoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            // Try mock admin login first
            const mockResponse = await fetch('/api/mock/admin/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            if (mockResponse.ok) {
                const data = await mockResponse.json();
                if (data.success) {
                    window.location.href = '/admin/dashboard';
                    return;
                }
            }

            // Fallback to regular admin login
            const response = await fetch('/admin/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (data.success) {
                window.location.href = data.redirect || '/admin/dashboard';
            } else {
                setError(data.error || 'Login failed');
            }
        } catch (error) {
            console.error('Admin login error:', error);
            setError('An error occurred. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-md-6 col-lg-5">
                        <div className="card shadow-sm">
                            <div className="card-body p-5">
                                <div className="text-center mb-4">
                                    <h2 className="fw-bold text-primary mb-3">
                                        <i className="fas fa-shield-alt me-2"></i>
                                        Admin Portal
                                    </h2>
                                    <p className="text-muted">
                                        Access the TradingGrow admin dashboard
                                    </p>
                                </div>

                                {error && (
                                    <div className="alert alert-danger" role="alert">
                                        <i className="fas fa-exclamation-triangle me-2"></i>
                                        {error}
                                    </div>
                                )}

                                {/* Demo Credentials Info */}
                                <div className="alert alert-info mb-4">
                                    <small>
                                        <strong>Demo Credentials:</strong><br />
                                        Email: admin@tradinggrow.com<br />
                                        Password: admin123
                                    </small>
                                </div>

                                <form onSubmit={handleSubmit}>
                                    <div className="mb-3">
                                        <label htmlFor="email" className="form-label">
                                            <i className="fas fa-envelope me-2"></i>Admin Email
                                        </label>
                                        <input
                                            type="email"
                                            className="form-control"
                                            id="email"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            required
                                            placeholder="admin@tradinggrow.com"
                                            disabled={isLoading}
                                        />
                                    </div>

                                    <div className="mb-4">
                                        <label htmlFor="password" className="form-label">
                                            <i className="fas fa-lock me-2"></i>Password
                                        </label>
                                        <input
                                            type="password"
                                            className="form-control"
                                            id="password"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            required
                                            placeholder="Enter admin password"
                                            disabled={isLoading}
                                        />
                                    </div>

                                    <button
                                        type="submit"
                                        className="btn btn-primary w-100 py-2"
                                        disabled={isLoading}
                                    >
                                        {isLoading ? (
                                            <>
                                                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                                Signing In...
                                            </>
                                        ) : (
                                            <>
                                                <i className="fas fa-sign-in-alt me-2"></i>
                                                Sign In to Admin Portal
                                            </>
                                        )}
                                    </button>
                                </form>

                                <div className="text-center mt-4">
                                    <div className="border-top pt-3">
                                        <small className="text-muted">
                                            <i className="fas fa-users me-1"></i>
                                            <a href="/" className="text-decoration-none">
                                                Back to User Portal
                                            </a>
                                        </small>
                                    </div>
                                </div>

                                {/* Admin Features Preview */}
                                <div className="mt-4">
                                    <small className="text-muted">
                                        <strong>Admin Features:</strong>
                                    </small>
                                    <div className="row text-center mt-2">
                                        <div className="col-4">
                                            <small className="text-muted">
                                                <i className="fas fa-users d-block mb-1"></i>
                                                User Management
                                            </small>
                                        </div>
                                        <div className="col-4">
                                            <small className="text-muted">
                                                <i className="fas fa-credit-card d-block mb-1"></i>
                                                Subscriptions
                                            </small>
                                        </div>
                                        <div className="col-4">
                                            <small className="text-muted">
                                                <i className="fas fa-chart-line d-block mb-1"></i>
                                                Stock Control
                                            </small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminLoginPage;