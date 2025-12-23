import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import SignupView from '../views/SignupView.vue'
import StockView from '../views/StockView.vue'
import StockDetailView from '../views/StockDetailView.vue'
import ExchangeView from '../views/ExchangeView.vue'
import MapView from '../views/MapView.vue'

import ProductView from '@/views/ProductView.vue'
import DepositDetailView from '@/views/DepositDetailView.vue'
import CommunityView from '@/views/CommunityView.vue'
import ArticleDetailView from '@/views/ArticleDetailView.vue'
import ArticleCreateView from '@/views/ArticleCreateView.vue'
import ProfileView from '@/views/ProfileView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/profile', name: 'profile', component: ProfileView },
    { path: '/', name: 'home', component: HomeView },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/signup', name: 'signup', component: SignupView },
    { path: '/exchange', name: 'exchange', component: ExchangeView },
    { path: '/stock', name: 'stock', component: StockView },
    { path: '/stock/:videoId', name: 'stock-detail', component: StockDetailView },
    
    // [예금 목록]
    { path: '/deposit', name: 'deposit', component: ProductView }, 
    
    // [예금 상세] ★ 변수명 fin_prdt_cd 확인 필수!
    { path: '/deposit/:fin_prdt_cd', name: 'deposit-detail', component: DepositDetailView },
    
    { path: '/map', name: 'map', component: MapView },
    { path: '/articles', name: 'articles', component: CommunityView },
    { path: '/articles/:id', name: 'article-detail', component: ArticleDetailView },
    { path: '/articles/create', name: 'article-create', component: ArticleCreateView },
  ]
})

export default router