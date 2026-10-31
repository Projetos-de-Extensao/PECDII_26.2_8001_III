from django.db import models

from app.Enums import TipoResponsavel

from .usuarioModel import Usuario


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
