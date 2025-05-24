<template>
    <div class="profile-container">
        <div class="profile-header">
            <h1 class="page-title">User Profile</h1>
            <p class="page-subtitle">Manage your account information and preferences</p>
        </div>
        
        <div class="profile-content">
            <div class="profile-card">
                <div class="card-header">
                    <h2>Account Information</h2>
                </div>
                <div class="card-body">
                    <div class="info-grid">
                        <div class="info-item">
                            <label>Email</label>
                            <span>user@example.com</span>
                        </div>
                        <div class="info-item">
                            <label>Member Since</label>
                            <span>January 2024</span>
                        </div>
                        <div class="info-item">
                            <label>Plan</label>
                            <span>Pro</span>
                        </div>
                        <div class="info-item">
                            <label>Active Bots</label>
                            <span>3</span>
                        </div>
                    </div>
                    
                    <div class="actions">
                        <button class="btn btn-primary">Edit Profile</button>
                        <button class="btn btn-secondary">Change Password</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'ProfileView',
    data() {
        return {
            user: {
                email: 'user@example.com',
                memberSince: 'January 2024',
                plan: 'Pro',
                activeBots: 3
            }
        }
    }
}
</script>

<style scoped>
.profile-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
}

.profile-header {
    text-align: center;
    margin-bottom: 3rem;
}

.page-title {
    font-size: 2.5rem;
    color: #2c3e50;
    margin-bottom: 0.5rem;
}

.page-subtitle {
    color: #7f8c8d;
    font-size: 1.1rem;
}

.profile-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.card-header {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white;
    padding: 1.5rem;
}

.card-header h2 {
    margin: 0;
    font-size: 1.5rem;
}

.card-body {
    padding: 2rem;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.info-item {
    display: flex;
    flex-direction: column;
}

.info-item label {
    font-weight: 600;
    color: #7f8c8d;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.info-item span {
    color: #2c3e50;
    font-size: 1.1rem;
    font-weight: 500;
}

.actions {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

.btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-primary {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
}

.btn-secondary {
    background: #95a5a6;
    color: white;
}

.btn-secondary:hover {
    background: #7f8c8d;
    transform: translateY(-2px);
}

@media (max-width: 768px) {
    .profile-container {
        padding: 1rem;
    }
    
    .info-grid {
        grid-template-columns: 1fr;
    }
    
    .actions {
        flex-direction: column;
    }
    
    .btn {
        width: 100%;
        text-align: center;
    }
}
</style>