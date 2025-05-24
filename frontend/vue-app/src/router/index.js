import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import CreateBotView from '../views/CreateBotView.vue';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import DashboardView from '../views/DashboardView.vue';
import ConnectBotView from '../views/ConnectBotView.vue';
import MarketplaceView from '../views/MarketplaceView.vue';

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
    path: '/create-bot',
    name: 'create-bot',
    component: CreateBotView,
    meta: { requiresAuth: true } // Example of adding auth guard meta
  },
  {
    path: '/connect-bot',
    name: 'connect-bot',
    component: ConnectBotView,
    meta: { requiresAuth: true }
  },
  {
    path: '/marketplace',
    name: 'marketplace',
    component: MarketplaceView,
    meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

// Navigation guard: redirect to login if not authenticated
router.beforeEach((to, from, next) => {
  const loggedIn = localStorage.getItem('authToken');
  const publicPages = ['login', 'register'];
  const authRequired = !publicPages.includes(to.name);

  if (authRequired && !loggedIn) {
    return next({ name: 'login' });
  }
  next();
});

export default router;
