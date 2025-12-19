import yfinance as yf
import pandas as pd

def build_data_mart():
    print("🚀 [Step 1] 상장일부터 현재까지 원천 데이터 수집 시작...")
    
    target_stock = "005930.KS"  # 삼성전자
    macro_symbols = {
        "USD_KRW": "KRW=X", 
        "Gold": "GC=F", 
        "Interest_Rate": "^TNX"
    }

    # 1. 주가 데이터 다운로드 (period="max" 적용)
    # start/end 대신 period="max"를 사용하여 상장일부터 전 기간 수집
    df_raw = yf.download(target_stock, period="max")
    
    if isinstance(df_raw.columns, pd.MultiIndex):
        df_raw.columns = df_raw.columns.get_level_values(0)
    
    # 상장일 확인 로그 (선택 사항)
    first_date = df_raw.index[0].strftime('%Y-%m-%d')
    print(f"📡 {target_stock} 상장일({first_date})부터 데이터를 수집했습니다.")

    df = df_raw[['Open', 'High', 'Low', 'Close', 'Volume']].copy()

    # 2. 거시 경제 데이터 통합 (주가 데이터 기간에 맞춤)
    for name, symbol in macro_symbols.items():
        # 거시 데이터도 가급적 max로 가져온 뒤 주가 데이터와 Join
        macro_raw = yf.download(symbol, period="max")
        
        if isinstance(macro_raw.columns, pd.MultiIndex):
            macro_raw.columns = macro_raw.columns.get_level_values(0)
            
        df[name] = macro_raw['Close']

    # 결측치 처리 (최신 문법 반영)
    df = df.ffill()

    print("🚀 [Step 2] 일목균형표 피처 엔지니어링 시작...")

    # 전환선 (Tenkan-sen): (9일간 최고가 + 9일간 최저가) / 2
    nine_high = df['High'].rolling(window=9).max()
    nine_low = df['Low'].rolling(window=9).min()
    df['tenkan_sen'] = (nine_high + nine_low) / 2

    # 기준선 (Kijun-sen): (26일간 최고가 + 26일간 최저가) / 2
    twenty_six_high = df['High'].rolling(window=26).max()
    twenty_six_low = df['Low'].rolling(window=26).min()
    df['kijun_sen'] = (twenty_six_high + twenty_six_low) / 2

    # 선행스팬 A: (전환선 + 기준선) / 2 -> 26일 뒤로 보냄
    # 모델이 오늘 시점에서 '미래의 구름대'를 참조하기 위해 shift(26)
    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)

    # 선행스팬 B: (52일간 최고가 + 52일간 최저가) / 2 -> 26일 뒤로 보냄
    fifty_two_high = df['High'].rolling(window=52).max()
    fifty_two_low = df['Low'].rolling(window=52).min()
    df['senkou_span_b'] = ((fifty_two_high + fifty_two_low) / 2).shift(26)

    # 3. 파생 변수 (비즈니스 로직)
    df['cloud_thickness'] = df['senkou_span_a'] - df['senkou_span_b']
    df['dist_from_kijun'] = df['Close'] - df['kijun_sen']

    # 4. Target(정답지) 생성: 내일 종가가 오늘보다 오르면 1, 아니면 0
    # shift(-1)을 사용하여 미래 데이터를 오늘 행으로 가져옴
    df['target'] = (df['Close'].shift(-1) > df['Close']).astype(int)

    # 결측치가 있는 행(초반 52일치) 제거 후 저장
    final_mart = df.dropna()
    final_mart.to_csv("final_data_mart.csv")
    
    print(f"✅ 데이터 마트 생성 완료! 총 {len(final_mart)}개의 학습 데이터가 준비되었습니다.")
    return final_mart

if __name__ == "__main__":
    build_data_mart()