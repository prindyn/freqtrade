<template>
    <Dialog v-model:visible="modalVisible" modal header="Connect Your Bot"
        :style="{ width: '900px', maxWidth: '95vw', maxHeight: '90vh' }" :closable="true" :draggable="false"
        class="connect-bot-modal" @hide="onModalHide">
        <template #header>
            <div class="modal-header-content">
                <i class="pi pi-link mr-2 text-xl"></i>
                <span class="text-xl font-semibold">Connect Your Bot</span>
            </div>
        </template>

        <div class="modal-body">
            <div class="modal-intro mb-3">
                <p class="text-600 mb-2">Connect your trading bot running on your own server</p>
                <div class="info-card p-2 border-round">
                    <div class="flex align-items-center">
                        <i class="pi pi-info-circle text-blue-500 mr-2"></i>
                        <span class="text-sm text-600">Make sure your bot is running and accessible from this
                            network</span>
                    </div>
                </div>
            </div>

            <form @submit.prevent="connectBot" class="grid gap-3">
                <!-- Basic Information Row -->
                <div class="col-12">
                    <h3 class="text-base font-semibold mb-2 text-900">Basic Information</h3>
                    <div class="grid gap-2">
                        <div class="col-12 md:col-4">
                            <div class="flex flex-column gap-1">
                                <label for="botName" class="text-900 font-medium text-sm">Bot Name</label>
                                <InputText id="botName" v-model="botData.name" placeholder="My Trading Bot"
                                    class="w-full" :class="{ 'p-invalid': errors.name }" />
                                <small v-if="errors.name" class="p-error">{{ errors.name }}</small>
                            </div>
                        </div>

                        <div class="col-12 md:col-4">
                            <div class="flex flex-column gap-1">
                                <label for="apiUrl" class="text-900 font-medium text-sm">Bot API URL</label>
                                <InputText id="apiUrl" v-model="botData.api_url" placeholder="http://192.168.1.100:8080"
                                    class="w-full" :class="{ 'p-invalid': errors.api_url }" />
                                <small v-if="errors.api_url" class="p-error">{{ errors.api_url }}</small>
                            </div>
                        </div>

                        <div class="col-12 md:col-8">
                            <div class="flex flex-column gap-1">
                                <label for="description" class="text-900 font-medium text-sm">Description <span
                                        class="text-500">(Optional)</span></label>
                                <Textarea id="description" v-model="botData.description"
                                    placeholder="Bot strategy description..." class="w-full" rows="4" />
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Authentication Section -->
                <div class="col-12">
                    <h3 class="text-base font-semibold mb-2 text-900">Authentication</h3>
                    <div class="auth-method-selection p-2 border-round bg-gray-50 mb-2">
                        <div class="flex gap-4">
                            <div class="flex align-items-center">
                                <RadioButton id="auth_token" v-model="botData.auth_method" value="token"
                                    name="auth_method" />
                                <label for="auth_token" class="ml-2 font-medium text-sm">API Token</label>
                            </div>
                            <div class="flex align-items-center">
                                <RadioButton id="auth_basic" v-model="botData.auth_method" value="basic"
                                    name="auth_method" />
                                <label for="auth_basic" class="ml-2 font-medium text-sm">Username & Password</label>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Authentication Fields -->
                <div v-if="botData.auth_method === 'token'" class="col-12">
                    <div class="grid gap-2">
                        <div class="col-12 lg:col-8">
                            <div class="flex flex-column gap-1">
                                <label for="apiToken" class="text-900 font-medium text-sm">API Token</label>
                                <Password id="apiToken" v-model="botData.api_token" placeholder="Your bot's API token"
                                    :feedback="false" :toggleMask="true" class="w-full"
                                    :class="{ 'p-invalid': errors.api_token }" />
                                <small v-if="errors.api_token" class="p-error">{{ errors.api_token }}</small>
                            </div>
                        </div>
                    </div>
                </div>

                <div v-if="botData.auth_method === 'basic'" class="col-12">
                    <div class="grid">
                        <div class="col-12 md:col-5">
                            <div class="flex flex-column gap-1">
                                <label for="username" class="text-900 font-medium">Username</label>
                                <InputText id="username" v-model="botData.username" placeholder="Bot username"
                                    class="w-full" :class="{ 'p-invalid': errors.username }" />
                                <small v-if="errors.username" class="p-error">{{ errors.username }}</small>
                            </div>
                        </div>

                        <div class="col-12 md:col-5">
                            <div class="flex flex-column gap-1">
                                <label for="password" class="text-900 font-medium">Password</label>
                                <Password id="password" v-model="botData.password" placeholder="Bot password"
                                    :feedback="false" :toggleMask="true" class="w-full"
                                    :class="{ 'p-invalid': errors.password }" />
                                <small v-if="errors.password" class="p-error">{{ errors.password }}</small>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Connection Testing Section -->
                <div class="col-12">
                    <div class="connection-section p-3 border-round bg-blue-50 border-1 border-blue-200">
                        <div class="flex align-items-center justify-content-between mb-2">
                            <h4 class="text-sm font-semibold text-900 m-0">Connection Test</h4>
                            <Button type="button" label="Test Connection" icon="pi pi-wifi" :loading="testingConnection"
                                severity="info" size="small" @click="testConnection" />
                        </div>

                        <!-- Connection Status -->
                        <div v-if="connectionStatus">
                            <div v-if="connectionStatus.success"
                                class="flex align-items-center text-green-700 bg-green-50 p-2 border-round border-1 border-green-200">
                                <i class="pi pi-check-circle mr-2"></i>
                                <span class="text-sm font-medium">{{ connectionStatus.message }}</span>
                            </div>
                            <div v-else
                                class="flex align-items-center text-red-700 bg-red-50 p-2 border-round border-1 border-red-200">
                                <i class="pi pi-times-circle mr-2"></i>
                                <span class="text-sm font-medium">{{ connectionStatus.message }}</span>
                            </div>
                        </div>

                        <!-- Error Message -->
                        <Message v-if="error" severity="error" :closable="true" @close="error = null" class="mt-2">
                            {{ error }}
                        </Message>
                    </div>
                </div>
            </form>
        </div>

        <template #footer>
            <div class="flex justify-content-end gap-2">
                <Button label="Cancel" icon="pi pi-times" @click="closeModal" severity="secondary" outlined />
                <Button label="Connect Bot" icon="pi pi-link" :loading="connecting"
                    :disabled="!connectionStatus?.success" @click="connectBot" />
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
.connect-bot-modal :deep(.p-dialog) {
    border-radius: 12px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.connect-bot-modal :deep(.p-dialog-header) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 12px 12px 0 0;
    padding: 1rem 1.5rem;
}

.connect-bot-modal :deep(.p-dialog-content) {
    padding: 1.5rem;
    background: #fafafa;
    overflow-y: auto;
    max-height: calc(90vh - 150px);
}

.connect-bot-modal :deep(.p-dialog-footer) {
    padding: 1rem 1.5rem;
    background: white;
    border-radius: 0 0 12px 12px;
    border-top: 1px solid #e9ecef;
}

.connect-bot-modal :deep(.p-dialog-title) {
    color: white;
    font-size: 1.25rem;
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

.info-card {
    background: #e3f2fd;
    border: 1px solid #bbdefb;
}

.auth-method-selection {
    background: white;
    border: 1px solid #e9ecef;
}

.connection-section {
    background: #f8fffe;
    border: 1px solid #b3e5fc;
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
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.95rem;
}

:deep(.p-password-input),
:deep(.p-inputtextarea) {
    width: 100%;
}

:deep(.p-inputtext:focus),
:deep(.p-password-input:focus),
:deep(.p-inputtextarea:focus) {
    border-color: #667eea;
    box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
    transform: translateY(-1px);
}

:deep(.p-invalid) {
    border-color: #ef4444 !important;
    box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.1) !important;
}

:deep(.p-button) {
    transition: all 0.3s ease;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
}

:deep(.p-button:hover) {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

:deep(.p-button-sm) {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
}

:deep(.p-radiobutton) {
    width: 20px;
    height: 20px;
}

:deep(.p-radiobutton .p-radiobutton-box) {
    border: 2px solid #d1d5db;
    border-radius: 50%;
    transition: all 0.3s ease;
}

:deep(.p-radiobutton .p-radiobutton-box:hover) {
    border-color: #667eea;
}

:deep(.p-radiobutton .p-radiobutton-box.p-highlight) {
    border-color: #667eea;
    background: #667eea;
}

h3,
h4 {
    color: #1f2937;
    margin: 0;
}

/* Section cards */
.col-12>h3 {
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 0.25rem;
}

/* Compact modal layout */
.modal-intro p {
    margin-bottom: 0.5rem;
}

.grid {
    gap: 0.75rem;
}

.grid.gap-2 {
    gap: 0.5rem;
}

.grid.gap-3 {
    gap: 0.75rem;
}

/* Small text styles */
.text-sm {
    font-size: 0.875rem;
}
</style>