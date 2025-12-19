import yfinance as yf
import pandas as pd
import sqlite3
import requests
import json

# 설정
FSS_API_KEY = "2fa1b84249e34622ee6cd8fa16c7d6fd"
TRAIN_DB = "stock_training.db"

def build_stock_db():
    print(f" [AI] {TRAIN_DB} 구축 시작...")
    target = "005930.KS"
    df_raw = yf.download(target, start="2005-01-01", end="2024-12-19")
    if isinstance(df_raw.columns, pd.MultiIndex):
        df_raw.columns = df_raw.columns.get_level_values(0)
    df = df_raw[['High', 'Low', 'Close', 'Volume']].copy()
    df['tenkan_sen'] = (df['High'].rolling(9).max() + df['Low'].rolling(9).min()) / 2
    df['kijun_sen'] = (df['High'].rolling(26).max() + df['Low'].rolling(26).min()) / 2
    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
    df['senkou_span_b'] = ((df['High'].rolling(52).max() + df['Low'].rolling(52).min()) / 2).shift(26)
    df['target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    df_mart = df.dropna()
    conn = sqlite3.connect(TRAIN_DB)
    df_mart.to_sql("training_set", conn, if_exists='replace', index=True)
    conn.close()
    print(f"✅ {TRAIN_DB} 생성 완료!")

if __name__ == "__main__":
    build_stock_db()
    print("\n✨ 작업이 마무리되었습니다. 에러 메시지를 확인해 주세요!")