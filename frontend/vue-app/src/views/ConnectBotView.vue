<template>
    <div class="connect-bot-container min-h-screen flex align-items-center justify-content-center px-3">
        <div class="connect-bot-card p-6 border-round-xl shadow-8 w-full max-w-35rem">
            <div class="text-center mb-6">
                <div class="text-900 text-3xl font-medium mb-2">Connect Your Bot</div>
                <div class="text-600 font-medium">Connect your trading bot running on your own server</div>
            </div>
            
            <form @submit.prevent="connectBot" class="flex flex-column gap-4">
                <div class="flex flex-column gap-2">
                    <label for="botName" class="text-900 font-medium">Bot Name</label>
                    <InputText 
                        id="botName" 
                        v-model="botData.name" 
                        placeholder="My Trading Bot"
                        class="w-full p-3 border-round-lg"
                        :class="{ 'p-invalid': errors.name }"
                    />
                    <small v-if="errors.name" class="p-error">{{ errors.name }}</small>
                </div>
                
                <div class="flex flex-column gap-2">
                    <label for="description" class="text-900 font-medium">Description <span class="text-500">(Optional)</span></label>
                    <Textarea 
                        id="description" 
                        v-model="botData.description" 
                        placeholder="Describe your bot's strategy..."
                        class="w-full p-3 border-round-lg"
                        rows="3"
                    />
                </div>
                
                <div class="flex flex-column gap-2">
                    <label for="apiUrl" class="text-900 font-medium">Bot API URL</label>
                    <InputText 
                        id="apiUrl" 
                        v-model="botData.api_url" 
                        placeholder="http://192.168.1.100:8080"
                        class="w-full p-3 border-round-lg"
                        :class="{ 'p-invalid': errors.api_url }"
                    />
                    <small v-if="errors.api_url" class="p-error">{{ errors.api_url }}</small>
                    <small class="text-600">The URL where your trading bot's REST API is accessible</small>
                </div>
                
                <!-- Authentication Method Selection -->
                <div class="flex flex-column gap-2">
                    <label class="text-900 font-medium">Authentication Method</label>
                    <div class="flex gap-4">
                        <div class="flex align-items-center">
                            <RadioButton 
                                id="auth_token" 
                                v-model="botData.auth_method" 
                                value="token" 
                                name="auth_method"
                            />
                            <label for="auth_token" class="ml-2">API Token</label>
                        </div>
                        <div class="flex align-items-center">
                            <RadioButton 
                                id="auth_basic" 
                                v-model="botData.auth_method" 
                                value="basic" 
                                name="auth_method"
                            />
                            <label for="auth_basic" class="ml-2">Username & Password</label>
                        </div>
                    </div>
                </div>
                
                <!-- Token Authentication Fields -->
                <div v-if="botData.auth_method === 'token'" class="flex flex-column gap-2">
                    <label for="apiToken" class="text-900 font-medium">API Token</label>
                    <Password 
                        id="apiToken" 
                        v-model="botData.api_token" 
                        placeholder="Your bot's API token"
                        :feedback="false"
                        :toggleMask="true"
                        class="w-full"
                        inputClass="p-3 border-round-lg w-full"
                        :class="{ 'p-invalid': errors.api_token }"
                    />
                    <small v-if="errors.api_token" class="p-error">{{ errors.api_token }}</small>
                    <small class="text-600">Found in your trading bot's configuration file</small>
                </div>
                
                <!-- Basic Authentication Fields -->
                <div v-if="botData.auth_method === 'basic'" class="flex flex-column gap-4">
                    <div class="flex flex-column gap-2">
                        <label for="username" class="text-900 font-medium">Username</label>
                        <InputText 
                            id="username" 
                            v-model="botData.username" 
                            placeholder="Bot username"
                            class="w-full p-3 border-round-lg"
                            :class="{ 'p-invalid': errors.username }"
                        />
                        <small v-if="errors.username" class="p-error">{{ errors.username }}</small>
                    </div>
                    
                    <div class="flex flex-column gap-2">
                        <label for="password" class="text-900 font-medium">Password</label>
                        <Password 
                            id="password" 
                            v-model="botData.password" 
                            placeholder="Bot password"
                            :feedback="false"
                            :toggleMask="true"
                            class="w-full"
                            inputClass="p-3 border-round-lg w-full"
                            :class="{ 'p-invalid': errors.password }"
                        />
                        <small v-if="errors.password" class="p-error">{{ errors.password }}</small>
                    </div>
                </div>
                
                <!-- Test Connection Button -->
                <Button 
                    type="button"
                    label="Test Connection" 
                    icon="pi pi-wifi" 
                    :loading="testingConnection"
                    class="w-full p-3 text-lg border-round-lg mt-2 test-connection-button"
                    severity="secondary"
                    @click="testConnection"
                />
                
                <!-- Connection Status -->
                <div v-if="connectionStatus" class="connection-status p-3 border-round-lg">
                    <div v-if="connectionStatus.success" class="flex align-items-center text-green-600">
                        <i class="pi pi-check-circle mr-2"></i>
                        <span>{{ connectionStatus.message }}</span>
                    </div>
                    <div v-else class="flex align-items-center text-red-600">
                        <i class="pi pi-times-circle mr-2"></i>
                        <span>{{ connectionStatus.message }}</span>
                    </div>
                </div>
                
                <!-- Connect Button -->
                <Button 
                    type="submit" 
                    label="Connect Bot" 
                    icon="pi pi-link" 
                    :loading="connecting"
                    :disabled="!connectionStatus?.success"
                    class="w-full p-3 text-xl border-round-lg mt-2 connect-button"
                />
            </form>
            
            <!-- Error Messages -->
            <Message 
                v-if="error" 
                severity="error" 
                :closable="true" 
                @close="error = null"
                class="mt-4"
            >
                {{ error }}
            </Message>
            
            <!-- Success Message -->
            <Message 
                v-if="successMessage" 
                severity="success" 
                :closable="true" 
                @close="successMessage = null"
                class="mt-4"
            >
                {{ successMessage }}
            </Message>
            
            <!-- Help Section -->
            <div class="help-section mt-6 pt-4 border-top-1 surface-border">
                <h4 class="text-lg font-medium text-900 mb-3">Need Help?</h4>
                <div class="text-600 line-height-3">
                    <p class="mb-2"><strong>API URL:</strong> The address where your trading bot is running (e.g., http://192.168.1.100:8080)</p>
                    <div v-if="botData.auth_method === 'token'">
                        <p class="mb-2"><strong>API Token:</strong> Enable REST API in your bot's config and use the jwt_secret_key value</p>
                    </div>
                    <div v-if="botData.auth_method === 'basic'">
                        <p class="mb-2"><strong>Username/Password:</strong> Use the credentials configured for your bot's REST API</p>
                    </div>
                    <p class="mb-0"><strong>Firewall:</strong> Make sure the bot's port is accessible from this platform</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Message from 'primevue/message';
import RadioButton from 'primevue/radiobutton';
import api from '@/services/api';

export default {
    name: 'ConnectBotView',
    components: {
        InputText,
        Textarea,
        Password,
        Button,
        Message,
        RadioButton
    },
    created() {
        // Ensure authentication token is set
        const token = localStorage.getItem('authToken');
        if (token) {
            api.setAuthHeader(token);
        } else {
            // Redirect to login if no token
            this.$router.push({ name: 'login' });
        }
    },
    data() {
        return {
            botData: {
                name: '',
                description: '',
                api_url: '',
                auth_method: 'token',
                api_token: '',
                username: '',
                password: ''
            },
            errors: {},
            testingConnection: false,
            connecting: false,
            connectionStatus: null,
            error: null,
            successMessage: null
        };
    },
    methods: {
        validateForm() {
            this.errors = {};
            
            if (!this.botData.name.trim()) {
                this.errors.name = 'Bot name is required';
            }
            
            if (!this.botData.api_url.trim()) {
                this.errors.api_url = 'API URL is required';
            } else if (!this.isValidUrl(this.botData.api_url)) {
                this.errors.api_url = 'Please enter a valid URL (e.g., http://192.168.1.100:8080)';
            }
            
            // Validate authentication fields based on method
            if (this.botData.auth_method === 'token') {
                if (!this.botData.api_token.trim()) {
                    this.errors.api_token = 'API token is required';
                }
            } else if (this.botData.auth_method === 'basic') {
                if (!this.botData.username.trim()) {
                    this.errors.username = 'Username is required';
                }
                if (!this.botData.password.trim()) {
                    this.errors.password = 'Password is required';
                }
            }
            
            return Object.keys(this.errors).length === 0;
        },
        
        isValidUrl(string) {
            try {
                new URL(string);
                return true;
            } catch (_) {
                return false;
            }
        },
        
        async testConnection() {
            if (!this.validateForm()) {
                return;
            }
            
            this.testingConnection = true;
            this.connectionStatus = null;
            this.error = null;
            
            try {
                const connectionData = {
                    api_url: this.botData.api_url,
                    auth_method: this.botData.auth_method
                };
                
                if (this.botData.auth_method === 'token') {
                    connectionData.api_token = this.botData.api_token;
                } else {
                    connectionData.username = this.botData.username;
                    connectionData.password = this.botData.password;
                }
                
                const response = await api.testBotConnection(connectionData);
                
                this.connectionStatus = {
                    success: response.data.success,
                    message: response.data.message
                };
                
            } catch (error) {
                console.error('Connection test failed:', error);
                this.connectionStatus = {
                    success: false,
                    message: error.response?.data?.detail || 'Connection test failed'
                };
            } finally {
                this.testingConnection = false;
            }
        },
        
        async connectBot() {
            if (!this.validateForm()) {
                return;
            }
            
            if (!this.connectionStatus?.success) {
                this.error = 'Please test the connection first';
                return;
            }
            
            this.connecting = true;
            this.error = null;
            
            try {
                // Prepare data based on auth method
                const connectData = {
                    name: this.botData.name,
                    description: this.botData.description,
                    api_url: this.botData.api_url,
                    auth_method: this.botData.auth_method
                };
                
                if (this.botData.auth_method === 'token') {
                    connectData.api_token = this.botData.api_token;
                } else {
                    connectData.username = this.botData.username;
                    connectData.password = this.botData.password;
                }
                
                const response = await api.connectExternalBot(connectData);
                
                this.successMessage = `Successfully connected ${this.botData.name}!`;
                
                // Redirect to dashboard after 2 seconds
                setTimeout(() => {
                    this.$router.push({ name: 'dashboard' });
                }, 2000);
                
            } catch (error) {
                console.error('Bot connection failed:', error);
                this.error = error.response?.data?.detail || 'Failed to connect bot';
            } finally {
                this.connecting = false;
            }
        }
    }
};
</script>

<style scoped>
.connect-bot-container {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100vw;
    height: 100vh;
    overflow: auto;
}

.connect-bot-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.test-connection-button {
    background: #6c757d;
    border-color: #6c757d;
}

.test-connection-button:hover {
    background: #5a6268;
    border-color: #545b62;
}

.connect-button {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    border: none;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.connect-button:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(30, 60, 114, 0.4);
}

.connection-status {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
}

.help-section {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1rem;
}

:deep(.p-inputtext),
:deep(.p-password-input),
:deep(.p-inputtextarea) {
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    border: 2px solid rgba(42, 82, 152, 0.1);
    background: rgba(255, 255, 255, 0.8);
}

:deep(.p-inputtext:focus),
:deep(.p-password-input:focus),
:deep(.p-inputtextarea:focus) {
    border-color: #2a5298;
    box-shadow: 0 0 0 3px rgba(42, 82, 152, 0.1);
    transform: translateY(-1px);
}

:deep(.p-invalid) {
    border-color: #e74c3c !important;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 768px) {
    .connect-bot-card {
        margin: 1rem;
        padding: 1.5rem;
    }
}
</style>