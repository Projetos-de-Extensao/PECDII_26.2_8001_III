
from django.core.exceptions import ValidationError
from django.db import models, transaction

from .usuarioModel import Usuario


class Responsavel(Usuario):
    """Gerencia os dependentes vinculados ao responsável."""

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
        return self.username

    def adicionarDependente(self, aluno):
        """Vincula um aluno que ainda não possui responsável."""
        VinculoResponsavel.objects.create(
            responsavel=self,
            aluno=aluno,
        )

    def removerDependente(self, aluno):
        """Remove o vínculo de um dependente."""
        vinculo = VinculoResponsavel.objects.filter(
            responsavel=self,
            aluno=aluno,
        ).first()

        if vinculo is None:
            raise ValidationError("Aluno não vinculado a este responsável.")

        vinculo.delete()

    @transaction.atomic
    def transferirResponsabilidade(self, aluno, novoResponsavel):
        """Transfere o aluno para outro responsável."""
        if not isinstance(novoResponsavel, Responsavel):
            raise ValidationError("Novo responsável inválido.")

        vinculo = VinculoResponsavel.objects.select_for_update().filter(
            responsavel=self,
            aluno=aluno,
        ).first()

        if vinculo is None:
            raise ValidationError("Aluno não vinculado a este responsável.")

        vinculo.responsavel = novoResponsavel
        vinculo.save(update_fields=["responsavel"])

    # def inscreverEmSessao(self, aluno, sessao):
    #     return sessao.inscreverAluno(aluno)

    # def cancelarInscricaoEmSessao(self, aluno, sessao, motivo):
    #     return sessao.removerAluno(aluno)


class VinculoResponsavel(models.Model):
    """Associa cada aluno a, no máximo, um responsável."""

    responsavel = models.ForeignKey(
        Responsavel,
        on_delete=models.CASCADE,
        related_name="dependentes",
    )
    aluno = models.OneToOneField(
        "app.Aluno",
        on_delete=models.CASCADE,
        related_name="vinculo_responsavel",
    )


