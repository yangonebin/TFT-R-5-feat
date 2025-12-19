from django.db import models

class Product(models.Model):
    fin_prdt_nm = models.TextField(unique=True)
    kor_co_nm = models.TextField()   
    intr_rate = models.FloatField(null=True) 
    intr_rate2 = models.FloatField(null=True) 
    save_trm = models.TextField()    
    
    class Meta:
        db_table = 'products'
        app_label = 'finlife'