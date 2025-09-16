import React, { useState } from 'react';

const UserManagementTab = ({ users, onRefresh }) => {
    const [selectedUser, setSelectedUser] = useState(null);
    const [editingUser, setEditingUser] = useState(null);
    const [showAddModal, setShowAddModal] = useState(false);

    const handleEditUser = (user) => {
        setEditingUser({ ...user });
    };

    const handleSaveUser = async () => {
        try {
            const response = await fetch(`/admin/api/users/${editingUser.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(editingUser)
            });

            if (response.ok) {
                setEditingUser(null);
                onRefresh();
                alert('User updated successfully!');
            } else {
                alert('Failed to update user');
            }
        } catch (error) {
            console.error('Error updating user:', error);
            alert('Error updating user');
        }
    };

    const handleDeleteUser = async (userId) => {
        if (!confirm('Are you sure you want to delete this user?')) return;

        try {
            const response = await fetch(`/admin/api/users/${userId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                onRefresh();
                alert('User deleted successfully!');
            } else {
                alert('Failed to delete user');
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            alert('Error deleting user');
        }
    };

    const handleSubscriptionChange = async (userId, newTier) => {
        try {
            const response = await fetch(`/admin/api/users/${userId}/subscription`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ subscription_tier: newTier })
            });

            if (response.ok) {
                onRefresh();
                alert(`Subscription changed to ${newTier}!`);
            } else {
                alert('Failed to change subscription');
            }
        } catch (error) {
            console.error('Error changing subscription:', error);
            alert('Error changing subscription');
        }
    };

    return (
        <div className="p-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h4><i className="fas fa-users me-2"></i>User Management</h4>
                <button 
                    className="btn btn-primary"
                    onClick={() => setShowAddModal(true)}
                >
                    <i className="fas fa-plus me-2"></i>Add User
                </button>
            </div>

            {/* Users Table */}
            <div className="table-responsive">
                <table className="table table-hover">
                    <thead className="table-light">
                        <tr>
                            <th>Email</th>
                            <th>Name</th>
                            <th>Subscription</th>
                            <th>Status</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map(user => (
                            <tr key={user.id}>
                                <td>
                                    <div className="d-flex align-items-center">
                                        {user.is_admin && <i className="fas fa-shield text-warning me-2" title="Admin"></i>}
                                        {user.email}
                                    </div>
                                </td>
                                <td>{user.full_name}</td>
                                <td>
                                    <select 
                                        className="form-select form-select-sm"
                                        value={user.subscription_tier}
                                        onChange={(e) => handleSubscriptionChange(user.id, e.target.value)}
                                    >
                                        <option value="free">Free</option>
                                        <option value="medium">Medium</option>
                                        <option value="pro">Pro</option>
                                    </select>
                                </td>
                                <td>
                                    <span className={`badge ${user.is_admin ? 'bg-warning' : 'bg-success'}`}>
                                        {user.is_admin ? 'Admin' : 'Active'}
                                    </span>
                                </td>
                                <td>{new Date(user.created_at).toLocaleDateString()}</td>
                                <td>
                                    <div className="btn-group btn-group-sm">
                                        <button 
                                            className="btn btn-outline-primary"
                                            onClick={() => handleEditUser(user)}
                                        >
                                            <i className="fas fa-edit"></i>
                                        </button>
                                        <button 
                                            className="btn btn-outline-danger"
                                            onClick={() => handleDeleteUser(user.id)}
                                            disabled={user.is_admin}
                                        >
                                            <i className="fas fa-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {users.length === 0 && (
                <div className="text-center py-5">
                    <i className="fas fa-users fa-3x text-muted mb-3"></i>
                    <h5 className="text-muted">No users found</h5>
                    <p className="text-muted">Users will appear here once registered</p>
                </div>
            )}

            {/* Edit User Modal */}
            {editingUser && (
                <div className="modal show d-block" tabIndex="-1">
                    <div className="modal-dialog">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title">Edit User</h5>
                                <button 
                                    type="button" 
                                    className="btn-close"
                                    onClick={() => setEditingUser(null)}
                                ></button>
                            </div>
                            <div className="modal-body">
                                <div className="mb-3">
                                    <label className="form-label">Email</label>
                                    <input 
                                        type="email" 
                                        className="form-control"
                                        value={editingUser.email}
                                        onChange={(e) => setEditingUser({...editingUser, email: e.target.value})}
                                    />
                                </div>
                                <div className="mb-3">
                                    <label className="form-label">Full Name</label>
                                    <input 
                                        type="text" 
                                        className="form-control"
                                        value={editingUser.full_name}
                                        onChange={(e) => setEditingUser({...editingUser, full_name: e.target.value})}
                                    />
                                </div>
                                <div className="mb-3">
                                    <label className="form-label">Subscription Tier</label>
                                    <select 
                                        className="form-select"
                                        value={editingUser.subscription_tier}
                                        onChange={(e) => setEditingUser({...editingUser, subscription_tier: e.target.value})}
                                    >
                                        <option value="free">Free</option>
                                        <option value="medium">Medium</option>
                                        <option value="pro">Pro</option>
                                    </select>
                                </div>
                                <div className="mb-3">
                                    <div className="form-check">
                                        <input 
                                            className="form-check-input" 
                                            type="checkbox"
                                            checked={editingUser.is_admin}
                                            onChange={(e) => setEditingUser({...editingUser, is_admin: e.target.checked})}
                                        />
                                        <label className="form-check-label">
                                            Admin User
                                        </label>
                                    </div>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button 
                                    type="button" 
                                    className="btn btn-secondary"
                                    onClick={() => setEditingUser(null)}
                                >
                                    Cancel
                                </button>
                                <button 
                                    type="button" 
                                    className="btn btn-primary"
                                    onClick={handleSaveUser}
                                >
                                    Save Changes
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default UserManagementTab;