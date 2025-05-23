import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import CreateBotView from '../views/CreateBotView.vue';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
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
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

// Basic navigation guard
router.beforeEach((to, from, next) => {
  const loggedIn = localStorage.getItem('authToken');

  if (to.matched.some(record => record.meta.requiresAuth) && !loggedIn) {
    next({ name: 'login' }); // Redirect to login if not authenticated
  } else {
    next(); // Proceed as normal
  }
});

export default router;
