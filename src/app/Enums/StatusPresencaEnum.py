from django.db.models import TextChoices


class StatusPresenca(TextChoices):
    PRESENTE = 'PRESENTE', 'Presente'
    AUSENTE = 'AUSENTE', 'Ausente'
    JUSTIFICADO = 'JUSTIFICADO', 'Justificado'
    DESISTENTE = 'DESISTENTE', 'Desistente'
