from django.db import models

class FaseEnum(models.TextChoices):
    F1 = 'F1', 'Fase 1'
    F2 = 'F2', 'Fase 2'

class CategoryEnum(models.TextChoices):
    PRIMARIO = 'primario', 'Primário'
    SECUNDARIO = 'secundario', 'Secundário'
    MEDIO = 'medio', 'Médio'

class VariantEnum(models.TextChoices):
    A = 'A', 'A'
    B = 'B', 'B'

class StatusEnum(models.TextChoices):
    REPROVADO = 'Reprovado', 'Reprovado'
    APROVADO = 'Aprovado', 'Aprovado'