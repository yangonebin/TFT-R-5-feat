from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import DepositProducts, DepositOptions
from .serializers import DepositProductsSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def product_list(request):
    """
    F03-2: 예적금 목록 조회 및 은행별 필터링
    """
    bank_name = request.query_params.get('bank')
    
    # 데이터가 하나도 없을 경우를 대비해 쿼리셋 확인
    products = DepositProducts.objects.all()
    
    # '전체'가 들어오거나 값이 없을 때는 필터링 건너뜀
    if bank_name and bank_name != '전체':
        products = products.filter(kor_co_nm__contains=bank_name)
    
    # prefetch_related를 사용하여 속도 최적화 및 500 에러 방지
    serializer = DepositProductsSerializer(products.prefetch_related('options'), many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_product(request, product_cd):
    """
    F03-3: 상품 가입 로직
    """
    # 실제 존재하는 상품인지 먼저 검증 (500 에러 방지)
    get_object_or_404(DepositProducts, fin_prdt_cd=product_cd)
    
    user = request.user
    current_products = user.financial_products or ""
    
    # 리스트 변환 및 중복 체크
    product_list = [p.strip() for p in current_products.split(',')] if current_products else []
    
    if product_cd not in product_list:
        product_list.append(product_cd)
        user.financial_products = ",".join(product_list)
        user.save()
        return Response({"message": "가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)
    
    return Response({"message": "이미 가입된 상품입니다."}, status=status.HTTP_400_BAD_REQUEST)