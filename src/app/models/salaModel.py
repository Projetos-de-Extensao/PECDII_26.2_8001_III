from django.db import models
from django.core.validators import MinValueValidator


class Sala(models.Model):
    numero = models.IntegerField(unique=True)
    capacidade = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(capacidade__gte=1),
                name="sala_capacidade_maior_que_zero",
            ),
        ]
