
from django.db import models

from .usuarioModel import Usuario


class Profissional(Usuario):
    tipoContrato = models.CharField(max_length=100)
    formacao = models.CharField(max_length=255)

    class Meta:
        abstract = True
