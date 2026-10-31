from django.db.models import TextChoices

class TipoResponsavel(TextChoices):
    PAI = "PAI", "Pai"
    MAE = "MAE", "Mãe"
    TUTOR = "TUTOR", "Tutor"
    OUTRO = "OUTRO", "Outro"
    NENHUM = "NENHUM", "Nenhum"
    PROPRIO = "PROPRIO", "Próprio"
