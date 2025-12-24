import mlflow
from mlflow.tracking import MlflowClient

# 1. 소스(DB)와 목적지(폴더) 설정
source_uri = "sqlite:///mlflow.db"
dest_uri = "file:./mlruns_recovered"

client_source = MlflowClient(tracking_uri=source_uri)
mlflow.set_tracking_uri(dest_uri)

# 2. 모든 실험 가져오기
experiments = client_source.search_experiments()

print(f"🚀 마이그레이션 시작: {len(experiments)}개의 실험 발견")

for exp in experiments:
    # 목적지에 동일한 이름의 실험 생성
    try:
        new_exp_id = mlflow.create_experiment(exp.name)
    except:
        new_exp_id = mlflow.get_experiment_by_name(exp.name).experiment_id
    
    runs = client_source.search_runs(experiment_ids=[exp.experiment_id])
    print(f"📦 실험 '{exp.name}'에서 {len(runs)}개의 실행 데이터를 옮기는 중...")

    for run in runs:
        # 목적지에 데이터 기록
        with mlflow.start_run(experiment_id=new_exp_id, run_name=run.info.run_name):
            # 파라미터 복사
            if run.data.params:
                mlflow.log_params(run.data.params)
            
            # 메트릭 복사
            if run.data.metrics:
                mlflow.log_metrics(run.data.metrics)
            
            # [수정] log_tags 대신 set_tags 사용
            if run.data.tags:
                mlflow.set_tags(run.data.tags)

print("\n✅ 마이그레이션 완료! 'mlruns_recovered' 폴더를 확인하세요.")