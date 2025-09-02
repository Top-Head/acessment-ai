from django.db import models
from .student import Student
from .key import Key
from .enums import FaseEnum, StatusEnum

class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="answers")
    chave = models.ForeignKey(Key, on_delete=models.SET_NULL, null=True, blank=True)
    answer_matrix = models.JSONField(null=True, default=list)  
    answer_img_url = models.TextField()
    note = models.FloatField(null=True, blank=True)
    corrects = models.IntegerField(null=True, blank=True)
    wrongs = models.IntegerField(null=True, blank=True)
    nulls = models.IntegerField(null=True, blank=True)
    fase = models.CharField(max_length=10, choices=FaseEnum.choices)
    status = models.CharField(max_length=20, choices=StatusEnum.choices, null=True, default=None)

    def save(self, *args, **kwargs):
        self.status = self.get_status_from_note()
        super().save(*args, **kwargs)

    def get_status_from_note(self):
        if self.note >= 10:
            return StatusEnum.APROVADO
        else:
            return StatusEnum.REPROVADO

    def __str__(self):
        return f'{self.student.name} - {self.fase}'
