import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import DashboardView from '../views/DashboardView.vue';
import MarketplaceView from '../views/MarketplaceView.vue';
import ProfileView from '../views/ProfileView.vue';
import SettingsView from '../views/SettingsView.vue';
import TerminalView from '../views/TerminalView.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView
  },
  {
    path: '/about', 
    name: 'about',
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  {
    path: '/bots',
    name: 'bots',
    component: () => import(/* webpackChunkName: "bots" */ '../views/BotsView.vue'),
    meta: { requiresAuth: true } // Example of adding auth guard meta
  },
  {
    path: '/marketplace',
    name: 'marketplace',
    component: MarketplaceView,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/terminal',
    name: 'terminal',
    component: TerminalView,
    meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

// Navigation guard: redirect to login if not authenticated
router.beforeEach((to, _from, next) => {
  const loggedIn = localStorage.getItem('authToken');
  const publicPages = ['home', 'login', 'register', 'about'];
  const authRequired = !publicPages.includes(to.name);

  // If user is logged in and tries to access home, redirect to dashboard
  if (loggedIn && to.name === 'home') {
    return next({ name: 'dashboard' });
  }

  // If auth required and not logged in, redirect to login
  if (authRequired && !loggedIn) {
    return next({ name: 'login' });
  }
  
  next();
});

export default router;
