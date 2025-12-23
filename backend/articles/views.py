from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Article, Comment
from .serializers import ArticleSerializer, CommentSerializer

# 1. 게시글 목록 조회 및 생성
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly]) # 조회는 누구나, 작성은 로그인 필요
def article_list(request):
    if request.method == 'GET':
        articles = Article.objects.order_by('-pk')
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user) # 작성자 자동 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)

# 2. 게시글 상세 조회, 수정, 삭제
@api_view(['GET', 'DELETE', 'PUT'])
@permission_classes([IsAuthenticatedOrReadOnly])
def article_detail(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)

    if request.method == 'GET':
        serializer = ArticleSerializer(article)
        return Response(serializer.data)
    
    # 수정/삭제는 작성자만 가능
    if request.user != article.user:
        return Response({'message': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'DELETE':
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'PUT':
        serializer = ArticleSerializer(article, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

# 3. 댓글 생성
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_create(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(article=article, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def comment_delete(request, article_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user == comment.user:
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response({'message': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)