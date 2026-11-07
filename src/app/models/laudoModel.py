from django.db import models
from django.core.exceptions import ValidationError

from .sessaoModel import Sessao
from .alunoModel import Aluno
from .profissionalModel import Profissional


class Laudo(models.Model):
    """
    Representa um laudo emitido após ou durante o acompanhamento de uma sessão.

    Atributos:
        sessao (Sessao): Sessão à qual o laudo está vinculado.
        aluno (Aluno): Aluno ao qual o laudo se refere.
        profissional (Profissional): Profissional responsável pela emissão do laudo.
        dataGeracao (datetime): Data e hora em que o laudo foi gerado.
        linkArquivo (str): Link/URL ou caminho referente ao documento do laudo.
    """

    TIPOS_DOCUMENTO = [
        ("DESEMPENHO", "Relatório de Desempenho"),
        ("FISIOTERAPIA", "Documento Fisioterapêutico"),
        ("PSICOLOGIA", "Documento Psicológico"),
        ("NUTRICAO", "Documento Nutricional"),
    ]

    tipoDocumento = models.CharField(
        max_length=20,
        choices=TIPOS_DOCUMENTO,
        null=True,
        blank=True,
        verbose_name="Tipo de Documento",
    )

    conteudo = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Conteúdo do Documento",
    )

    sessao = models.ForeignKey(
        Sessao,
        on_delete=models.CASCADE,
        related_name='laudos',
        verbose_name="Sessão"
    )
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name='laudos',
        verbose_name="Aluno"
    )
    profissional = models.ForeignKey(
        Profissional,
        on_delete=models.CASCADE,
        related_name='laudos_emitidos',
        verbose_name="Profissional Responsável"
    )
    dataGeracao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Geração"
    )
    linkArquivo = models.URLField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="Link do Arquivo"
    )

    class Meta:
        verbose_name = "Laudo"
        verbose_name_plural = "Laudos"
        ordering = ['-dataGeracao']

    def __str__(self):
        """
        Retorna a representação textual do laudo.
        """
        return f"Laudo #{self.pk} - Aluno: {self.aluno} (Sessão #{self.sessao_id})"

    def clean(self):
        """
        Validações de negócio para garantir a consistência do laudo antes de salvar.
        """
        super().clean()
        
        # Opcional: Garante que o profissional informado é o mesmo da sessão (se aplicável ao modelo)
        if self.sessao_id and self.profissional_id:
            if hasattr(self.sessao, 'profissional') and self.sessao.profissional != self.profissional:
                raise ValidationError({
                    'profissional': 'O profissional emissor do laudo deve ser o mesmo responsável pela sessão.'
                })