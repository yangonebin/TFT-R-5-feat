from django.urls import path
from . import views

urlpatterns = [
    # 1. 데이터 저장 (제일 먼저 실행해야 함!)
    path('save-deposit-products/', views.save_deposit_products),

    # 2. 전체 목록 조회 (deposit -> deposit-products)
    path('deposit-products/', views.product_list),
    
    # 3. 상세 조회 (이게 없어서 상세페이지가 안 열렸음)
    path('deposit-products/<str:fin_prdt_cd>/', views.deposit_product_detail),

    # 4. 가입
    path('join/<str:product_cd>/', views.join_product),
    

    path('exchange/', views.gold_silver_prices),

    path('users/joined-products/', views.user_joined_products),
   
]