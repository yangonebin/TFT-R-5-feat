from django.urls import path
from . import views

urlpatterns = [
    # ❌ [수정 전] 이렇게 하면 '/articles/articles/'가 됩니다 (에러 원인)
    # path('articles/', views.article_list),

    # ✅ [수정 후] 따옴표 안을 비워주세요! (최종 주소: /articles/)
    path('', views.article_list),
    
    # 상세 경로도 마찬가지로 앞부분을 지워줍니다.
    path('<int:article_pk>/', views.article_detail),
    path('<int:article_pk>/comments/', views.comment_create),
    path('<int:article_pk>/comments/<int:comment_pk>/', views.comment_delete),
]