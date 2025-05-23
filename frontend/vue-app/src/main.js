import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // Assuming your router is here
import PrimeVue from 'primevue/config';

// Import PrimeVue theme (e.g., Saga Blue, choose one)
import 'primevue/resources/themes/saga-blue/theme.css'; // or other themes like 'lara-light-indigo'
import 'primevue/resources/primevue.min.css';
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css'; // For PrimeFlex utilities

// Optionally, import specific components globally or import them in components as needed
// import Button from 'primevue/button';
// import InputText from 'primevue/inputtext';

const app = createApp(App);

app.use(router);
app.use(PrimeVue, { ripple: true }); // ripple effect is optional

// Globally register components if you choose to:
// app.component('Button', Button);
// app.component('InputText', InputText);

app.mount('#app');
