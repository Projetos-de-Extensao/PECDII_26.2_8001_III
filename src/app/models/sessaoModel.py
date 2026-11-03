from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from app.Enums import StatusSessao
from app.decorators import *

from .salaModel import Sala
from .profissionalModel import Profissional


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
    profissional = models.ForeignKey(
        'app.Profissional',
        on_delete=models.PROTECT,
        related_name='sessoes',
        null=True,
        blank=True,
    )

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


    @classmethod
    def solicitar(cls, profissional, sala, dataHora, duracao, creditosNecessarios):
        """
        Cria uma nova sessão com status SOLICITADA.
        Esse método deve sempre ser utilizado ao solicitar uma nova sessão, 
        pois ele garante que a sessão será criada com o status correto 
        e que os dados serão validados antes de salvar no banco de dados.
        """
        if not isinstance(sala, Sala) or sala.pk is None:
            raise ValidationError("A sala deve estar cadastrada.")

        if not isinstance(profissional, Profissional) or profissional.pk is None:
            raise ValidationError("O profissional deve estar cadastrado.")

        sessao = cls(
            sala=sala,
            dataHora=dataHora,
            duracao=duracao,
            creditosNecessarios=creditosNecessarios,
            status=StatusSessao.SOLICITADA,
            profissional=profissional,
        )

        sessao.full_clean()
        sessao.save()

        return sessao


    @exigir_sessao_valida('A sessão precisa estar cadastrada para ser confirmada.')
    @exigir_status_solicitada('Apenas sessões solicitadas podem ser confirmadas.')
    def confirmar(self):
        self.status = StatusSessao.CONFIRMADA
        self.save(update_fields=['status'])


    @exigir_sessao_valida('A sessão precisa estar cadastrada para ser rejeitada.')
    @exigir_status_solicitada('A sessão não pode ser rejeitada no estado atual.')
    @exigir_motivo()
    def rejeitar(self, motivo):
        motivo = motivo.strip()
        self.status = StatusSessao.REJEITADA
        self.motivoCancelamento = motivo
        self.save(update_fields=['status', 'motivoCancelamento'])



    @exigir_sessao_valida('A sessão precisa estar cadastrada para ser cancelada.')
    @exigir_motivo()
    def cancelar(self, motivo):
        if self.status not in (
            StatusSessao.SOLICITADA,
            StatusSessao.CONFIRMADA,
        ):
            raise ValidationError(
                'A sessão não pode ser cancelada no estado atual.'
            )

        self.status = StatusSessao.CANCELADA
        self.motivoCancelamento = motivo.strip()
        self.save(update_fields=['status', 'motivoCancelamento'])
