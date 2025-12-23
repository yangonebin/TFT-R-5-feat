from rest_framework import serializers
from .models import DepositProducts, DepositOptions

class DepositOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositOptions
        fields = ('save_trm', 'intr_rate', 'intr_rate2')

class DepositProductsSerializer(serializers.ModelSerializer):
    # 역참조를 통해 상품에 딸린 금리 옵션들을 가져옴
    options = DepositOptionsSerializer(many=True, read_only=True)

    class Meta:
        model = DepositProducts
        fields = '__all__'
        