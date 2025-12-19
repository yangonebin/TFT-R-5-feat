import yfinance as yf
import pandas as pd
import sqlite3
import os

# 파일 경로 설정 (경로 꼬임 방지)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPOT_DB = os.path.join(BASE_DIR, "spot_data.db")

def build_spot_visualization_db():
    print(f"🚀 [F04] {SPOT_DB} 데이터 자동 구축 시작...")
    
    # 1. 데이터 수집 (금: GC=F, 은: SI=F)
    symbols = {"Gold": "GC=F", "Silver": "SI=F"}
    spot_frames = []

    for name, sym in symbols.items():
        print(f"📡 {name} 데이터 수집 중 (기간: 전체 이력)...")
        # [수정] period="max"를 사용하여 오늘까지의 모든 데이터를 가져옴
        raw = yf.download(sym, period="max")
        
        # Multi-index 처리 (yfinance 최신 버전 대응)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
            
        temp_df = raw[['Close']].copy()
        temp_df.columns = [name]
        spot_frames.append(temp_df)

    # 2. 데이터 통합 및 정제
    print("🧹 데이터 병합 및 결측치 처리 중...")
    df_final = pd.concat(spot_frames, axis=1).ffill().dropna()
    df_final.reset_index(inplace=True) 
    
    # 3. SQLite3 DB 저장
    conn = sqlite3.connect(SPOT_DB)
    df_final.to_sql("spot_prices", conn, if_exists='replace', index=False)
    conn.close()
    
    first_date = df_final['Date'].iloc[0].strftime('%Y-%m-%d')
    last_date = df_final['Date'].iloc[-1].strftime('%Y-%m-%d')
    print(f"✅ {SPOT_DB} 구축 완료!")
    print(f"📅 데이터 기간: {first_date} ~ {last_date} (총 {len(df_final)}거래일)")

if __name__ == "__main__":
    build_spot_visualization_db()