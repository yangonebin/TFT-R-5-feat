from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    financial_products = models.TextField(blank=True, null=True)
    nickname = models.CharField(max_length=100, blank=True, null=True)