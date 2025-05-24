<template>
    <div id="app">
        <nav class="navbar">
            <div class="container">
                <a class="navbar-brand" href="#">Freqtrade SaaS</a>
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <router-link to="/" class="nav-link">Home</router-link>
                    </li>
                    <li v-if="isAuthenticated" class="nav-item">
                        <router-link to="/bots" class="nav-link">Bots</router-link>
                    </li>
                    <li v-if="!isAuthenticated" class="nav-item">
                        <router-link to="/login" class="nav-link">Login</router-link>
                    </li>
                    <li v-if="!isAuthenticated" class="nav-item">
                        <router-link to="/register" class="nav-link">Register</router-link>
                    </li>
                    <li v-if="isAuthenticated" class="nav-item">
                        <a href="#" @click.prevent="logout" class="nav-link">Logout</a>
                    </li>
                    <!-- Add more links as needed -->
                </ul>
            </div>
        </nav>
        <main class="main-content container">
            <router-view />
        </main>
        <Toast />
    </div>
</template>

<script>
import api from '@/services/api'; // Import your API service
import Toast from 'primevue/toast';

export default {
    name: 'App',
    components: {
        Toast
    },
    data() {
        return {
            isAuthenticated: false, // Reactive property
        };
    },
    watch: {
        // Watch for route changes to update authentication status
        '$route'() {
            this.updateAuthStatus();
        }
    },
    created() {
        this.updateAuthStatus(); // Initial check

        // Also, set the auth header if a token exists from a previous session
        const token = localStorage.getItem('authToken');
        if (token) {
            api.setAuthHeader(token);
        }
    },
    methods: {
        updateAuthStatus() {
            this.isAuthenticated = !!localStorage.getItem('authToken');
        },
        logout() {
            localStorage.removeItem('authToken');
            api.setAuthHeader(null); // Clear Authorization header in API client
            this.updateAuthStatus(); // Update reactive property
            this.$router.push({ name: 'login' }); // Redirect to login
        }
    }
};
</script>

<style>
/* Basic global styles and navbar styles */
body {
    font-family: sans-serif;
    margin: 0;
    background-color: #f4f7f6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
}

.navbar {
    background-color: #343a40;
    /* Dark background */
    padding: 1rem 0;
    color: white;
}

.navbar .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.navbar-brand {
    color: white;
    text-decoration: none;
    font-size: 1.5rem;
}

.navbar-nav {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
}

.nav-item {
    margin-left: 15px;
}

.nav-link {
    color: #adb5bd;
    /* Light gray for links */
    text-decoration: none;
}

.nav-link:hover,
.router-link-exact-active {
    color: white;
}

.main-content {
    padding: 20px 0;
}
</style>
