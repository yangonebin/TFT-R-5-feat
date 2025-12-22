# finlife/models.py
from django.db import models
from django.conf import settings # User 모델 참조용

# 기존 Products 모델 (그대로 유지)
class Products(models.Model):
    id = models.IntegerField(primary_key=True, db_column='rowid')
    fin_prdt_nm = models.TextField(blank=True, null=True)
    kor_co_nm = models.TextField(blank=True, null=True)
    intr_rate = models.FloatField(blank=True, null=True)
    intr_rate2 = models.FloatField(blank=True, null=True)
    save_trm = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'products'

class DepositProducts(models.Model):
    # 1. 누가 가입했는지 (User와 연결)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # 2. 어떤 상품인지 (ForeignKey 대신 '숫자 ID'만 저장!)
    # 이렇게 하면 DB 충돌 없이 연결할 수 있습니다.
    product_id = models.IntegerField() 
    
    # 3. 언제 가입했는지
    join_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 한 유저가 같은 상품 중복 가입 방지
        unique_together = ('user', 'product_id')