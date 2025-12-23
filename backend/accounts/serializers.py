# backend/accounts/serializers.py
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
    nickname = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(required=False, allow_blank=True)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['nickname'] = self.validated_data.get('nickname', '')
        data['email'] = self.validated_data.get('email', '')
        return data

class CustomUserDetailSerializer(UserDetailsSerializer):
    class Meta:
        model = User
        fields = ('pk', 'username', 'nickname',)
        read_only_fields = ('username', )