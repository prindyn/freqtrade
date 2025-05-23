<template>
    <div class="login-view p-d-flex p-jc-center p-ai-center">
        <Card style="width: 28em; margin-top: 2em;">
            <template #title>
                <div class="p-text-center">Login</div>
            </template>
            <template #content>
                <form @submit.prevent="handleLogin" class="p-fluid">
                    <div class="p-field p-mb-3">
                        <label for="email" class="p-mb-1">Email</label>
                        <InputText id="email" type="email" v-model="email" placeholder="Enter your email" />
                    </div>
                    <div class="p-field p-mb-4"> <!-- Increased margin bottom -->
                        <label for="password" class="p-mb-1">Password</label>
                        <Password id="password" v-model="password" placeholder="Enter your password" :feedback="false"
                            :toggleMask="true" />
                    </div>
                    <Button type="submit" label="Login" icon="pi pi-sign-in" :loading="isLoading" class="p-mb-3" />
                </form>
                <Message v-if="error" severity="error" :closable="true" @close="error = null">{{ error }}</Message>
                <div class="p-mt-4 p-text-center"> <!-- Increased margin top -->
                    Don't have an account? <router-link to="/register">Register here</router-link>
                </div>
            </template>
        </Card>
    </div>
</template>

<script>
import api from '@/services/api';
import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Message from 'primevue/message';

export default {
    name: 'LoginView',
    components: { Card, InputText, Password, Button, Message },
    data() {
        return {
            email: '',
            password: '',
            isLoading: false,
            error: null,
        };
    },
    methods: {
        async handleLogin() {
            this.isLoading = true;
            this.error = null;
            try {
                const response = await api.login({ username: this.email, password: this.password });
                const token = response.data.access_token;
                localStorage.setItem('authToken', token);
                api.setAuthHeader(token); // Update apiClient with the new token
                this.$router.push({ name: 'bots' }); // Navigate to a protected route
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
};
</script>

<style scoped>
.login-view {
    min-height: calc(100vh - 100px);
    /* Adjust 100px based on navbar height */
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f4f7f6;
    /* Match App.vue's body background */
}

/* PrimeVue class p-mb-x didn't work as expected in template, using CSS */
.p-field {
    margin-bottom: 1.5rem;
}

label {
    display: block;
    margin-bottom: 0.5rem;
    /* Space between label and input */
}
</style>
