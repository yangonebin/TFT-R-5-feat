import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "spot_data.db")

def get_visual_data(item="Gold", days=90):
    # 입력값의 첫 글자를 대문자로 변환 (gold -> Gold)
    item = item.capitalize() 
    
    conn = sqlite3.connect(DB_PATH)
    
    # 데이터 기준일로부터 기간 계산
    end_date = datetime.now() 
    start_date = end_date - timedelta(days=days)
    
    query = f"""
    SELECT Date, {item}
    FROM spot_prices 
    WHERE Date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
    ORDER BY Date ASC
    """
    
    try:
        df = pd.read_sql(query, conn)
    except Exception as e:
        print(f"❌ 조회 에러: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

if __name__ == "__main__":
    print("📈 F04 현물 시세 시각화 전용 서비스")
    
    # DB 존재 여부 체크
    if not os.path.exists(DB_PATH):
        print("❌ DB 파일이 없습니다. 빌드 스크립트를 먼저 실행하세요!")
    else:
        target = input("💎 조회할 자산 (Gold/Silver): ").strip()
        period = int(input("📅 조회 기간 (일): "))
        
        result = get_visual_data(target, period)
        
        if not result.empty:
            pd.set_option('display.max_rows', None)
            print(f"\n✨ [{target.capitalize()}] 최근 {period}일 전체 데이터:")
            print(result)
        else:
            print("❌ 데이터를 찾을 수 없습니다. 자산명이나 기간을 확인하세요.")