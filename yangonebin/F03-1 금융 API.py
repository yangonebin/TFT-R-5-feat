import pandas as pd
import sqlite3
import requests

# 설정
FSS_API_KEY = "2fa1b84249e34622ee6cd8fa16c7d6fd"
SERVICE_DB = "service_data.db"

def build_service_db():
    print(f"🚀 [Service] {SERVICE_DB} 실제 데이터 수집 시도...")
    
    # 수정 포인트: https 적용 및 get 제거 (표준 경로로 수정)
    url = f"https://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json"
    
    params = {
        'auth': FSS_API_KEY,
        'topFinGrpNo': '020000', # 권역 코드: 은행
        'pageNo': '1'
    }
    
    # 1. API 호출
    response = requests.get(url, params=params)
    
    # 404나 500 에러 발생 시 즉시 중단 및 에러 출력
    if response.status_code != 200:
        print(f"❌ 호출 실패! URL 확인 필요 (Status: {response.status_code})")
        print(f"시도한 URL: {response.url}")
        return

    # 2. 데이터 파싱
    data = response.json()
    
    # 금감원 API 특유의 에러 메시지 처리 (예: 유효하지 않은 키 등)
    if 'result' not in data or data['result'].get('err_cd') != '000':
        err_msg = data.get('result', {}).get('err_msg', '알 수 없는 에러')
        print(f"❌ 금감원 API 에러 응답: {err_msg}")
        return

    # 3. 데이터 정제 및 DB 저장
    base = pd.DataFrame(data['result']['baseList'])
    opt = pd.DataFrame(data['result']['optionList'])
    
    # 상품 정보를 기준으로 병합 (F03 요구사항 대응)
    df_products = pd.merge(base, opt, on='fin_prdt_cd')
    
    # 팀원들이 필요로 하는 핵심 컬럼만 추출
    product_list = df_products[['fin_prdt_nm', 'kor_co_nm', 'intr_rate', 'intr_rate2', 'save_trm']]
    
    # SQLite3 저장
    conn = sqlite3.connect(SERVICE_DB)
    product_list.to_sql("products", conn, if_exists='replace', index=False)
    conn.close()
    
    print(f"✅ {SERVICE_DB} 실제 데이터로 생성 완료! (수집된 상품 수: {len(product_list)})")

if __name__ == "__main__":
    build_service_db()  