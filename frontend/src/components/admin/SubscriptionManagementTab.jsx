import React, { useState } from 'react';

const SubscriptionManagementTab = ({ users, subscriptionRequests, onRefresh }) => {
    const [showUpgradeModal, setShowUpgradeModal] = useState(false);
    const [selectedUser, setSelectedUser] = useState(null);

    const handleSubscriptionRequest = async (requestId, action) => {
        try {
            const response = await fetch(`/admin/api/subscription-requests/${requestId}/${action}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                alert(`✅ ${data.message}`);
                onRefresh();
            } else {
                alert(`❌ ${data.error || 'Failed to process request'}`);
            }
        } catch (error) {
            console.error('Error processing subscription request:', error);
            alert('Error processing subscription request');
        }
    };

    const handleBulkUpgrade = async (fromTier, toTier) => {
        if (!confirm(`Upgrade all ${fromTier} users to ${toTier}?`)) return;

        try {
            const response = await fetch('/admin/api/bulk-upgrade', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ from_tier: fromTier, to_tier: toTier })
            });

            if (response.ok) {
                const data = await response.json();
                alert(`✅ Upgraded ${data.updated_count} users`);
                onRefresh();
            } else {
                alert('Failed to perform bulk upgrade');
            }
        } catch (error) {
            console.error('Error performing bulk upgrade:', error);
            alert('Error performing bulk upgrade');
        }
    };

    const handleManualUpgrade = async (userId, newTier) => {
        try {
            const response = await fetch(`/admin/api/users/${userId}/subscription`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ subscription_tier: newTier })
            });

            if (response.ok) {
                alert(`✅ User subscription changed to ${newTier}`);
                onRefresh();
            } else {
                alert('Failed to change subscription');
            }
        } catch (error) {
            console.error('Error changing subscription:', error);
            alert('Error changing subscription');
        }
    };

    // Calculate subscription statistics
    const stats = {
        free_users: users.filter(u => u.subscription_tier === 'free').length,
        medium_users: users.filter(u => u.subscription_tier === 'medium').length,
        pro_users: users.filter(u => u.subscription_tier === 'pro').length,
        total_revenue: users.reduce((sum, u) => {
            if (u.subscription_tier === 'medium') return sum + 19.99;
            if (u.subscription_tier === 'pro') return sum + 49.99;
            return sum;
        }, 0)
    };

    return (
        <div className="p-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h4><i className="fas fa-credit-card me-2"></i>Subscription Management</h4>
                <button 
                    className="btn btn-primary"
                    onClick={() => setShowUpgradeModal(true)}
                >
                    <i className="fas fa-arrow-up me-2"></i>Bulk Actions
                </button>
            </div>

            {/* Subscription Stats */}
            <div className="row mb-4">
                <div className="col-md-3">
                    <div className="card text-center">
                        <div className="card-body">
                            <h5 className="text-muted">{stats.free_users}</h5>
                            <p className="mb-0">Free Users</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card text-center">
                        <div className="card-body">
                            <h5 className="text-info">{stats.medium_users}</h5>
                            <p className="mb-0">Medium Users</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card text-center">
                        <div className="card-body">
                            <h5 className="text-success">{stats.pro_users}</h5>
                            <p className="mb-0">Pro Users</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card text-center">
                        <div className="card-body">
                            <h5 className="text-primary">${stats.total_revenue.toFixed(2)}</h5>
                            <p className="mb-0">Monthly Revenue</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Subscription Requests */}
            {subscriptionRequests.length > 0 && (
                <div className="card mb-4">
                    <div className="card-header">
                        <h5 className="mb-0">
                            <i className="fas fa-clock me-2"></i>
                            Pending Subscription Requests ({subscriptionRequests.length})
                        </h5>
                    </div>
                    <div className="card-body p-0">
                        <div className="table-responsive">
                            <table className="table table-hover mb-0">
                                <thead className="table-light">
                                    <tr>
                                        <th>User</th>
                                        <th>Current Plan</th>
                                        <th>Requested Plan</th>
                                        <th>Date</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {subscriptionRequests.map(request => (
                                        <tr key={request.id}>
                                            <td>
                                                <div>
                                                    <strong>{request.user_name}</strong>
                                                    <br />
                                                    <small className="text-muted">{request.user_email}</small>
                                                </div>
                                            </td>
                                            <td>
                                                <span className="badge bg-secondary">
                                                    {request.current_tier}
                                                </span>
                                            </td>
                                            <td>
                                                <span className="badge bg-primary">
                                                    {request.requested_tier}
                                                </span>
                                            </td>
                                            <td>{request.created_at}</td>
                                            <td>
                                                <div className="btn-group btn-group-sm">
                                                    <button 
                                                        className="btn btn-outline-success"
                                                        onClick={() => handleSubscriptionRequest(request.id, 'approve')}
                                                    >
                                                        <i className="fas fa-check"></i> Approve
                                                    </button>
                                                    <button 
                                                        className="btn btn-outline-danger"
                                                        onClick={() => handleSubscriptionRequest(request.id, 'reject')}
                                                    >
                                                        <i className="fas fa-times"></i> Reject
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}

            {/* Users by Subscription */}
            <div className="card">
                <div className="card-header">
                    <h5 className="mb-0">
                        <i className="fas fa-users me-2"></i>
                        All Users by Subscription
                    </h5>
                </div>
                <div className="card-body p-0">
                    <div className="table-responsive">
                        <table className="table table-hover mb-0">
                            <thead className="table-light">
                                <tr>
                                    <th>User</th>
                                    <th>Current Plan</th>
                                    <th>Member Since</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map(user => (
                                    <tr key={user.id}>
                                        <td>
                                            <div className="d-flex align-items-center">
                                                {user.is_admin && <i className="fas fa-shield text-warning me-2" title="Admin"></i>}
                                                <div>
                                                    <strong>{user.full_name}</strong>
                                                    <br />
                                                    <small className="text-muted">{user.email}</small>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <span className={`badge ${
                                                user.subscription_tier === 'pro' ? 'bg-success' :
                                                user.subscription_tier === 'medium' ? 'bg-info' : 'bg-secondary'
                                            }`}>
                                                {user.subscription_tier.toUpperCase()}
                                            </span>
                                        </td>
                                        <td>{new Date(user.created_at).toLocaleDateString()}</td>
                                        <td>
                                            <div className="btn-group btn-group-sm">
                                                <select 
                                                    className="form-select form-select-sm"
                                                    value={user.subscription_tier}
                                                    onChange={(e) => handleManualUpgrade(user.id, e.target.value)}
                                                    style={{width: '100px'}}
                                                >
                                                    <option value="free">Free</option>
                                                    <option value="medium">Medium</option>
                                                    <option value="pro">Pro</option>
                                                </select>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Bulk Actions Modal */}
            {showUpgradeModal && (
                <div className="modal show d-block" tabIndex="-1">
                    <div className="modal-dialog">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title">Bulk Subscription Actions</h5>
                                <button 
                                    type="button" 
                                    className="btn-close"
                                    onClick={() => setShowUpgradeModal(false)}
                                ></button>
                            </div>
                            <div className="modal-body">
                                <p>Perform bulk actions on user subscriptions:</p>
                                
                                <div className="d-grid gap-2">
                                    <button 
                                        className="btn btn-outline-success"
                                        onClick={() => handleBulkUpgrade('free', 'medium')}
                                    >
                                        Upgrade All Free → Medium
                                    </button>
                                    <button 
                                        className="btn btn-outline-success"
                                        onClick={() => handleBulkUpgrade('free', 'pro')}
                                    >
                                        Upgrade All Free → Pro
                                    </button>
                                    <button 
                                        className="btn btn-outline-success"
                                        onClick={() => handleBulkUpgrade('medium', 'pro')}
                                    >
                                        Upgrade All Medium → Pro
                                    </button>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button 
                                    type="button" 
                                    className="btn btn-secondary"
                                    onClick={() => setShowUpgradeModal(false)}
                                >
                                    Close
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SubscriptionManagementTab;