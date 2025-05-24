<template>
    <div id="app">
        <!-- Top Header -->
        <header class="top-header" :class="{ 'logged-out': !isAuthenticated }">
            <div class="header-container">
                <div class="header-left">
                    <button v-if="isAuthenticated" class="sidebar-toggle" @click="toggleSidebar">
                        <i class="pi pi-bars"></i>
                    </button>
                    <router-link to="/" class="brand">
                        TradeWise
                    </router-link>
                </div>

                <!-- Account Menu - stays on the right -->
                <div class="header-right">
                    <template v-if="isAuthenticated">
                        <div class="account-dropdown" @mouseenter="showDropdown = 'account'"
                            @mouseleave="showDropdown = null">
                            <a class="account-trigger" :class="{ 'active': showDropdown === 'account' }">
                                <i class="pi pi-user"></i>
                                <span>Account</span>
                                <i class="pi pi-chevron-down"></i>
                            </a>
                            <ul class="dropdown-menu" :class="{ 'show': showDropdown === 'account' }">
                                <li>
                                    <router-link to="/profile" class="dropdown-item">
                                        <i class="pi pi-user-edit"></i>
                                        Profile
                                    </router-link>
                                </li>
                                <li>
                                    <router-link to="/settings" class="dropdown-item">
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
                        </div>
                    </template>

                    <!-- Unauthenticated Links -->
                    <template v-else>
                        <router-link to="/login" class="auth-link">
                            <i class="pi pi-sign-in"></i>
                            <span>Login</span>
                        </router-link>
                        <router-link to="/register" class="auth-link auth-link-primary">
                            <i class="pi pi-user-plus"></i>
                            <span>Sign Up</span>
                        </router-link>
                    </template>
                </div>
            </div>
        </header>

        <!-- App Body (Sidebar + Main Content) -->
        <div class="app-body" :class="{ 'has-persistent-sidebar': isPersistentSidebar && isAuthenticated }">
            <!-- Left Sidebar - Only show for authenticated users -->
            <aside v-if="isAuthenticated" class="sidebar" :class="{ 'sidebar-open': sidebarOpen, 'sidebar-persistent': isPersistentSidebar }">
                <nav class="sidebar-nav">
                    <router-link to="/dashboard" class="sidebar-link" @click="closeSidebar">
                        <i class="pi pi-th-large"></i>
                        <span>Dashboard</span>
                    </router-link>

                    <div class="sidebar-dropdown">
                        <a class="sidebar-link dropdown-trigger" @click="toggleSidebarDropdown('bots')">
                            <div>
                                <i class="pi pi-android"></i>
                                <span>Bots</span>
                            </div>
                            <i class="pi pi-chevron-down dropdown-arrow"
                                :class="{ rotated: sidebarDropdowns.bots }"></i>
                        </a>
                        <div class="sidebar-dropdown-menu" :class="{ show: sidebarDropdowns.bots }">
                            <router-link to="/bots" class="sidebar-dropdown-item" @click="closeSidebar">
                                <i class="pi pi-list"></i>
                                <span>All Bots</span>
                            </router-link>
                            <router-link to="/bots/templates" class="sidebar-dropdown-item" @click="closeSidebar">
                                <i class="pi pi-copy"></i>
                                <span>Bot Templates</span>
                            </router-link>
                        </div>
                    </div>

                    <router-link to="/marketplace" class="sidebar-link" @click="closeSidebar">
                        <i class="pi pi-shopping-cart"></i>
                        <span>Marketplace</span>
                    </router-link>

                    <router-link to="/terminal" class="sidebar-link" @click="closeSidebar">
                        <i class="pi pi-desktop"></i>
                        <span>Terminal</span>
                    </router-link>
                </nav>
            </aside>

            <!-- Sidebar Overlay - Only show for authenticated users -->
            <div v-if="isAuthenticated" class="sidebar-overlay" :class="{ active: sidebarOpen && !isPersistentSidebar }" @click="closeSidebar">
            </div>

            <!-- Main Content -->
            <main class="main-content"
                :class="{ 'sidebar-expanded': sidebarOpen && isAuthenticated, 'sidebar-persistent-open': isPersistentSidebar && isAuthenticated }">
                <router-view />
            </main>
        </div>



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
            sidebarOpen: false,
            showDropdown: null,
            sidebarDropdowns: {
                bots: false
            },
            windowWidth: window.innerWidth
        };
    },
    computed: {
        isPersistentSidebar() {
            return this.windowWidth >= 1200;
        }
    },
    watch: {
        // Watch for route changes to update authentication status
        '$route'() {
            this.updateAuthStatus();
            this.closeSidebar(); // Close sidebar on route change
        }
    },
    created() {
        this.updateAuthStatus(); // Initial check

        // Also, set the auth header if a token exists from a previous session
        const token = localStorage.getItem('authToken');
        if (token) {
            api.setAuthHeader(token);
        }

        // Add window resize listener
        window.addEventListener('resize', this.handleResize);
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.handleResize);
    },
    methods: {
        updateAuthStatus() {
            this.isAuthenticated = !!localStorage.getItem('authToken');
        },
        handleResize() {
            this.windowWidth = window.innerWidth;
        },
        logout() {
            localStorage.removeItem('authToken');
            api.setAuthHeader(null); // Clear Authorization header in API client
            this.updateAuthStatus(); // Update reactive property
            this.closeSidebar(); // Close sidebar if open
            this.$router.push({ name: 'login' }); // Redirect to login
        },
        toggleSidebar() {
            this.sidebarOpen = !this.sidebarOpen;
        },
        closeSidebar() {
            this.sidebarOpen = false;
            this.showDropdown = null;
            this.sidebarDropdowns.bots = false;
        },
        toggleSidebarDropdown(dropdown) {
            this.sidebarDropdowns[dropdown] = !this.sidebarDropdowns[dropdown];
        }
    }
};
</script>

<style>
/* Basic global styles */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    line-height: 1.6;
}

#app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

.app-body {
    display: flex;
    flex: 1;
    margin-top: 64px;
}

@media (min-width: 1200px) {
    .app-body.has-persistent-sidebar {
        display: flex;
    }
}

.mr-2 {
    margin-right: 0.5rem;
}

/* Top Header - Modern Minimalistic Design */
.top-header {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1001;
    height: 64px;
    transition: all 0.3s ease;
}

/* Minimalistic header for logged out users */
.top-header.logged-out {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    box-shadow: 0 1px 20px rgba(0, 0, 0, 0.08);
}

.top-header.logged-out .brand {
    color: #0f172a;
    font-weight: 700;
    font-size: 1.5rem;
    letter-spacing: -0.025em;
    text-decoration: none;
}

.top-header.logged-out .brand:hover {
    color: #3b82f6;
}

.top-header.logged-out .header-right {
    gap: 0.5rem;
}

.top-header.logged-out .auth-link {
    color: #64748b;
    background: transparent;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-weight: 500;
    font-size: 0.875rem;
    padding: 0.5rem 1rem;
    transition: all 0.2s ease;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 0.375rem;
}

.top-header.logged-out .auth-link:hover {
    color: #475569;
    background: #f8fafc;
    border-color: #cbd5e1;
}

.top-header.logged-out .auth-link-primary {
    background: #3b82f6;
    color: white !important;
    border: 1px solid #3b82f6;
    font-weight: 600;
}

.top-header.logged-out .auth-link-primary:hover {
    background: #2563eb;
    border-color: #2563eb;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 100%;
    padding: 0 1rem;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.sidebar-toggle {
    background: transparent;
    border: none;
    color: white;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 4px;
    transition: background-color 0.3s ease;
}

.sidebar-toggle:hover {
    background-color: rgba(255, 255, 255, 0.1);
}

.brand {
    color: white;
    text-decoration: none;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.025em;
    transition: color 0.3s ease;
}

.brand:hover {
    color: #3b82f6;
}

/* Header Right - Account Menu */
.header-right {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.account-dropdown {
    position: relative;
}

.account-trigger {
    color: #ecf0f1;
    text-decoration: none;
    padding: 0.5rem 1rem;
    display: flex;
    align-items: center;
    transition: all 0.3s ease;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    gap: 0.5rem;
}

.account-trigger:hover,
.account-trigger.active {
    color: white;
    background-color: rgba(255, 255, 255, 0.1);
}

.account-trigger .pi-chevron-down {
    font-size: 0.8rem;
    transition: transform 0.3s ease;
}

.account-trigger.active .pi-chevron-down {
    transform: rotate(180deg);
}

.auth-link {
    color: #ecf0f1;
    text-decoration: none;
    padding: 0.5rem 1rem;
    display: flex;
    align-items: center;
    transition: all 0.3s ease;
    border-radius: 6px;
    font-weight: 500;
    gap: 0.5rem;
    border: 1px solid transparent;
}

.auth-link:hover {
    color: white;
    background-color: rgba(255, 255, 255, 0.1);
}

.auth-link-primary {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white !important;
    border-radius: 25px;
    padding: 0.5rem 1.5rem;
    border: 1px solid transparent;
}

.auth-link-primary:hover {
    background: linear-gradient(135deg, #2980b9 0%, #3498db 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
}

/* Dropdown Menu */
.dropdown-menu {
    position: absolute;
    top: 100%;
    right: 0;
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
    list-style: none;
    padding: 0;
    margin: 0;
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
    gap: 0.75rem;
}

.dropdown-item:hover {
    background-color: #f8f9fa;
    color: #3498db;
    padding-left: 1.25rem;
}

.dropdown-divider {
    height: 1px;
    background-color: #dee2e6;
    margin: 0.5rem 0;
}

/* Left Sidebar */
.sidebar {
    position: fixed;
    top: 64px;
    left: -280px;
    width: 280px;
    height: calc(100vh - 64px);
    background: white;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
    transition: left 0.3s ease;
    z-index: 1000;
    overflow-y: auto;
}

.sidebar.sidebar-open {
    left: 0;
}

.sidebar.sidebar-persistent {
    left: 0;
    position: fixed;
}

@media (min-width: 1200px) {
    .sidebar.sidebar-persistent {
        position: static;
        left: 0;
        top: 0;
        height: calc(100vh - 64px);
        box-shadow: none;
        border-right: 1px solid #dee2e6;
        flex-shrink: 0;
    }
}

.sidebar-nav {
    padding: 1rem 0;
}

.sidebar-link {
    display: flex;
    align-items: center;
    padding: 0.75rem 1.5rem;
    color: #2c3e50;
    text-decoration: none;
    transition: all 0.3s ease;
    gap: 1rem;
    font-weight: 500;
}

.sidebar-link:hover,
.sidebar-link.router-link-active {
    background-color: #f8f9fa;
    color: #3498db;
    border-right: 3px solid #3498db;
}

.sidebar-link i {
    font-size: 1.1rem;
    width: 20px;
    text-align: center;
}

/* Sidebar Dropdown */
.sidebar-dropdown {
    position: relative;
}

.sidebar-link.dropdown-trigger {
    cursor: pointer;
}

.sidebar-link.dropdown-trigger {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.sidebar-link.dropdown-trigger>div {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.dropdown-arrow {
    font-size: 0.8rem;
    transition: transform 0.3s ease;
}

.dropdown-arrow.rotated {
    transform: rotate(180deg);
}

.sidebar-dropdown-menu {
    background-color: #f8f9fa;
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}

.sidebar-dropdown-menu.show {
    max-height: 200px;
}

.sidebar-dropdown-item {
    display: flex;
    align-items: center;
    padding: 0.6rem 2rem;
    color: #2c3e50;
    text-decoration: none;
    transition: all 0.3s ease;
    gap: 1rem;
    font-weight: 400;
}

.sidebar-dropdown-item:hover {
    background-color: #e9ecef;
    color: #3498db;
    padding-left: 2.5rem;
}

.sidebar-dropdown-item i {
    font-size: 1rem;
    width: 18px;
    text-align: center;
}

.sidebar-dropdown-divider {
    height: 1px;
    background-color: #dee2e6;
    margin: 0.5rem 1rem;
}

/* Sidebar Overlay */
.sidebar-overlay {
    position: fixed;
    top: 64px;
    left: 0;
    width: 100%;
    height: calc(100vh - 64px);
    background-color: rgba(0, 0, 0, 0.5);
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
    z-index: 999;
}

.sidebar-overlay.active {
    opacity: 1;
    visibility: visible;
}

/* Main Content */
.main-content {
    margin-top: 0;
    transition: margin-left 0.3s ease;
    padding: 2rem;
    min-height: calc(100vh - 64px);
    flex: 1;
}

@media (max-width: 1199px) {
    .main-content {
        margin-top: 0;
    }
}

/* Responsive Design */
@media (max-width: 768px) {
    .header-left .brand {
        font-size: 1.3rem;
    }

    .auth-link span {
        display: none;
    }

    .account-trigger span {
        display: none;
    }

    .sidebar {
        width: 250px;
        left: -250px;
    }

    .main-content {
        padding: 1rem;
    }
}

@media (max-width: 480px) {
    .header-container {
        padding: 0 0.5rem;
    }

    .brand {
        font-size: 1.2rem;
    }

    .sidebar {
        width: 220px;
        left: -220px;
    }

    .main-content {
        padding: 0.5rem;
    }
}

@media (min-width: 1200px) {
    .sidebar.sidebar-open+.sidebar-overlay+.main-content {
        margin-left: 280px;
    }
}
</style>
