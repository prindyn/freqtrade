<template>
    <div class="settings-container">
        <div class="settings-header">
            <h1 class="page-title">Settings</h1>
            <p class="page-subtitle">Configure your TradeWise experience</p>
        </div>
        
        <div class="settings-content">
            <!-- Notifications Settings -->
            <div class="settings-card">
                <div class="card-header">
                    <h2><i class="pi pi-bell mr-2"></i>Notifications</h2>
                </div>
                <div class="card-body">
                    <div class="setting-item">
                        <div class="setting-info">
                            <h3>Email Notifications</h3>
                            <p>Receive important updates via email</p>
                        </div>
                        <div class="setting-control">
                            <input type="checkbox" id="emailNotifications" v-model="settings.emailNotifications" class="toggle-switch">
                            <label for="emailNotifications" class="toggle-label"></label>
                        </div>
                    </div>
                    
                    <div class="setting-item">
                        <div class="setting-info">
                            <h3>Trade Alerts</h3>
                            <p>Get notified when trades are executed</p>
                        </div>
                        <div class="setting-control">
                            <input type="checkbox" id="tradeAlerts" v-model="settings.tradeAlerts" class="toggle-switch">
                            <label for="tradeAlerts" class="toggle-label"></label>
                        </div>
                    </div>
                    
                    <div class="setting-item">
                        <div class="setting-info">
                            <h3>Bot Status Updates</h3>
                            <p>Notifications when bots start/stop</p>
                        </div>
                        <div class="setting-control">
                            <input type="checkbox" id="botStatusUpdates" v-model="settings.botStatusUpdates" class="toggle-switch">
                            <label for="botStatusUpdates" class="toggle-label"></label>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Security Settings -->
            <div class="settings-card">
                <div class="card-header">
                    <h2><i class="pi pi-shield mr-2"></i>Security</h2>
                </div>
                <div class="card-body">
                    <div class="setting-item">
                        <div class="setting-info">
                            <h3>Two-Factor Authentication</h3>
                            <p>Add an extra layer of security to your account</p>
                        </div>
                        <div class="setting-control">
                            <button class="btn btn-primary">Enable 2FA</button>
                        </div>
                    </div>
                    
                    <div class="setting-item">
                        <div class="setting-info">
                            <h3>Session Timeout</h3>
                            <p>Automatically log out after inactivity</p>
                        </div>
                        <div class="setting-control">
                            <select v-model="settings.sessionTimeout" class="select-input">
                                <option value="30">30 minutes</option>
                                <option value="60">1 hour</option>
                                <option value="240">4 hours</option>
                                <option value="480">8 hours</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Trading Preferences -->
            <div class="settings-card">
                <div class="card-header">
                    <h2><i class="pi pi-chart-line mr-2"></i>Trading Preferences</h2>
                </div>
                <div class="card-body">
                    <div class="setting-item">
                        <div class="setting-info">
                            <h3>Default Currency</h3>
                            <p>Your preferred base currency for displays</p>
                        </div>
                        <div class="setting-control">
                            <select v-model="settings.defaultCurrency" class="select-input">
                                <option value="USD">USD</option>
                                <option value="EUR">EUR</option>
                                <option value="BTC">BTC</option>
                                <option value="ETH">ETH</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="setting-item">
                        <div class="setting-info">
                            <h3>Risk Level Display</h3>
                            <p>Show risk indicators on strategies</p>
                        </div>
                        <div class="setting-control">
                            <input type="checkbox" id="riskDisplay" v-model="settings.riskDisplay" class="toggle-switch">
                            <label for="riskDisplay" class="toggle-label"></label>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Save Button -->
            <div class="settings-actions">
                <button @click="saveSettings" class="btn btn-primary btn-large" :disabled="saving">
                    <i class="pi pi-save mr-2"></i>
                    {{ saving ? 'Saving...' : 'Save Settings' }}
                </button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'SettingsView',
    data() {
        return {
            saving: false,
            settings: {
                emailNotifications: true,
                tradeAlerts: true,
                botStatusUpdates: false,
                sessionTimeout: '60',
                defaultCurrency: 'USD',
                riskDisplay: true
            }
        }
    },
    methods: {
        async saveSettings() {
            this.saving = true;
            
            // Simulate API call
            setTimeout(() => {
                this.saving = false;
                this.$toast.add({
                    severity: 'success',
                    summary: 'Settings Saved',
                    detail: 'Your preferences have been updated successfully',
                    life: 3000
                });
            }, 1000);
        }
    }
}
</script>

<style scoped>
.settings-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem;
}

.settings-header {
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

.settings-content {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.settings-card {
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
    font-size: 1.3rem;
    display: flex;
    align-items: center;
}

.mr-2 {
    margin-right: 0.5rem;
}

.card-body {
    padding: 2rem;
}

.setting-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 0;
    border-bottom: 1px solid #ecf0f1;
}

.setting-item:last-child {
    border-bottom: none;
}

.setting-info h3 {
    margin: 0 0 0.5rem 0;
    color: #2c3e50;
    font-size: 1.1rem;
}

.setting-info p {
    margin: 0;
    color: #7f8c8d;
    font-size: 0.9rem;
}

.setting-control {
    flex-shrink: 0;
}

/* Toggle Switch Styles */
.toggle-switch {
    display: none;
}

.toggle-label {
    display: block;
    width: 50px;
    height: 26px;
    background: #bdc3c7;
    border-radius: 13px;
    cursor: pointer;
    position: relative;
    transition: background 0.3s ease;
}

.toggle-label::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 22px;
    height: 22px;
    background: white;
    border-radius: 50%;
    transition: transform 0.3s ease;
}

.toggle-switch:checked + .toggle-label {
    background: #3498db;
}

.toggle-switch:checked + .toggle-label::after {
    transform: translateX(24px);
}

/* Select Input Styles */
.select-input {
    padding: 0.5rem 1rem;
    border: 2px solid #ecf0f1;
    border-radius: 6px;
    background: white;
    color: #2c3e50;
    font-size: 0.9rem;
    cursor: pointer;
    transition: border-color 0.3s ease;
}

.select-input:focus {
    outline: none;
    border-color: #3498db;
}

/* Button Styles */
.btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
}

.btn-primary {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white;
}

.btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
}

.btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.btn-large {
    padding: 1rem 2rem;
    font-size: 1.1rem;
}

.settings-actions {
    text-align: center;
    margin-top: 2rem;
}

@media (max-width: 768px) {
    .settings-container {
        padding: 1rem;
    }
    
    .setting-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .setting-control {
        align-self: flex-end;
    }
}
</style>