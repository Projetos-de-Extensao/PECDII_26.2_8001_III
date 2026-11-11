
from django.db import models

from .profissionalModel import Profissional


class Fisioterapeuta(Profissional):
    CREFITO = models.CharField(
        max_length=50,
        unique=True,
    )

    class Meta:
        verbose_name = "Fisioterapeuta"
        verbose_name_plural = "Fisioterapeutas"
