
from django.db import models

from .profissionalModel import Profissional


class Psicologo(Profissional):
    CRP = models.CharField(
        max_length=50,
        unique=True,
    )
