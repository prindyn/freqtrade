<template>
    <div id="app">
        <nav class="navbar">
            <div class="container">
                <!-- Brand -->
                <router-link to="/" class="navbar-brand">
                    <i class="pi pi-chart-line mr-2"></i>
                    TradeWise
                </router-link>
                
                <!-- Mobile menu toggle -->
                <button 
                    class="navbar-toggle"
                    @click="toggleMobileMenu"
                    :class="{ 'active': mobileMenuOpen }"
                >
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
                
                <!-- Navigation Menu -->
                <div class="navbar-menu" :class="{ 'active': mobileMenuOpen }">
                    <ul class="navbar-nav">
                        <!-- Public Navigation -->
                        <li class="nav-item">
                            <router-link to="/" class="nav-link" @click="closeMobileMenu">
                                <i class="pi pi-home"></i>
                                <span>Home</span>
                            </router-link>
                        </li>
                        
                        <!-- Authenticated Navigation -->
                        <template v-if="isAuthenticated">
                            <li class="nav-item">
                                <router-link to="/dashboard" class="nav-link" @click="closeMobileMenu">
                                    <i class="pi pi-th-large"></i>
                                    <span>Dashboard</span>
                                </router-link>
                            </li>
                            
                            <li class="nav-item dropdown" @mouseenter="showDropdown = 'bots'" @mouseleave="showDropdown = null">
                                <a class="nav-link dropdown-toggle" :class="{ 'active': showDropdown === 'bots' }">
                                    <i class="pi pi-cog"></i>
                                    <span>Bots</span>
                                    <i class="pi pi-chevron-down"></i>
                                </a>
                                <ul class="dropdown-menu" :class="{ 'show': showDropdown === 'bots' }">
                                    <li>
                                        <router-link to="/bots" class="dropdown-item" @click="closeMobileMenu">
                                            <i class="pi pi-list"></i>
                                            My Bots
                                        </router-link>
                                    </li>
                                    <li>
                                        <a class="dropdown-item" href="#" @click.prevent="openConnectBotModal">
                                            <i class="pi pi-link"></i>
                                            Connect Bot
                                        </a>
                                    </li>
                                </ul>
                            </li>
                            
                            <li class="nav-item">
                                <router-link to="/marketplace" class="nav-link" @click="closeMobileMenu">
                                    <i class="pi pi-shopping-cart"></i>
                                    <span>Marketplace</span>
                                </router-link>
                            </li>
                            
                            <li class="nav-item dropdown" @mouseenter="showDropdown = 'account'" @mouseleave="showDropdown = null">
                                <a class="nav-link dropdown-toggle" :class="{ 'active': showDropdown === 'account' }">
                                    <i class="pi pi-user"></i>
                                    <span>Account</span>
                                    <i class="pi pi-chevron-down"></i>
                                </a>
                                <ul class="dropdown-menu" :class="{ 'show': showDropdown === 'account' }">
                                    <li>
                                        <router-link to="/profile" class="dropdown-item" @click="closeMobileMenu">
                                            <i class="pi pi-user-edit"></i>
                                            Profile
                                        </router-link>
                                    </li>
                                    <li>
                                        <router-link to="/settings" class="dropdown-item" @click="closeMobileMenu">
                                            <i class="pi pi-cog"></i>
                                            Settings
                                        </router-link>
                                    </li>
                                    <li class="dropdown-divider"></li>
                                    <li>
                                        <a class="dropdown-item" href="#" @click.prevent="logout">
                                            <i class="pi pi-sign-out"></i>
                                            Logout
                                        </a>
                                    </li>
                                </ul>
                            </li>
                        </template>
                        
                        <!-- Unauthenticated Navigation -->
                        <template v-else>
                            <li class="nav-item">
                                <router-link to="/login" class="nav-link" @click="closeMobileMenu">
                                    <i class="pi pi-sign-in"></i>
                                    <span>Login</span>
                                </router-link>
                            </li>
                            <li class="nav-item">
                                <router-link to="/register" class="nav-link nav-link-primary" @click="closeMobileMenu">
                                    <i class="pi pi-user-plus"></i>
                                    <span>Sign Up</span>
                                </router-link>
                            </li>
                        </template>
                    </ul>
                </div>
            </div>
        </nav>
        <main class="main-content container">
            <router-view />
        </main>
        
        <!-- Connect Bot Modal -->
        <ConnectBotModal 
            v-model:visible="connectBotModalVisible"
            @bot-connected="onBotConnected"
        />
        
        <Toast />
    </div>
</template>

<script>
import api from '@/services/api'; // Import your API service
import Toast from 'primevue/toast';
import ConnectBotModal from '@/components/ConnectBotModal.vue';

export default {
    name: 'App',
    components: {
        Toast,
        ConnectBotModal
    },
    data() {
        return {
            isAuthenticated: false, // Reactive property
            mobileMenuOpen: false,
            showDropdown: null,
            connectBotModalVisible: false
        };
    },
    watch: {
        // Watch for route changes to update authentication status
        '$route'() {
            this.updateAuthStatus();
            this.closeMobileMenu(); // Close mobile menu on route change
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
            this.closeMobileMenu(); // Close mobile menu if open
            this.$router.push({ name: 'login' }); // Redirect to login
        },
        toggleMobileMenu() {
            this.mobileMenuOpen = !this.mobileMenuOpen;
        },
        closeMobileMenu() {
            this.mobileMenuOpen = false;
            this.showDropdown = null;
        },
        openConnectBotModal() {
            this.connectBotModalVisible = true;
            this.closeMobileMenu();
            this.showDropdown = null;
        },
        onBotConnected(botData) {
            this.connectBotModalVisible = false;
            this.$toast.add({
                severity: 'success',
                summary: 'Bot Connected',
                detail: `Successfully connected ${botData.name}!`,
                life: 5000
            });
        }
    }
};
</script>

<style>
/* Basic global styles */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    background-color: #f8f9fa;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
}

/* Navbar Styles */
.navbar {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 1000;
    padding: 0;
}

.navbar .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
}

.navbar-brand {
    color: white;
    text-decoration: none;
    font-size: 1.75rem;
    font-weight: 700;
    padding: 1rem 0;
    display: flex;
    align-items: center;
    transition: color 0.3s ease;
}

.navbar-brand:hover {
    color: #3498db;
}

.navbar-brand .mr-2 {
    margin-right: 0.5rem;
}

/* Mobile Toggle */
.navbar-toggle {
    display: none;
    flex-direction: column;
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 0.5rem;
    width: 30px;
    height: 30px;
    position: relative;
}

.navbar-toggle span {
    width: 25px;
    height: 3px;
    background-color: white;
    margin: 3px 0;
    transition: 0.3s;
    border-radius: 2px;
}

.navbar-toggle.active span:nth-child(1) {
    transform: rotate(-45deg) translate(-5px, 6px);
}

.navbar-toggle.active span:nth-child(2) {
    opacity: 0;
}

.navbar-toggle.active span:nth-child(3) {
    transform: rotate(45deg) translate(-5px, -6px);
}

/* Navigation Menu */
.navbar-menu {
    display: flex;
}

.navbar-nav {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    align-items: center;
}

.nav-item {
    position: relative;
    margin: 0 0.25rem;
}

.nav-link {
    color: #ecf0f1;
    text-decoration: none;
    padding: 1rem 1rem;
    display: flex;
    align-items: center;
    transition: all 0.3s ease;
    border-radius: 6px;
    font-weight: 500;
}

.nav-link i {
    margin-right: 0.5rem;
    font-size: 1rem;
}

.nav-link:hover,
.nav-link.router-link-active {
    color: white;
    background-color: rgba(255, 255, 255, 0.1);
    transform: translateY(-1px);
}

.nav-link-primary {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white !important;
    border-radius: 25px;
    padding: 0.75rem 1.5rem;
    margin-left: 0.5rem;
}

.nav-link-primary:hover {
    background: linear-gradient(135deg, #2980b9 0%, #3498db 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
}

/* Dropdown Styles */
.dropdown {
    position: relative;
}

.dropdown-toggle {
    cursor: pointer;
}

.dropdown-toggle .pi-chevron-down {
    margin-left: 0.5rem;
    font-size: 0.8rem;
    transition: transform 0.3s ease;
}

.dropdown.active .dropdown-toggle .pi-chevron-down,
.dropdown:hover .dropdown-toggle .pi-chevron-down {
    transform: rotate(180deg);
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    background: white;
    min-width: 200px;
    border-radius: 8px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    z-index: 1000;
    border: 1px solid rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.dropdown-menu.show {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

.dropdown-item {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    color: #2c3e50;
    text-decoration: none;
    transition: all 0.2s ease;
    font-weight: 500;
}

.dropdown-item:hover {
    background-color: #f8f9fa;
    color: #3498db;
    padding-left: 1.25rem;
}

.dropdown-item i {
    margin-right: 0.75rem;
    font-size: 0.9rem;
    width: 16px;
    text-align: center;
}

.dropdown-divider {
    height: 1px;
    background-color: #dee2e6;
    margin: 0.5rem 0;
}

/* Main Content */
.main-content {
    padding: 2rem 0;
    min-height: calc(100vh - 80px);
}

/* Responsive Design */
@media (max-width: 768px) {
    .navbar-toggle {
        display: flex;
    }
    
    .navbar-menu {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        opacity: 0;
        visibility: hidden;
        transform: translateY(-20px);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
    }
    
    .navbar-menu.active {
        opacity: 1;
        visibility: visible;
        transform: translateY(0);
    }
    
    .navbar-nav {
        flex-direction: column;
        width: 100%;
        padding: 1rem 0;
    }
    
    .nav-item {
        margin: 0;
        width: 100%;
    }
    
    .nav-link {
        padding: 1rem 1.5rem;
        border-radius: 0;
        justify-content: flex-start;
    }
    
    .nav-link-primary {
        margin: 0.5rem 1rem;
        border-radius: 25px;
        text-align: center;
        justify-content: center;
    }
    
    .dropdown-menu {
        position: static;
        opacity: 1;
        visibility: visible;
        transform: none;
        box-shadow: none;
        background: rgba(255, 255, 255, 0.1);
        border: none;
        border-radius: 0;
        margin: 0;
        padding: 0;
    }
    
    .dropdown-item {
        color: #ecf0f1;
        padding: 0.75rem 2rem;
    }
    
    .dropdown-item:hover {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
    }
    
    .dropdown-divider {
        background-color: rgba(255, 255, 255, 0.2);
        margin: 0.25rem 1rem;
    }
}

@media (max-width: 480px) {
    .navbar-brand {
        font-size: 1.5rem;
    }
    
    .container {
        padding: 0 10px;
    }
    
    .main-content {
        padding: 1rem 0;
    }
}
</style>
