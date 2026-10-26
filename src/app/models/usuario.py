from django.db import models
from django.conf import settings

class TipoUsuario(models.TextChoices):
    ADMINISTRADOR = "administrador", "Administrador"
    RECEPCAO = "recepcao", "Recepção"
    PROFESSOR_PKZ = "professor_pkz", "Professor PKZ"
    PROFESSOR_ONE_TO_ONE="professor_one_to_one", "Professor One to One"
    FISIOTERAPEUTA = "fisioterapeuta", "Fisioterapeuta"
    NUTRICIONISTA = "nutricionista", "Nutricionista"
    PSICOLOGO = "psicologo", "Psicólogo"

class Usuario(models.Model):
    conta = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_pkz",
        null=True,
        blank=True,
    )

    nome_completo = models.CharField(max_length=100)

    nome_usuario = models.CharField(max_length=150)

    perfil = models.CharField(
        max_length=30,
        choices=TipoUsuario.choices,
    )

    def __str__(self):
        return f"{self.nome_completo} - {self.get_perfil_display()}"
