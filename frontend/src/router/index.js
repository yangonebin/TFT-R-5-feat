import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import SignupView from '../views/SignupView.vue'
import StockView from '../views/StockView.vue'
import StockDetailView from '../views/StockDetailView.vue'
import ExchangeView from '../views/ExchangeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/signup', name: 'signup', component: SignupView },
    { path: '/exchange', name: 'exchange', component: ExchangeView },
    { path: '/stock', name: 'stock', component: StockView },
    { path: '/stock/:videoId', name: 'stock-detail', component: StockDetailView },
    { path: '/deposit', name: 'deposit', component: HomeView }, 
    { path: '/map', name: 'map', component: HomeView },
    { path: '/community', name: 'community', component: HomeView },
  ]
})

export default router