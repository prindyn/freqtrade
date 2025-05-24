<template>
    <Dialog 
        v-model:visible="modalVisible" 
        modal 
        header="Connect Your Bot" 
        :style="{ width: '500px' }"
        :closable="true"
        :draggable="false"
        class="connect-bot-modal"
        @hide="onModalHide"
    >
        <template #header>
            <div class="modal-header-content">
                <i class="pi pi-link mr-2 text-xl"></i>
                <span class="text-xl font-semibold">Connect Your Bot</span>
            </div>
        </template>
        
        <div class="modal-body">
            <p class="text-600 mb-4">Connect your trading bot running on your own server</p>
            
            <form @submit.prevent="connectBot" class="flex flex-column gap-3">
                <div class="flex flex-column gap-2">
                    <label for="botName" class="text-900 font-medium">Bot Name</label>
                    <InputText 
                        id="botName" 
                        v-model="botData.name" 
                        placeholder="My Trading Bot"
                        class="w-full"
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
                        class="w-full"
                        rows="2"
                    />
                </div>
                
                <div class="flex flex-column gap-2">
                    <label for="apiUrl" class="text-900 font-medium">Bot API URL</label>
                    <InputText 
                        id="apiUrl" 
                        v-model="botData.api_url" 
                        placeholder="http://192.168.1.100:8080"
                        class="w-full"
                        :class="{ 'p-invalid': errors.api_url }"
                    />
                    <small v-if="errors.api_url" class="p-error">{{ errors.api_url }}</small>
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
                        :class="{ 'p-invalid': errors.api_token }"
                    />
                    <small v-if="errors.api_token" class="p-error">{{ errors.api_token }}</small>
                </div>
                
                <!-- Basic Authentication Fields -->
                <div v-if="botData.auth_method === 'basic'" class="flex flex-column gap-3">
                    <div class="flex flex-column gap-2">
                        <label for="username" class="text-900 font-medium">Username</label>
                        <InputText 
                            id="username" 
                            v-model="botData.username" 
                            placeholder="Bot username"
                            class="w-full"
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
                    class="w-full mt-2"
                    severity="secondary"
                    @click="testConnection"
                />
                
                <!-- Connection Status -->
                <div v-if="connectionStatus" class="connection-status p-3 border-round">
                    <div v-if="connectionStatus.success" class="flex align-items-center text-green-600">
                        <i class="pi pi-check-circle mr-2"></i>
                        <span>{{ connectionStatus.message }}</span>
                    </div>
                    <div v-else class="flex align-items-center text-red-600">
                        <i class="pi pi-times-circle mr-2"></i>
                        <span>{{ connectionStatus.message }}</span>
                    </div>
                </div>
                
                <!-- Error Message -->
                <Message 
                    v-if="error" 
                    severity="error" 
                    :closable="true" 
                    @close="error = null"
                    class="mt-2"
                >
                    {{ error }}
                </Message>
            </form>
        </div>
        
        <template #footer>
            <div class="flex justify-content-end gap-2">
                <Button 
                    label="Cancel" 
                    icon="pi pi-times" 
                    @click="closeModal"
                    severity="secondary"
                    outlined
                />
                <Button 
                    label="Connect Bot" 
                    icon="pi pi-link" 
                    :loading="connecting"
                    :disabled="!connectionStatus?.success"
                    @click="connectBot"
                />
            </div>
        </template>
    </Dialog>
</template>

<script>
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Message from 'primevue/message';
import RadioButton from 'primevue/radiobutton';
import api from '@/services/api';

export default {
    name: 'ConnectBotModal',
    components: {
        Dialog,
        InputText,
        Textarea,
        Password,
        Button,
        Message,
        RadioButton
    },
    emits: ['update:visible', 'bot-connected'],
    props: {
        visible: {
            type: Boolean,
            default: false
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
            error: null
        };
    },
    computed: {
        modalVisible: {
            get() {
                return this.visible;
            },
            set(value) {
                this.$emit('update:visible', value);
            }
        }
    },
    created() {
        // Ensure authentication token is set
        const token = localStorage.getItem('authToken');
        if (token) {
            api.setAuthHeader(token);
        }
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
                this.errors.api_url = 'Please enter a valid URL';
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
                
                // Emit success event to parent
                this.$emit('bot-connected', {
                    name: this.botData.name,
                    id: response.data.id
                });
                
                // Reset form
                this.resetForm();
                
            } catch (error) {
                console.error('Bot connection failed:', error);
                this.error = error.response?.data?.detail || 'Failed to connect bot';
            } finally {
                this.connecting = false;
            }
        },
        
        closeModal() {
            this.modalVisible = false;
        },
        
        onModalHide() {
            this.resetForm();
        },
        
        resetForm() {
            this.botData = {
                name: '',
                description: '',
                api_url: '',
                auth_method: 'token',
                api_token: '',
                username: '',
                password: ''
            };
            this.errors = {};
            this.connectionStatus = null;
            this.error = null;
            this.testingConnection = false;
            this.connecting = false;
        }
    }
};
</script>

<style scoped>
.connect-bot-modal :deep(.p-dialog-header) {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white;
    border-radius: 6px 6px 0 0;
}

.connect-bot-modal :deep(.p-dialog-title) {
    color: white;
}

.connect-bot-modal :deep(.p-dialog-header-icon) {
    color: white;
}

.connect-bot-modal :deep(.p-dialog-header-icon:hover) {
    background-color: rgba(255, 255, 255, 0.1);
}

.modal-header-content {
    display: flex;
    align-items: center;
}

.modal-body {
    padding: 0;
}

.connection-status {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
}

.mr-2 {
    margin-right: 0.5rem;
}

.ml-2 {
    margin-left: 0.5rem;
}

:deep(.p-inputtext),
:deep(.p-password-input),
:deep(.p-inputtextarea) {
    transition: all 0.3s ease;
    border: 2px solid #e9ecef;
}

:deep(.p-inputtext:focus),
:deep(.p-password-input:focus),
:deep(.p-inputtextarea:focus) {
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

:deep(.p-invalid) {
    border-color: #e74c3c !important;
}

:deep(.p-button) {
    transition: all 0.3s ease;
}

:deep(.p-button:hover) {
    transform: translateY(-1px);
}
</style>