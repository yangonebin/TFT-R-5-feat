from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status # status 코드 사용 권장
from django.shortcuts import get_object_or_404
from .models import DepositProducts, DepositOptions
from .serializers import DepositProductsSerializer
import pandas as pd
import os
from django.conf import settings



@api_view(['GET'])
@permission_classes([AllowAny])
def product_list(request):
    """
    F03-2: 은행별 필터 기능
    """
    bank_name = request.query_params.get('bank')
    products = DepositProducts.objects.all()
    
    if bank_name and bank_name != 'all': # 프론트엔드 'all' 값 대응
        products = products.filter(kor_co_nm=bank_name)
    
    serializer = DepositProductsSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_product(request, product_cd):
    """
    F03-3: 금융상품 가입 및 중복 체크 로직
    """
    user = request.user
    
    # 1. 기존 가입 목록 가져오기 및 공백 제거
    # None이면 빈 문자열로 처리하고 양 끝 공백을 제거함
    raw_str = (user.financial_products or "").strip()
    
    # 2. 리스트 변환 (매우 중요!)
    # split(',') 후 각 요소의 공백을 제거하고, 빈 문자열이 아닌 것만 리스트에 담음
    joined_list = [p.strip() for p in raw_str.split(',') if p.strip()]
    
    # 3. 중복 체크
    # 이제 리스트에는 실제 상품 코드들만 들어있으므로 정확한 비교가 가능함
    if product_cd in joined_list:
        return Response(
            {"message": "이미 가입된 상품입니다."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 4. 새로운 상품 코드 추가
    joined_list.append(product_cd)
    
    # 5. 다시 콤마로 연결하여 저장
    user.financial_products = ",".join(joined_list)
    user.save()
    
    return Response(
        {"message": "가입이 완료되었습니다.", "joined_list": joined_list}, 
        status=status.HTTP_201_CREATED
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def gold_silver_prices(request):
    asset = request.query_params.get('asset', 'gold').lower()
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    file_name = 'Gold_prices.xlsx' if asset == 'gold' else 'Silver_prices.xlsx'
    file_path = os.path.join(settings.BASE_DIR, 'data', file_name)

    if not os.path.exists(file_path):
        return Response({"error": "파일 없음"}, status=404)

    try:
        # 1. 엑셀 읽기 (헤더가 이상할 수 있으니 넉넉하게 읽음)
        df = pd.read_excel(file_path, engine='openpyxl')

        # 2. 날짜 컬럼 찾기 (대소문자 구분 없이 'date'가 포함된 컬럼 찾기)
        # 엑셀에 'Date', 'date', 'Name' 등이 섞여 있어도 찾을 수 있게 함
        date_col = None
        for col in df.columns:
            if 'date' in str(col).lower():
                date_col = col
                break
        
        # 날짜 컬럼을 못 찾았으면 첫 번째 컬럼을 날짜로 가정
        if not date_col:
            date_col = df.columns[0]

        # 날짜 포맷 통일
        df = df.rename(columns={date_col: 'date'})
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

        # 3. 가격 컬럼 찾기 (가장 중요한 부분!)
        # 날짜가 아닌 컬럼 중에서, 이름에 'USD'가 있거나 'Price'가 있는 것을 우선 선택
        price_col = None
        candidates = [c for c in df.columns if c != 'date']

        # 우선순위 1: 'USD'가 들어간 컬럼 (예: USD (PM))
        for c in candidates:
            if 'USD' in str(c):
                price_col = c
                break
        
        # 우선순위 2: 못 찾았으면 그냥 날짜 뺴고 첫 번째 컬럼 선택
        if not price_col and candidates:
            price_col = candidates[0]

        # 4. 가격 컬럼 이름 통일 및 데이터 정제
        if price_col:
            df = df.rename(columns={price_col: 'price'})
            # 숫자가 아닌 값(결측치 등) 강제 변환 및 제거
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
            df = df.dropna(subset=['price']) # 가격 없는 행 삭제
        else:
             return Response({"error": "가격 데이터를 찾을 수 없습니다."}, status=500)

        # 5. 필요한 컬럼만 선택 및 필터링
        df = df[['date', 'price']]

        if start_date:
            df = df[df['date'] >= start_date]
        if end_date:
            df = df[df['date'] <= end_date]
        
        # 시간순 정렬 (차트가 꼬이지 않게)
        df = df.sort_values('date')

        return Response(df.to_dict(orient='records'))

    except Exception as e:
        print(f"Error processing {asset}: {e}")
        return Response({"error": str(e)}, status=500)