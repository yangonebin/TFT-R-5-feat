import yfinance as yf
import pandas as pd
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)

def build_data_mart():
    print("="*50)
    print(" [Step 1] 데이터 수집 및 마트 구축 시작...")
    print("="*50)
    
    target_stock = "005930.KS"  # 삼성전자 코드
    # 거시경제 지표를 딕셔너리에 담음.
    macro_symbols = { 
        "USD_KRW": "KRW=X", # 원/달러 환율
        "Gold": "GC=F", # 금 선물 가격
        "Interest_Rate": "^TNX" # 미국 10년 만기 국채 수익률
    }

    # AI가 학습할 때, 단순한 종가 정보뿐만 아니라 {환율, 금, 금리}가 이럴 때 종가가 어떻더라. 거시경제 피쳐를 추가하고자 했음.  

    # 1. 주가 데이터 다운로드 (period="max" 적용)
    # start/end 대신 period="max"를 사용하여 상장일부터 전 기간 수집
    # 하지만 온전한 상장일로부터 데이터를 제공받지 못하고 대한민국 주가 정보들은 yfinace에서 주로 2000년 초반부터 제공해줌. 하지만 5000거래일 이상이라 충분할 것이라 판단함. 
    # atuo_adjust는 액면분할이나 배당락 보정
    # progress는 yfinace의 진행상태 터미널에 표시 
    df_raw = yf.download(target_stock, period="max", auto_adjust=True, progress=False)

    # yfinace는 MultiIndex이기 때문에 level이 0인 값만 출력
    # 예 : (Level 0) | Date | Adj Close | Close | High | Low | Open | Volume | 
    #      (Level 1) | 005930.KS | 005930.KS | 005930.KS | 005930.KS | 005930.KS | 005930.KS |  <- 이 부분을 제거하고자 함.
    #      (value)   | 2024-12-18 | 55000 | 55000 | 55500 | 54000 | 54500 | 15000000 |
    if isinstance(df_raw.columns, pd.MultiIndex):
        df_raw.columns = df_raw.columns.get_level_values(0)
    
    # 상장일 확인 로그
    first_date = df_raw.index[0].strftime('%Y-%m-%d')
    print(f"({first_date})부터 데이터를 수집했습니다.")

    # 깊은 복사 True가 defalut임
    df = df_raw[['Open', 'High', 'Low', 'Close', 'Volume']].copy()

    # 2. 거시 경제 데이터 통합 (주가 데이터 기간에 맞춤)
    for name, symbol in macro_symbols.items():
        print(f"📡 {name} 데이터 수집 중...")
        # 거시 데이터도 가급적 max로 가져온 뒤 주가 데이터와 Join
        macro_raw = yf.download(symbol, period="max", auto_adjust=True, progress=False)
        
        if isinstance(macro_raw.columns, pd.MultiIndex):
            macro_raw.columns = macro_raw.columns.get_level_values(0)
            
        df[name] = macro_raw['Close']

    # 결측치 처리 (앞날의 데이터를 가져오는게 합리적이라 판단)
    df = df.ffill()

    print("="*50)
    print(" [Step 2] 일목균형표 피처 엔지니어링 시작...")
    print("="*50)

    # 전환선 (Tenkan-sen): (9일간 최고가 + 9일간 최저가) / 2
    # rolling은 슬라이딩 윈도우 기법
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
    # 구름대 두께 : 지금 벽이 얼마나 두꺼운지!
    df['cloud_thickness'] = df['senkou_span_a'] - df['senkou_span_b']
    # 기준선 이격도 : 현재 과매수/과매도 상태인가? 
    df['dist_from_kijun'] = df['Close'] - df['kijun_sen']

    # 4. Target(정답지) 생성: 회귀(Regression) 모델을 위한 다중 타겟 설정
    
    # [Target 1] 내일의 실제 종가 (Price Regression용)
    # shift(-1)을 사용하여 내일의 종가를 오늘 행으로 가져옴.
    df['target_price'] = df['Close'].shift(-1)

    # [Target 2] 내일의 등락률 (Return Regression용)
    # (내일 종가 / 오늘 종가) - 1 공식을 사용하여 변동 비율을 계산
    # 예: 오늘 100원 -> 내일 105원인 경우 0.05 (5%)가 기록됨
    df['target_return'] = (df['Close'].shift(-1) / df['Close']) - 1

    # 결측치가 있는 행(초반 52일치 및 타겟값이 없는 마지막 행) 제거 후 저장
    final_mart = df.dropna()
    final_mart.to_csv("samsung.csv")
    
    print(f"데이터 마트 생성 완료! 총 {len(final_mart)}개의 학습 데이터가 준비되었습니다.")
    return final_mart

if __name__ == "__main__":
    build_data_mart()



    # 회고 포인트  
    # 일목균형표를 만든 '이치모쿠 산진'은 시장의 주기를 연구하여 9, 26, 52라는 숫자의 의미 
    # 과거 일본 주식 시장은 토요일에도 열렸기 때문에, 26일은 대략 일요일을 제외한 한 달의 영업일을 의미합니다. 
    # 즉, "한 달 전의 에너지가 한 달 뒤의 주가에 영향을 미친다"는 철학이 담겨 있습니다.
    # 하지만 한국 시장은 5영업일이 기준이기 때문에 더욱 적합한 숫자가 있을 것으로 기대
    # 추후, 파라미터 실험을 통해 더욱 정교한 모델을 만들기로 다짐