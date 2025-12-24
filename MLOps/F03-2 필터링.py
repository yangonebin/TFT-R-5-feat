import sqlite3
import pandas as pd

DB_NAME = "service_data.db"

# [핵심] 판다스 출력 옵션 설정: 행(row)과 열(column)을 생략 없이 모두 표시
pd.set_option('display.max_rows', None)  # 모든 행 출력
pd.set_option('display.max_columns', None)  # 모든 열 출력
pd.set_option('display.width', None)  # 줄바꿈 없이 한 줄에 출력

def get_bank_list():
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT DISTINCT kor_co_nm FROM products"
    banks = pd.read_sql(query, conn)
    conn.close()
    return banks['kor_co_nm'].tolist()

def search_products(bank_name):
    conn = sqlite3.connect(DB_NAME)
    # LIKE 절을 사용하여 유연한 검색 지원
    query = "SELECT fin_prdt_nm, kor_co_nm, intr_rate, save_trm FROM products WHERE kor_co_nm LIKE ?"
    df = pd.read_sql(query, conn, params=(f'%{bank_name}%',))
    conn.close()
    return df

if __name__ == "__main__":
    print("="*60)
    print("🏦 금융상품 은행별 전체 목록 조회 서비스")
    print("="*60)
    
    # 1. 가능한 은행 목록 안내
    banks = get_bank_list()
    print(f"📍 현재 조회 가능한 은행 리스트:\n{', '.join(banks)}")
    print("-" * 60)
    
    # 2. 사용자 입력 받기
    user_input = input("🔍 조회하고 싶은 은행 이름을 입력하세요: ")
    
    # 3. 결과 전체 출력
    result = search_products(user_input)
    
    if not result.empty:
        print(f"\n✅ '{user_input}' 검색 결과 (총 {len(result)}건 전부 표시):")
        # .head()를 빼고 전체를 출력합니다.
        print(result)
    else:
        print(f"\n❌ '{user_input}'에 해당하는 데이터가 없습니다.")
    
    print("=" * 60)