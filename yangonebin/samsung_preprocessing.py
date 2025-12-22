import os
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# ---------------------------------------------------------
# [핵심] 로그 수익률 변환 함수
# ---------------------------------------------------------
def get_log_return(series):
    # np.log(현재가 / 어제가) = 로그 수익률
    # 가격 레벨을 제거하고 '변화율'만 남김
    return np.log(series / series.shift(1))

def build_clean_data():
    print("="*50)
    print(" 🧹 데이터 전처리 리뉴얼 (Price -> Log Return) 시작")
    print("="*50)
    
    target_stock = "005930.KS"
    macro_symbols = { 
        "USD_KRW": "KRW=X", 
        "Gold": "GC=F", 
        "Interest_Rate": "^TNX" 
    }

    # 1. 원본 데이터 다운로드
    print("1. 데이터 다운로드 중...")
    df = yf.download(target_stock, period="max", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # 거시경제 지표 병합
    for name, symbol in macro_symbols.items():
        macro = yf.download(symbol, period="max", auto_adjust=True, progress=False)
        if isinstance(macro.columns, pd.MultiIndex):
            macro.columns = macro.columns.get_level_values(0)
        df[name] = macro['Close']
    
    df = df.ffill()

    # ---------------------------------------------------------
    # 2. [전처리 핵심] 절대 가격을 모두 '변화율'로 변경
    # ---------------------------------------------------------
    print("2. 비정상(Non-stationary) 데이터를 정상(Stationary) 데이터로 변환 중...")
    
    # (1) 주가 OHLC -> 로그 수익률로 변환
    # Close가 80,000원이든 5,000원이든, 1% 오르면 똑같이 0.01이 됨
    df['Log_Return_Close'] = get_log_return(df['Close'])
    df['Log_Return_Open'] = get_log_return(df['Open'])
    df['Log_Return_High'] = get_log_return(df['High'])
    df['Log_Return_Low'] = get_log_return(df['Low'])
    df['Log_Return_Volume'] = get_log_return(df['Volume'].replace(0, 1)) # 0 나누기 방지

    # (2) 거시경제 지표도 변화율로 변환 (환율이 1000원이냐 1400원이냐보다, 변화가 중요)
    df['Log_Return_USD'] = get_log_return(df['USD_KRW'])
    df['Log_Return_Gold'] = get_log_return(df['Gold'])
    df['Log_Return_Rate'] = get_log_return(df['Interest_Rate'])

    # (3) 기술적 지표 (이격도 등은 이미 비율이므로 유지하거나 스케일링만 하면 됨)
    # 다만, 이동평균선 자체(가격)는 의미가 없으므로 '이동평균선 대비 이격률'로 변경해야 함
    
    # 예: 일목균형표 전환선(가격) -> 종가 대비 전환선 비율(%)
    nine_high = df['High'].rolling(window=9).max()
    nine_low = df['Low'].rolling(window=9).min()
    tenkan_sen = (nine_high + nine_low) / 2
    df['Tenkan_Ratio'] = (df['Close'] - tenkan_sen) / tenkan_sen # 전환선 대비 얼마나 떨어져 있나

    twenty_six_high = df['High'].rolling(window=26).max()
    twenty_six_low = df['Low'].rolling(window=26).min()
    kijun_sen = (twenty_six_high + twenty_six_low) / 2
    df['Kijun_Ratio'] = (df['Close'] - kijun_sen) / kijun_sen # 기준선 대비 이격률

    # (4) 불필요한 '절대 가격' 컬럼 삭제 (이제 AI는 8만전자인지 모르게 함)
    drop_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 
                 'USD_KRW', 'Gold', 'Interest_Rate']
    df_clean = df.drop(columns=drop_cols).dropna()

    # ---------------------------------------------------------
    # 3. 데이터 시각화 (Before & After 비교)
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 6))
    
    plt.subplot(2, 1, 1)
    plt.title("Before: Close Price (Non-Stationary)")
    plt.plot(df['Close'], color='red')
    plt.grid(True)
    
    plt.subplot(2, 1, 2)
    plt.title("After: Log Return (Stationary)")
    plt.plot(df_clean['Log_Return_Close'], color='blue')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    print(f"3. 전처리 완료! 데이터 개수: {len(df_clean)}일")
    print("   ㄴ 이제 데이터는 0을 기준으로 진동하는 파동 형태가 되었습니다.")
    
    # 파일 저장
    df_clean.to_csv("samsung_clean_stationary.csv")
    return df_clean

if __name__ == "__main__":
    df_clean = build_clean_data()
    print(df_clean.head())
    print("\n[Check] 'Close' 같은 가격 컬럼이 없어야 합니다. 오직 비율(Ratio/Return)만 존재해야 합니다.")