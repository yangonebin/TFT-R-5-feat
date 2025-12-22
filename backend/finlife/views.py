# finlife/views.py

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny  # IsAuthenticated 추가!
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Products, DepositProducts  # DepositProducts 모델 확인
from .serializers import ProductsSerializer
# ------------------------------------------------
# 목록 조회 (누구나 볼 수 있게 허용)
# ------------------------------------------------
@api_view(['GET'])
@permission_classes([AllowAny]) # [수정3] 이 줄을 꼭 추가하세요! (로그인 없이 조회 허용)
def products_list(request):
    products = Products.objects.all()
    
    # ... (기존 필터링 로직) ...
    bank_name = request.GET.get('bank')
    if bank_name:
        products = products.filter(kor_co_nm__contains=bank_name)
    
    # 터미널 확인용
    print(f"가져온 데이터 개수: {products.count()}")

    serializer = ProductsSerializer(products, many=True)
    return Response(serializer.data)


# ------------------------------------------------
# 상세 조회 (누구나 볼 수 있게 허용)
# ------------------------------------------------
@api_view(['GET'])
@permission_classes([AllowAny]) # 여기도 추가!
def product_detail(request, product_id):
    # ... (기존 상세 조회 로직) ...
    pass


@api_view(['POST'])
@permission_classes([IsAuthenticated]) # 여기서 에러가 났던 것입니다.
def join_product(request, product_id):
    user = request.user
    product = get_object_or_404(Products, pk=product_id)

    # DepositProducts 모델을 통해 가입 여부 확인
    if DepositProducts.objects.filter(user=user, product_id=product_id).exists():
        DepositProducts.objects.filter(user=user, product_id=product_id).delete()
        return Response({'message': '가입 취소', 'is_joined': False})
    else:
        DepositProducts.objects.create(user=user, product_id=product_id)
        return Response({'message': '가입 성공', 'is_joined': True})