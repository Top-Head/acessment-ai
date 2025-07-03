from django.db import models
from .enums import FaseEnum, CategoryEnum, VariantEnum

class Key(models.Model):
    title = models.CharField(max_length=200)
    key_url = models.TextField()
    fase = models.CharField(max_length=10, choices=FaseEnum.choices)
    category = models.CharField(max_length=20, choices=CategoryEnum.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    variant = models.CharField(max_length=10, choices=VariantEnum.choices)
    matrix = models.JSONField() 
    classe = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title
