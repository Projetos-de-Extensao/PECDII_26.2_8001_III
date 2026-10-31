from django.db import models

from .usuarioModel import Usuario


class TipoResponsavel(models.TextChoices):
    PAI = 'PAI', 'Pai'
    MAE = 'MAE', 'Mãe'
    TUTOR = 'TUTOR', 'Tutor'
    OUTRO = 'OUTRO', 'Outro'
    NENHUM = 'NENHUM', 'Nenhum'
    PROPRIO = 'PROPRIO', 'Próprio'


class Aluno(Usuario):
    matricula = models.CharField(max_length=50, unique=True)
    responsavel = models.CharField(
        max_length=10,
        choices=TipoResponsavel.choices,
        default=TipoResponsavel.NENHUM,
    )
    creditos = models.PositiveIntegerField(default=0)

    def assumirTutoria(self):
        self.responsavel = TipoResponsavel.PROPRIO
        self.save(update_fields=['responsavel'])
