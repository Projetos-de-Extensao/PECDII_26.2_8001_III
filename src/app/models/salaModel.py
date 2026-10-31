from django.db import models


class Sala(models.Model):
    numero = models.IntegerField(unique=True)
    capacidade = models.IntegerField()
