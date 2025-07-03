from django.db import models
from .enums import CategoryEnum

class Student(models.Model):
    name = models.CharField(max_length=255)
    grade = models.IntegerField()
    turma = models.CharField(max_length=50)
    course = models.CharField(max_length=255, default='N/A', null=True)
    category = models.CharField(max_length=20, choices=CategoryEnum.choices)

    def save(self, *args, **kwargs):
        self.category = self.get_category_from_grade()
        super().save(*args, **kwargs)

    def get_category_from_grade(self):
        if 1 <= self.grade <= 6:
            return CategoryEnum.PRIMARIO
        elif 7 <= self.grade <= 9:
            return CategoryEnum.SECUNDARIO
        elif 10 <= self.grade <= 13:
            return CategoryEnum.MEDIO
        return None

    def __str__(self):
        return self.name

