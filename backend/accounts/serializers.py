from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'nickname', 'financial_products')
        read_only_fields = ('username',)