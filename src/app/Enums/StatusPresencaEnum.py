from django.db.models import TextChoices


class StatusPresenca(TextChoices):
    """Estados possíveis de uma inscrição ou presença."""
    PENDENTE = "PENDENTE", "Pendente"
    PRESENTE = 'PRESENTE', 'Presente'
    AUSENTE = 'AUSENTE', 'Ausente'
    JUSTIFICADO = 'JUSTIFICADO', 'Justificado'
    DESISTENTE = 'DESISTENTE', 'Desistente'
    CANCELADA = "CANCELADA", "Cancelada"
