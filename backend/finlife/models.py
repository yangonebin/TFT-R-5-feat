from django.db import models

# 여기에는 User 모델이 있으면 안 됩니다. 아래 상품 모델만 남기세요.
class DepositProducts(models.Model):
    fin_prdt_cd = models.CharField(max_length=100, primary_key=True)
    kor_co_nm = models.CharField(max_length=100)
    fin_prdt_nm = models.CharField(max_length=100)
    etc_note = models.TextField(null=True)
    join_way = models.TextField(null=True)
    spcl_cnd = models.TextField(null=True)

class DepositOptions(models.Model):
    product = models.ForeignKey(DepositProducts, on_delete=models.CASCADE, related_name='options')
    fin_prdt_cd = models.CharField(max_length=100)
    save_trm = models.IntegerField()
    intr_rate = models.FloatField(null=True)
    intr_rate2 = models.FloatField(null=True)