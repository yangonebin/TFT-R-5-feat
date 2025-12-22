# backend/finlife/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # 기존: path('products/', views.products_list),
    # 수정: 프론트엔드가 찾는 주소인 'deposit'으로 변경!
    path('deposit/', views.products_list),
    
    # (참고) 혹시 적금(savings) 요청도 있다면 같은 뷰를 연결하거나 별도로 만드세요.
    path('saving/', views.products_list), 
    
    # 상세 조회도 id만 받도록 수정 (필요하다면)
    path('deposit/<int:product_id>/', views.product_detail),
]