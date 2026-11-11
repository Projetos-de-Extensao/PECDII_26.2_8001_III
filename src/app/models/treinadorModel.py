
from django.db import models

from .profissionalModel import Profissional


class Treinador(Profissional):
    especialidade = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Treinador"
        verbose_name_plural = "Treinadores"
