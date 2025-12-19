import yfinance as yf
import pandas as pd
import sqlite3
import os

# 설정
SPOT_DB = "spot_data.db"

def build_spot_visualization_db():
    print(f"🚀 [F04] {SPOT_DB} 구축 시작 (금/은 시각화 전용)...")
    
    # 1. 데이터 수집 (금: GC=F, 은: SI=F)
    symbols = {"Gold": "GC=F", "Silver": "SI=F"}
    spot_frames = []

    for name, sym in symbols.items():
        print(f"📡 {name} 데이터 다운로드 중...")
        raw = yf.download(sym, start="2005-01-01", end="2025-12-19")
        
        # Multi-index 처리
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
            
        temp_df = raw[['Close']].copy()
        temp_df.columns = [name]
        spot_frames.append(temp_df)

    # 2. 데이터 통합 (날짜 기준)
    df_final = pd.concat(spot_frames, axis=1).ffill().dropna()
    df_final.reset_index(inplace=True) # Date를 컬럼으로 변환
    
    # 3. 새로운 DB에 저장
    conn = sqlite3.connect(SPOT_DB)
    df_final.to_sql("spot_prices", conn, if_exists='replace', index=False)
    conn.close()
    
    print(f"✅ {SPOT_DB} 생성 완료! (테이블명: spot_prices)")

if __name__ == "__main__":
    build_spot_visualization_db()