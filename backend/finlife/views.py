from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .models import DepositProducts, DepositOptions
from .serializers import DepositProductsSerializer, DepositOptionsSerializer
from django.conf import settings
import requests
import pandas as pd
import os

# ==========================================
# 0. [필수] 데이터 저장 기능 (이게 없어서 목록이 비어있던 겁니다!)
# ==========================================
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def save_deposit_products(request):
    # API 키 확인 (settings.py에 FINLIFE_API_KEY가 있어야 함, 없으면 직접 입력)
    api_key = getattr(settings, 'FINLIFE_API_KEY', '여기에_API_KEY_직접입력가능') 
    
    url = f'http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json?auth={api_key}&topFinGrpNo=020000&pageNo=1'
    
    try:
        response = requests.get(url).json()
        baseList = response.get('result').get('baseList')
        optionList = response.get('result').get('optionList')

        # 1. 상품 기본 정보 저장
        for product in baseList:
            save_data = {
                'fin_prdt_cd': product.get('fin_prdt_cd'),
                'kor_co_nm': product.get('kor_co_nm'),
                'fin_prdt_nm': product.get('fin_prdt_nm'),
                'etc_note': product.get('etc_note'),
                'join_way': product.get('join_way'),
                'spcl_cnd': product.get('spcl_cnd'),
            }
            serializer = DepositProductsSerializer(data=save_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

        # 2. 상품 옵션 정보 저장
        for option in optionList:
            prdt_cd = option.get('fin_prdt_cd')
            product = DepositProducts.objects.get(fin_prdt_cd=prdt_cd)
            
            save_data = {
                'fin_prdt_cd': prdt_cd,
                'intr_rate_type_nm': option.get('intr_rate_type_nm'),
                'intr_rate': option.get('intr_rate') if option.get('intr_rate') else -1,
                'intr_rate2': option.get('intr_rate2') if option.get('intr_rate2') else -1,
                'save_trm': option.get('save_trm'),
            }
            
            # 이미 있는지 확인 후 저장
            if not DepositOptions.objects.filter(fin_prdt_cd=prdt_cd, save_trm=option.get('save_trm')).exists():
                serializer = DepositOptionsSerializer(data=save_data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save(product=product)

        return Response({'message': '데이터 저장 성공!'}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==========================================
# 1. 정기 예금 상품 관련 (목록, 상세, 가입)
# ==========================================

# [목록 조회]
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def product_list(request):
    bank_name = request.query_params.get('bank')
    products = DepositProducts.objects.all()
    
    if bank_name and bank_name != 'all': 
        products = products.filter(kor_co_nm=bank_name)
    
    serializer = DepositProductsSerializer(products, many=True)
    return Response(serializer.data)


# [상세 조회] - 상세 페이지 연결용
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def deposit_product_detail(request, fin_prdt_cd):
    product = get_object_or_404(DepositProducts, fin_prdt_cd=fin_prdt_cd)
    serializer = DepositProductsSerializer(product)
    return Response(serializer.data)


# [상품 가입]
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_product(request, product_cd):
    product = get_object_or_404(DepositProducts, fin_prdt_cd=product_cd)
    
    if product.join_users.filter(pk=request.user.pk).exists():
        return Response({'message': '이미 가입된 상품입니다.'}, status=status.HTTP_400_BAD_REQUEST)
    
    product.join_users.add(request.user)
    return Response({'message': '상품 가입이 완료되었습니다.'}, status=status.HTTP_201_CREATED)


# ==========================================
# 2. 금/은 시세 관련
# ==========================================
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def gold_silver_prices(request):
    asset = request.query_params.get('asset', 'gold').lower()
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    file_name = 'Gold_prices.xlsx' if asset == 'gold' else 'Silver_prices.xlsx'
    # 보내주신 사진에 따라 'Gold' 폴더로 지정
    file_path = os.path.join(settings.BASE_DIR, 'Gold', file_name)

    if not os.path.exists(file_path):
        return Response({"error": f"파일 없음: {file_path}"}, status=404)

    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # 날짜 컬럼 찾기
        date_col = next((col for col in df.columns if 'date' in str(col).lower()), df.columns[0])
        df = df.rename(columns={date_col: 'date'})
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

        # 가격 컬럼 찾기
        price_col = next((c for c in df.columns if c != 'date' and 'USD' in str(c)), None)
        if not price_col:
             # USD가 없으면 두번째 컬럼을 가격으로
             price_col = df.columns[1] if len(df.columns) > 1 else None
        
        if price_col:
            df = df.rename(columns={price_col: 'price'})
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
            df = df.dropna(subset=['price'])
            
        df = df[['date', 'price']].sort_values('date')

        if start_date: df = df[df['date'] >= start_date]
        if end_date: df = df[df['date'] <= end_date]
        
        return Response(df.to_dict(orient='records'))

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_joined_products(request):
    # models.py에서 related_name='deposit_products'로 설정했으므로 이렇게 접근 가능
    products = request.user.deposit_products.all()
    serializer = UserJoinedProductSerializer(products, many=True)
    return Response(serializer.data)    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_joined_products(request):
    # 현재 로그인한 유저가 가입한 상품들만 가져옴
    products = request.user.deposit_products.all()
    serializer = DepositProductsSerializer(products, many=True)
    return Response(serializer.data)