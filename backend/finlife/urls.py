from django.urls import path
from . import views

urlpatterns = [

    path('deposit/', views.product_list),
    path('join/<str:product_cd>/', views.join_product),
    path('exchange/', views.gold_silver_prices),
]