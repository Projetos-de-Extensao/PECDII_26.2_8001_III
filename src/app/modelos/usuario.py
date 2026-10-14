from django.db import models

class Usuario(models.Model):
    nome_completo = models.CharField(max_length=100)
    nome_usuario = models.CharField(max_length=20)
    senha = models.CharField(max_length=20)
    # perfil = models.CheckConstraint(
    #     "Administrador",
    #     "Recepção",
    #     "Professor PKZ",
    #     "Professor One to One",
    #     "Fisioterapeuta",
    #     "Nutricionista",
    #     "Psicológo"
    # )