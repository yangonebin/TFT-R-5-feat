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

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        # 여기에 수정하고 싶은 필드를 반드시 명시해야 합니다.
        fields = ('username', 'email', 'first_name', 'last_name',)
        # username은 보통 수정을 막으므로 읽기 전용으로 둡니다.
        read_only_fields = ('username', )