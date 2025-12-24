import os
import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import mlflow
import mlflow.keras
import tensorflow as tf
from tensorflow.keras import layers, Model, Input
from sklearn.preprocessing import StandardScaler
import time

# --- [ 환경 설정 및 최적화] ---
# 텐서플로우의 로그 수준을 조절하여 불필요한 경고 메시지를 숨김
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# oneDNN 최적화 옵션을 꺼서 연산 순서 차이로 인한 미세한 수치 변동을 방지.
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
# 불필요한 경고를 무시하여 터미널 로그를 깔끔하게 유지
warnings.filterwarnings('ignore')


# --- [1. 데이터 수집] ---

# 1. 데이터 로드 및 전처리
def build_tft_data():
    """삼성전자 주가 데이터를 수집하고 로그 수익률 기반의 5개 피처를 생성합니다."""
    target_stock = "005930.KS"
    # 야후 파이낸스에서 전 기간 데이터를 가져옵니다.
    df = yf.download(target_stock, period="max", auto_adjust=True, progress=False)
    # 멀티인덱스 컬럼을 단순화합니다.
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    # 핵심 5개 피처(시/고/저/종/거)만 선택하고 결측치를 처리합니다.
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].ffill().dropna()
    
    feature_cols = []
    # 주가의 절대 수치보다 '변동 비율'이 학습에 유리하므로 로그 수익률로 변환합니다.
    for col in df.columns:
        new_name = f'Log_Ret_{col}'
        df[new_name] = np.log((df[col] + 1e-9) / (df[col].shift(1) + 1e-9))
        feature_cols.append(new_name)
    
    # [Target 1] 내일의 주가가 오를지(1) 내릴지(0) 판단용 (시뮬레이션용)
    df['target_up'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    # [Target 2] 실제 ROI 계산을 위한 내일의 단순 수익률 (복리 계산용)
    df['actual_ret'] = (df['Close'].shift(-1) / df['Close']) - 1
    df = df.dropna()
    
    # 평균 0, 표준편차 1로 스케일링하여 딥러닝 모델의 학습 효율을 극대화합니다.
    for col in feature_cols:
        df[col] = StandardScaler().fit_transform(df[[col]])
    return df, feature_cols

# 2. 학습용 윈도우 사이즈 변환 (Input데이터 생성완료)
def create_sequences(df, features, window=20):
    """과거 20일치 데이터를 묶어 하나의 학습 단위(Sequence)로 만듭니다."""
    X, y, r = [], [], []
    data, target, ret = df[features].values, df['target_up'].values, df['actual_ret'].values
    for i in range(len(df) - window):
        # 입력 데이터: 20일간의 가격 변동 패턴
        X.append(data[i:i+window])
        # 정답 데이터: 20일째 되는 날 기준 '내일'의 주가 상승 여부
        y.append(target[i+window-1])
        # 수익률 데이터: 실제 자산 시뮬레이션을 위한 수익률 값
        r.append(ret[i+window-1])
    return np.array(X), np.array(y), np.array(r)


# --- [2. TFT 아키텍처 빌드] ---
# 1. model 생성시작

def build_beast_tft(window_size, num_features, units=64):
    """TFT의 어텐션 메커니즘과 순환 신경망을 결합한 모델을 설계합니다."""
    inputs = Input(shape=(window_size, num_features))
    
    # 1. 변수 선택: 5개 피처 중 유의미한 시그널을 동적으로 필터링합니다.
    vsn = variable_selection_network(inputs, units, num_features)
    
    # 2. LSTM: 시계열의 장기/단기 패턴(맥락)을 파악합니다.
    lstm = layers.LSTM(units, return_sequences=True)(vsn)
    lstm = layers.LayerNormalization()(lstm)
    
    # 3. Multi-Head Attention: 과거 한달 중 현재 가격에 가장 큰 영향을 준 날을 찾아냅니다.
    attn = layers.MultiHeadAttention(num_heads=4, key_dim=units)(lstm, lstm)
    # 잔차 연결(Add)을 통해 학습의 안정성을 확보합니다.
    attn = layers.Add()([lstm, attn])
    attn = layers.LayerNormalization()(attn)
    
    # 4. GRN: 최종 출력 전 노이즈를 한 번 더 제거하고 특징을 정제합니다.
    grn = gated_residual_network(attn[:, -1, :], units)
    
    # 5. Output: 내일의 수익률 강도를 예측하는 회귀(Regressor) 노드입니다.
    outputs = layers.Dense(1)(grn) 
    
    model = Model(inputs, outputs)
    # Adam 옵티마이저와 MSE(평균제곱오차) 손실함수를 사용하여 오차를 최소화합니다.
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-4), loss='mse')
    return model


# 2. Input -> VSN 
def variable_selection_network(x, units, num_features):
    """
    VSN 블록: 입력된 피처들 중 현재 예측에 가장 중요한 변수를 동적으로 선택합니다.
    삼성전자의 시/고/저/종/거 중 무엇이 중요한지 모델이 스스로 판단하게 합니다.
    """
    feature_embeddings = []
    # 각 피처(시, 고, 저, 종, 거)를 모델이 이해할 수 있는 고차원 벡터로 변환합니다.
    for i in range(num_features):
        feat = layers.Lambda(lambda x, i=i: x[:, :, i:i+1])(x)
        feature_embeddings.append(layers.Dense(units)(feat))
        
    # 모든 임베딩을 합쳐서 어떤 피처가 중요한지 가중치(Softmax)를 계산합니다.
    combined = layers.Concatenate()(feature_embeddings)
    weights = layers.Dense(num_features, activation='softmax')(combined)
    
    # 피처 벡터와 계산된 가중치를 곱하여 중요한 정보만 강조합니다.
    stacked_features = layers.Lambda(lambda x: tf.stack(x, axis=2))(feature_embeddings)
    expanded_weights = layers.Reshape((-1, num_features, 1))(weights)
    weighted_features = layers.Multiply()([stacked_features, expanded_weights])
    
    # 가중치가 적용된 피처들을 하나로 합쳐 다음 단계로 넘깁니다.
    return layers.Lambda(lambda x: tf.reduce_sum(x, axis=2))(weighted_features)


# 3. VSN -> LSTM -> Attn -> GRN 
def gated_residual_network(x, units, dropout_rate=0.1):
    """
    TFT의 핵심인 GRN 블록: 모델이 복잡한 비선형 관계를 학습하되, 
    필요 없는 경우에는 신호를 그대로 통과시켜 과적합(Overfitting)을 방지.
    """
    # 은닉층을 통해 특징을 추출. activation='elu'는 기울기 소실 방지에 탁월.
    h = layers.Dense(units, activation='elu')(x)
    h = layers.Dense(units)(h)
    h = layers.Dropout(dropout_rate)(h)
    
    # GLU(Gated Linear Unit): 정보의 통과량을 결정하는 '수문' 역할.
    gate = layers.Dense(units, activation='sigmoid')(x)
    # 입력값과 변환된 값을 더해(Skip Connection) 층이 깊어져도 학습이 잘 되게 합니다.
    x = layers.Add()([x, layers.Multiply()([gate, h])])
    return layers.LayerNormalization()(x)


# --- [5. 메인 실행 및 시뮬레이션 루프] ---

if __name__ == "__main__":
    # 데이터 로드 및 시퀀스 생성
    df, features = build_tft_data()
    X, y, r = create_sequences(df, features)
    
    # 8:2 비율로 학습 데이터와 테스트 데이터를 분리합니다.
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    # 타겟(y)은 실제 수익률(r)로 설정하여 회귀 학습을 수행합니다.
    y_train, y_test = r[:split], r[split:] 
    r_test = r[split:]

    # MLflow 실험실 설정
    mlflow.set_experiment("Samsung_SOTA_TFT_5Features_Final")
    
    roi_results, buy_counts = [], []
    
    print(f"\n🚀 [SOTA] TFT 5-Feature 모델 학습 및 검증 시작")
    print("="*60)

    # 결과의 신뢰도를 위해 서로 다른 시드(Seed)로 30회 반복 실험합니다.
    for seed in range(30):
        with mlflow.start_run(run_name=f"TFT_Seed_{seed}"):
            # 난수를 고정하여 실험 결과의 재현성을 확보합니다.
            tf.random.set_seed(seed)
            np.random.seed(seed)
            mlflow.log_param("seed", seed)
            
            # 모델 생성 및 학습
            model = build_beast_tft(X.shape[1], X.shape[2])
            # 과적합 방지를 위한 얼리 스토핑: 검증 손실이 15번 정체되면 멈춥니다.
            es = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)
            
            model.fit(X_train, y_train, validation_data=(X_test, y_test), 
                      epochs=150, batch_size=128, verbose=1, callbacks=[es])
            
            # 테스트 데이터에 대해 주가 수익률 예측을 수행합니다.
            preds = model.predict(X_test, verbose=0).flatten()
            
            # [Backtesting] 1,000만원으로 시작하는 투자 시뮬레이션
            balance = 10000000
            buy_count = 0
            for i in range(len(preds)):
                # 모델이 예측한 내일의 수익률이 조금이라도 플러스(+)라면 매수합니다.
                if preds[i] > 0: 
                    balance *= (1 + r_test[i]) # 실제 결과 반영
                    buy_count += 1
            
            # 최종 투자 수익률(ROI) 계산
            final_roi = ((balance - 10000000) / 10000000) * 100
            roi_results.append(final_roi)
            buy_counts.append(buy_count)
            
            # 결과 지표를 MLflow에 기록합니다.
            mlflow.log_metric("final_roi", final_roi)
            mlflow.log_metric("buy_count", buy_count)
            
            print(f"[{time.strftime('%H:%M:%S')}] Seed {seed:2d} | ROI: {final_roi:8.2f}% | Buy: {buy_count:4d}")

    # --- [6. 최종 성과 보고서 출력] ---
    print("\n" + "="*60)
    print(f"🏆 [TFT SOTA 최종 리포트]")
    print(f" - 30회 평균 ROI: {np.mean(roi_results):.4f}%")
    print(f" - 30회 평균 매매 횟수: {np.mean(buy_counts):.2f}회")
    # 30회 실험 중 가장 높게 터진 최고 수익률을 기록합니다.
    print(f" - 최고 ROI (Seed {np.argmax(roi_results)}): {np.max(roi_results):.2f}%")
    print("="*60)