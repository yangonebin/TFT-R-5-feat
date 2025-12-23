from django.db import models
from django.conf import settings  # [필수] 유저 모델을 가져오기 위해 필요

class DepositProducts(models.Model):
    fin_prdt_cd = models.CharField(max_length=100, primary_key=True)
    kor_co_nm = models.CharField(max_length=100)
    fin_prdt_nm = models.CharField(max_length=100)
    etc_note = models.TextField(null=True)
    join_way = models.TextField(null=True)
    spcl_cnd = models.TextField(null=True)
    
    join_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='deposit_products', blank=True)

class DepositOptions(models.Model):
    product = models.ForeignKey(DepositProducts, on_delete=models.CASCADE, related_name='options')
    fin_prdt_cd = models.CharField(max_length=100)
    save_trm = models.IntegerField()
    intr_rate = models.FloatField(null=True)
    intr_rate2 = models.FloatField(null=True)