from django.db import models

class TipoUsuario(models.TextChoices):
    ADMINISTRADOR = "administrador", "Administrador"
    RECEPCAO = "recepcao", "Recepção"
    PROFESSOR_PKZ = "professor_pkz", "Professor PKZ"
    PROFESSOR_ONE_TO_ONE="professor_one_to_one", "Professor One to One"
    FISIOTERAPEUTA = "fisioterapeuta", "Fisioterapeuta"
    NUTRICIONISTA = "nutricionista", "Nutricionista"
    PSICOLOGO = "psicologo", "Psicólogo"

class Usuario(models.Model):
    nome_completo = models.CharField(max_length=100)
    nome_usuario = models.CharField(max_length=20)
    senha = models.CharField(max_length=20)
    perfil = models.CharField(
        choices=TipoUsuario.choices,
    )