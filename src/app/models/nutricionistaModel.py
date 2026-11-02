
from django.db import models

from .profissionalModel import Profissional


class Nutricionista(Profissional):
    CRN = models.CharField(
        max_length=50,
        unique=True,
    )
