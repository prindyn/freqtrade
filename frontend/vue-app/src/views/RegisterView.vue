<template>
    <div class="register-view p-d-flex p-jc-center p-ai-center">
        <Card style="width: 30em; margin-top: 2em;">
            <template #title>
                <div class="p-text-center">Register New Account</div>
            </template>
            <template #content>
                <form @submit.prevent="handleRegister" class="p-fluid">
                    <div class="p-field p-mb-3">
                        <label for="fullName" class="p-mb-1">Full Name (Optional)</label>
                        <InputText id="fullName" type="text" v-model="fullName" placeholder="Enter your full name" />
                    </div>
                    <div class="p-field p-mb-3">
                        <label for="email" class="p-mb-1">Email</label>
                        <InputText id="email" type="email" v-model="email" placeholder="Enter your email" required />
                    </div>
                    <div class="p-field p-mb-4">
                        <label for="password" class="p-mb-1">Password</label>
                        <Password id="password" v-model="password" placeholder="Choose a password" :feedback="true"
                            :toggleMask="true" required />
                    </div>
                    <div class="p-field p-mb-4">
                        <label for="confirmPassword" class="p-mb-1">Confirm Password</label>
                        <Password id="confirmPassword" v-model="confirmPassword" placeholder="Confirm your password"
                            :feedback="false" :toggleMask="true" required />
                    </div>
                    <Button type="submit" label="Register" icon="pi pi-user-plus" :loading="isLoading" class="p-mb-3" />
                </form>
                <Message v-if="error" severity="error" :closable="true" @close="error = null">{{ error }}</Message>
                <Message v-if="successMessage" severity="success" :closable="true" @close="successMessage = null">{{
                    successMessage }}</Message>
                <div class="p-mt-4 p-text-center">
                    Already have an account? <router-link to="/login">Login here</router-link>
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
    name: 'RegisterView',
    components: { Card, InputText, Password, Button, Message },
    data() {
        return {
            email: '',
            password: '',
            confirmPassword: '',
            fullName: '',
            isLoading: false,
            error: null,
            successMessage: null,
        };
    },
    methods: {
        async handleRegister() {
            this.isLoading = true;
            this.error = null;
            this.successMessage = null;

            if (this.password !== this.confirmPassword) {
                this.error = 'Passwords do not match.';
                this.isLoading = false;
                return;
            }
            if (!this.email || !this.password) {
                this.error = 'Email and Password are required.';
                this.isLoading = false;
                return;
            }

            try {
                const userData = {
                    email: this.email,
                    password: this.password,
                    full_name: this.fullName || null, // Send null if empty, backend handles Optional
                };
                await api.register(userData);
                this.successMessage = 'Registration successful! Please login.';
                // Optionally redirect to login after a delay or clear form
                setTimeout(() => {
                    if (!this.error) { // Only redirect if no error occurred during success message display
                        this.$router.push({ name: 'login' });
                    }
                }, 2000);
            } catch (err) {
                if (err.response && err.response.data && err.response.data.detail) {
                    this.error = err.response.data.detail;
                } else if (err.message) {
                    this.error = 'Registration failed: ' + err.message;
                } else {
                    this.error = 'An unexpected error occurred during registration.';
                }
                console.error('Registration error:', err);
            } finally {
                this.isLoading = false;
            }
        },
    },
};
</script>

<style scoped>
.register-view {
    min-height: calc(100vh - 100px);
    /* Adjust 100px based on navbar height */
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f4f7f6;
    /* Match App.vue's body background */
}

.p-field {
    margin-bottom: 1.5rem;
}

label {
    display: block;
    margin-bottom: 0.5rem;
    /* Space between label and input */
}
</style>
