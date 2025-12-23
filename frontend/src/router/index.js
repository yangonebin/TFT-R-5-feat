import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import SignupView from '../views/SignupView.vue'
import StockView from '../views/StockView.vue'
import StockDetailView from '../views/StockDetailView.vue'
import ExchangeView from '../views/ExchangeView.vue'
import MapView from '../views/MapView.vue'
// import ArticleView from '../views/ArticleView.vue'  <-- 삭제됨

import ProductView from '@/views/ProductView.vue'
import DepositDetailView from '@/views/DepositDetailView.vue'
import CommunityView from '@/views/CommunityView.vue'
import ArticleDetailView from '@/views/ArticleDetailView.vue'
import ArticleCreateView from '@/views/ArticleCreateView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },

    // 회원가입 및 로그인
    { path: '/login', name: 'login', component: LoginView },
    { path: '/signup', name: 'signup', component: SignupView },

    // 환율 및 주식
    { path: '/exchange', name: 'exchange', component: ExchangeView },
    { path: '/stock', name: 'stock', component: StockView },
    { path: '/stock/:videoId', name: 'stock-detail', component: StockDetailView },
    
    // 예금 상품 (Deposit)
    { path: '/deposit', name: 'deposit', component: ProductView }, 
    { path: '/deposit/:id', name: 'deposit-detail', component: DepositDetailView },
    
    // 지도
    { path: '/map', name: 'map', component: MapView },


    { path: '/articles', name: 'articles', component: CommunityView },
    { path: '/articles/:id', name: 'article-detail', component: ArticleDetailView },
    { path: '/articles/create', name: 'article-create', component: ArticleCreateView },


  ]
})

export default router