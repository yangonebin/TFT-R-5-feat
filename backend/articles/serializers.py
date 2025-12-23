from rest_framework import serializers
from .models import Article, Comment

# 댓글 시리얼라이저
class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username') # 작성자 이름 표시

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('article', 'user') # 이 필드들은 유효성 검사 제외

# 게시글 시리얼라이저
class ArticleSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    comments = CommentSerializer(many=True, read_only=True) # 댓글 리스트 포함

    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ('user',)