<template>
    <div class="login-container min-h-screen flex align-items-center justify-content-center px-3">
        <div class="login-glass-card p-6 border-round-xl shadow-8 w-full max-w-28rem">
            <div class="text-center mb-6">
                <div class="text-900 text-3xl font-medium mb-2">Welcome Back</div>
                <div class="text-600 font-medium">Sign in to your account</div>
            </div>

            <form @submit.prevent="handleLogin" class="flex flex-column gap-4">
                <div class="flex flex-column gap-2">
                    <label for="email" class="text-900 font-medium">Email</label>
                    <InputText id="email" type="email" v-model="email" placeholder="Enter your email"
                        class="w-full p-3 border-round-lg" :class="{ 'p-invalid': emailError }" />
                </div>

                <div class="flex flex-column gap-2">
                    <label for="password" class="text-900 font-medium">Password</label>
                    <Password id="password" v-model="password" placeholder="Enter your password" :feedback="false"
                        :toggleMask="true" class="w-full" inputClass="p-3 border-round-lg w-full"
                        :class="{ 'p-invalid': passwordError }" />
                </div>

                <Button type="submit" label="Sign In" icon="pi pi-sign-in" :loading="isLoading"
                    class="w-full p-3 text-xl border-round-lg mt-2 login-button" />
            </form>

            <Message v-if="error" severity="error" :closable="true" @close="error = null" class="mt-4">
                {{ error }}
            </Message>

            <div class="text-center mt-6 pt-4 border-top-1 surface-border">
                <span class="text-600">Don't have an account? </span>
                <router-link to="/register" class="font-medium no-underline text-primary cursor-pointer">
                    Create one
                </router-link>
            </div>
        </div>
    </div>
</template>

<script>
import api from '@/services/api';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Message from 'primevue/message';

export default {
    name: 'LoginView',
    components: { InputText, Password, Button, Message },
    data() {
        return {
            email: '',
            password: '',
            isLoading: false,
            error: null,
            emailError: false,
            passwordError: false,
        };
    },
    methods: {
        validateForm() {
            this.emailError = !this.email || !this.email.includes('@');
            this.passwordError = !this.password || this.password.length < 6;
            return !this.emailError && !this.passwordError;
        },
        async handleLogin() {
            if (!this.validateForm()) {
                this.error = 'Please fill in all fields correctly';
                return;
            }

            this.isLoading = true;
            this.error = null;
            try {
                const response = await api.login({ username: this.email, password: this.password });
                const token = response.data.access_token;
                localStorage.setItem('authToken', token);
                api.setAuthHeader(token);
                this.$router.push({ name: 'dashboard' });
            } catch (err) {
                if (err.response && err.response.data && err.response.data.detail) {
                    this.error = err.response.data.detail;
                } else if (err.message) {
                    this.error = 'Login failed: ' + err.message;
                } else {
                    this.error = 'An unexpected error occurred during login.';
                }
                console.error('Login error:', err);
            } finally {
                this.isLoading = false;
            }
        },
    },
    watch: {
        email() {
            this.emailError = false;
        },
        password() {
            this.passwordError = false;
        }
    }
};
</script>

<style scoped>
.login-container {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
}

.login-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 1000"><defs><radialGradient id="a" cx="50%" cy="0%"><stop offset="0%" style="stop-color:rgb(255,255,255);stop-opacity:0.1"/><stop offset="100%" style="stop-color:rgb(255,255,255);stop-opacity:0"/></radialGradient></defs><path d="M0,0v1000h100V0z" fill="url(%23a)"/></svg>');
    pointer-events: none;
}

.login-glass-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    position: relative;
    z-index: 1;
    animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.login-glass-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
    border-radius: inherit;
    pointer-events: none;
}

.login-button {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    border: none;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    overflow: hidden;
}

.login-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(30, 60, 114, 0.4);
}

.login-button:active {
    transform: translateY(0);
}

.login-button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s;
}

.login-button:hover::before {
    left: 100%;
}

:deep(.p-inputtext),
:deep(.p-password-input) {
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    border: 2px solid rgba(42, 82, 152, 0.1);
    background: rgba(255, 255, 255, 0.8);
}

:deep(.p-inputtext:focus),
:deep(.p-password-input:focus) {
    border-color: #2a5298;
    box-shadow: 0 0 0 3px rgba(42, 82, 152, 0.1);
    transform: translateY(-1px);
}

:deep(.p-invalid) {
    border-color: #e74c3c !important;
    animation: shake 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97);
}

label {
    transition: color 0.3s ease;
}

.router-link {
    transition: all 0.3s ease;
    text-decoration: none;
}

.router-link:hover {
    transform: translateY(-1px);
    text-shadow: 0 2px 4px rgba(42, 82, 152, 0.3);
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

@keyframes shake {

    0%,
    100% {
        transform: translateX(0);
    }

    10%,
    30%,
    50%,
    70%,
    90% {
        transform: translateX(-5px);
    }

    20%,
    40%,
    60%,
    80% {
        transform: translateX(5px);
    }
}

:deep(.p-message) {
    animation: slideDown 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 768px) {
    .login-glass-card {
        margin: 1rem;
        padding: 1.5rem;
    }
}
</style>
