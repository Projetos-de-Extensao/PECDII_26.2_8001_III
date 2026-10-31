from django.db.models import TextChoices

class StatusSessao(TextChoices):
    SOLICITADA = "SOLICITADA", "Solicitada"
    CONFIRMADA = "CONFIRMADA", "Confirmada"
    REALIZADA = "REALIZADA", "Realizada"
    CANCELADA = "CANCELADA", "Cancelada"
