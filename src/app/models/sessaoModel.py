from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from app.Enums import StatusSessao

from .salaModel import Sala


class Sessao(models.Model):
    sala = models.ForeignKey(
        Sala,
        on_delete=models.PROTECT,
        related_name='sessoes',
    )
    dataHora = models.DateTimeField()
    duracao = models.DurationField(
        validators=[MinValueValidator(timedelta(microseconds=1))],
    )
    status = models.CharField(
        max_length=10,
        choices=StatusSessao.choices,
        default=StatusSessao.SOLICITADA,
    )
    creditosNecessarios = models.IntegerField(
        validators=[MinValueValidator(0)],
    )
    motivoCancelamento = models.TextField(blank=True, default='')

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(duracao__gt=timedelta(0)),
                name='sessao_duracao_maior_que_zero',
            ),
            models.CheckConstraint(
                condition=models.Q(creditosNecessarios__gte=0),
                name='sessao_creditos_nao_negativos',
            ),
        ]

    def cancelar(self, motivo):
        if self._state.adding:
            raise ValidationError('A sessão precisa estar cadastrada para ser cancelada.')
        if self.status not in (StatusSessao.CONFIRMADA):
            raise ValidationError('A sessão não pode ser cancelada no estado atual.')

        if not isinstance(motivo, str) or not motivo.strip():
            raise ValidationError('O motivo do cancelamento é obrigatório.')

        motivo = motivo.strip()
        self.status = StatusSessao.CANCELADA
        self.motivoCancelamento = motivo
        self.save(update_fields=['status', 'motivoCancelamento'])

    def rejeitar(self, motivo):
        if self._state.adding:
            raise ValidationError('A sessão precisa estar cadastrada para ser rejeitada.')
        if self.status != StatusSessao.SOLICITADA:
            raise ValidationError('Apenas sessões solicitadas podem ser rejeitadas.')

        if not isinstance(motivo, str) or not motivo.strip():
            raise ValidationError('O motivo da rejeição é obrigatório.')

        motivo = motivo.strip()
        self.status = StatusSessao.REJETADA
        self.motivoCancelamento = motivo
        self.save(update_fields=['status', 'motivoCancelamento'])

    def confirmar(self):
        if self._state.adding:
            raise ValidationError('A sessão precisa estar cadastrada para ser confirmada.')
        if self.status != StatusSessao.SOLICITADA:
            raise ValidationError('Apenas sessões solicitadas podem ser confirmadas.')

        self.status = StatusSessao.CONFIRMADA
        self.save(update_fields=['status'])

    @classmethod
    def solicitar(cls, sala, dataHora, duracao, creditosNecessarios):
        if not isinstance(sala, Sala) or sala.pk is None:
            raise ValidationError(
                "A sala deve estar cadastrada."
            )

        sessao = cls(
            sala=sala,
            dataHora=dataHora,
            duracao=duracao,
            creditosNecessarios=creditosNecessarios,
            status=StatusSessao.SOLICITADA,
        )

        sessao.full_clean()
        sessao.save()

        return sessao
