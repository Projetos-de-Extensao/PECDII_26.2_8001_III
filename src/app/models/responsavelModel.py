
from django.db import models

from .usuarioModel import Usuario


class Responsavel(Usuario):
    """Representa um responsável pelos alunos do PKZ Lab."""
    
    usuario_ptr = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name="perfil_responsavel",
    )


    class Meta:
        verbose_name = "Responsável"
        verbose_name_plural = "Responsáveis"

    def __str__(self):
        """Retorna o nome de usuário do responsável."""
        return self.username
