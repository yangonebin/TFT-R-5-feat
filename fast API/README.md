# 주가 예측 서비스

1. pip install -r requirements.txt
2. yangonebin 폴더의 17. fianl TFT-R 5 feat.py 실행
3. 상위 디렉토리에 beast_scaler.pkl, beast_scaler.pkl 생성 확인
4. fast API.py 실행
5. http://127.0.0.1:8000/predict 접속
6. 결과 확인 (예: {"status":"success","result":{"predicted_return":"0.8843%","signal":"BUY"},"meta":{"timestamp":"2025-12-24 11:42:14"}})


