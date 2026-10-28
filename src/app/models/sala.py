from django.db import models

class Sala(models.Model):
    numero = models.CharField(max_length=4, unique=True)
    capacidade = models.IntegerField()
