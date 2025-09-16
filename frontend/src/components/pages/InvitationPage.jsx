import React from 'react';
import { useNavigate } from 'react-router-dom';

const InvitationPage = ({ user }) => {
    const navigate = useNavigate();

    const handleGetStarted = () => {
        navigate('/dashboard');
    };

    return (
        <div className="main-content" style={{
            minHeight: '80vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        }}>
            <div className="invitation-card" style={{
                background: 'white',
                borderRadius: '20px',
                padding: '3rem',
                boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
                maxWidth: '500px',
                width: '100%',
                textAlign: 'center'
            }}>
                <div className="welcome-icon mb-4">
                    <i className="fas fa-chart-line" style={{
                        fontSize: '4rem',
                        color: '#20c997',
                        marginBottom: '1rem'
                    }}></i>
                </div>
                
                <h1 className="mb-3" style={{
                    fontSize: '2.5rem',
                    fontWeight: 'bold',
                    color: '#2c3e50'
                }}>
                    Welcome to TradingGrow!
                </h1>
                
                <p className="mb-4" style={{
                    fontSize: '1.2rem',
                    color: '#6c757d',
                    lineHeight: '1.6'
                }}>
                    Hello <strong>{user?.username || user?.email}</strong>! 
                    Get ready to take your trading to the next level with our 
                    professional analytics platform.
                </p>
                
                <div className="features-preview mb-4">
                    <div className="row text-center">
                        <div className="col-4">
                            <div className="feature-item p-3">
                                <i className="fas fa-chart-bar mb-2" style={{
                                    fontSize: '2rem',
                                    color: '#20c997'
                                }}></i>
                                <p className="small mb-0">Advanced Charts</p>
                            </div>
                        </div>
                        <div className="col-4">
                            <div className="feature-item p-3">
                                <i className="fas fa-list mb-2" style={{
                                    fontSize: '2rem',
                                    color: '#20c997'
                                }}></i>
                                <p className="small mb-0">Smart Watchlists</p>
                            </div>
                        </div>
                        <div className="col-4">
                            <div className="feature-item p-3">
                                <i className="fas fa-brain mb-2" style={{
                                    fontSize: '2rem',
                                    color: '#20c997'
                                }}></i>
                                <p className="small mb-0">AI Insights</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                {user?.subscription_tier && (
                    <div className="subscription-badge mb-4">
                        <span className="badge" style={{
                            backgroundColor: user.subscription_tier === 'pro' ? '#28a745' : 
                                           user.subscription_tier === 'premium' ? '#6f42c1' : '#6c757d',
                            fontSize: '1rem',
                            padding: '0.5rem 1rem',
                            borderRadius: '20px',
                            color: 'white'
                        }}>
                            <i className="fas fa-crown me-2"></i>
                            {user.subscription_tier.toUpperCase()} Member
                        </span>
                    </div>
                )}
                
                <button 
                    onClick={handleGetStarted}
                    className="btn btn-lg"
                    style={{
                        backgroundColor: '#20c997',
                        borderColor: '#20c997',
                        color: 'white',
                        fontWeight: '600',
                        padding: '15px 40px',
                        borderRadius: '30px',
                        fontSize: '1.1rem',
                        transition: 'all 0.3s ease'
                    }}
                >
                    <i className="fas fa-rocket me-2"></i>
                    Get Started
                </button>
                
                <div className="mt-4">
                    <p className="small text-muted">
                        Ready to explore professional trading tools and analytics
                    </p>
                </div>
            </div>
        </div>
    );
};

export default InvitationPage;