#!/usr/bin/env python3
"""Django Web Framework - Quick Start Guide"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import path
from django.views.generic import ListView, DetailView


class Article(models.Model):
    """Blog article model."""
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def summary(self):
        return self.content[:100] + "..."


class Comment(models.Model):
    """Comment model for articles."""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"


# URLs
urlpatterns = [
    path('articles/', ListView.as_view(model=Article)),
    path('articles/<int:pk>/', DetailView.as_view(model=Article)),
]

# Views
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse


def article_list(request):
    """List all published articles."""
    articles = Article.objects.filter(published=True)
    data = [
        {
            'id': a.id,
            'title': a.title,
            'author': a.author.username,
            'created_at': a.created_at.isoformat(),
        }
        for a in articles
    ]
    return JsonResponse({'articles': data})


def article_detail(request, pk):
    """Get article detail with comments."""
    article = get_object_or_404(Article, pk=pk)
    comments = article.comments.all()
    
    data = {
        'id': article.id,
        'title': article.title,
        'content': article.content,
        'author': article.author.username,
        'comments': [
            {'user': c.user.username, 'text': c.text}
            for c in comments
        ]
    }
    return JsonResponse(data)


# Serializers (Django REST Framework style)
from rest_framework import serializers

class ArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author_name', 'created_at', 'published']
        read_only_fields = ['created_at']


# Signals
from django.db.models.signals post_save
from django.dispatch import receiver

@receiver(post_save, sender=Article)
def notify_subscribers(sender, instance, created, **kwargs):
    """Send notification when new article is published."""
    if created and instance.published:
        # Send email to subscribers
        pass
