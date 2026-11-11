from datetime import timedelta
from django.db.models import F
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone

from app.Enums import StatusPresenca, StatusSessao
from app.decorators import *

from .salaModel import Sala
from .profissionalModel import Profissional
from .alunoModel import Aluno


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
        Profissional,
        on_delete=models.PROTECT,
        related_name='sessoes',
        null=True,
        blank=True,
    )
    ListaPresenca = models.ManyToManyField(
        Aluno,
        through='app.Presenca',
        related_name='sessoes',
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

    def clean(self):
        super().clean()
        errors = {}
        data_hora_futura = bool(
            self.dataHora and self.dataHora > timezone.now()
        )

        if self.dataHora and not data_hora_futura:
            errors["dataHora"] = "A data e hora da sessão devem ser futuras."

        status_que_reservam_sala = (
            StatusSessao.SOLICITADA,
            StatusSessao.CONFIRMADA,
        )
        if (
            self.status in status_que_reservam_sala
            and self.sala_id
            and data_hora_futura
            and self.duracao
            and self.duracao > timedelta(0)
        ):
            fim = self.dataHora + self.duracao
            sessoes_conflitantes = Sessao.objects.filter(
                sala_id=self.sala_id,
                status__in=status_que_reservam_sala,
                dataHora__lt=fim,
            ).exclude(pk=self.pk).only("dataHora", "duracao")

            if any(
                sessao.dataHora + sessao.duracao > self.dataHora
                for sessao in sessoes_conflitantes
            ):
                errors["dataHora"] = (
                    "A sala já possui sessão em horário conflitante."
                )

        if errors:
            raise ValidationError(errors)


    #@exigir_sala_valida('A sala precisa estar cadastrada para solicitar uma sessão.')
    @classmethod
    def solicitar(cls, profissional, sala, dataHora, duracao, creditosNecessarios):
        """
        Cria uma nova sessão com status SOLICITADA.
        Esse método deve sempre ser utilizado ao solicitar uma nova sessão, 
        pois ele garante que a sessão será criada com o status correto 
        e que os dados serão validados antes de salvar no banco de dados.
        """
        if not isinstance(profissional, Profissional) or profissional.pk is None:
            raise ValidationError("O profissional deve estar cadastrado.")
        if not isinstance(sala, Sala) or sala.pk is None:
            raise ValidationError(
                "A sala precisa estar cadastrada para solicitar uma sessão."
            )

        sessao = cls(
            sala=sala,
            dataHora=dataHora,
            duracao=duracao,
            creditosNecessarios=creditosNecessarios,
            status=StatusSessao.SOLICITADA,
            profissional=profissional,
        )

        with transaction.atomic():
            Sala.objects.select_for_update().get(pk=sala.pk)
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
    @transaction.atomic
    def cancelar(self, motivo):
        """Cancela a sessão e reembolsa integralmente os alunos inscritos."""
        from .presencaModel import Presenca

        sessao = Sessao.objects.select_for_update().get(pk=self.pk)

        if sessao.status not in (
            StatusSessao.SOLICITADA,
            StatusSessao.CONFIRMADA,
        ):
            raise ValidationError("A sessão não pode ser cancelada neste estado.")

        if sessao.dataHora <= timezone.now():
            raise ValidationError("Não é possível cancelar uma sessão iniciada.")

        alunos_ids = Presenca.objects.filter(
            sessao=sessao,
            status=StatusPresenca.PENDENTE,
        ).values_list("aluno_id", flat=True)

        Aluno.objects.filter(pk__in=alunos_ids).update(
            creditos=F("creditos") + sessao.creditosNecessarios
        )

        Presenca.objects.filter(sessao=sessao, status=StatusPresenca.PENDENTE).update(
            status=StatusPresenca.CANCELADA
        )

        sessao.status = StatusSessao.CANCELADA
        sessao.motivoCancelamento = motivo.strip()
        sessao.save(update_fields=["status", "motivoCancelamento"])

        self.status = sessao.status
        self.motivoCancelamento = sessao.motivoCancelamento

    #def cancelar(self, motivo):
        #if self.status not in (
           # StatusSessao.SOLICITADA,
            #StatusSessao.CONFIRMADA,
        #):
            #raise ValidationError(
                #'A sessão não pode ser cancelada no estado atual.'
            #)

        #self.status = StatusSessao.CANCELADA
        #self.motivoCancelamento = motivo.strip()
       # self.save(update_fields=['status', 'motivoCancelamento'])


    @exigir_sessao_valida('A sessão precisa estar cadastrada para ser realizada.')
    @exigir_status_confirmada('Um aluno não pode ser inscrito em uma sessão que não está confirmada.')
    @exigir_aluno_valido('O aluno precisa estar cadastrado para ser inscrito em uma sessão.')
    @transaction.atomic
    def inscreverAluno(self, aluno):
        """Inscreve o aluno e desconta os créditos da sessão."""
        from .presencaModel import Presenca

        if self.dataHora <= timezone.now():
            raise ValidationError("A sessão já começou.")

        aluno = Aluno.objects.select_for_update().get(pk=aluno.pk)

        presenca = Presenca.objects.filter(sessao=self, aluno=aluno).first()
        if presenca and presenca.status != StatusPresenca.DESISTENTE:
            raise ValidationError("Aluno já inscrito nesta sessão.")

        status_que_reservam_horario = (
            StatusSessao.SOLICITADA,
            StatusSessao.CONFIRMADA,
        )
        fim = self.dataHora + self.duracao
        inscricoes_conflitantes = Presenca.objects.filter(
            aluno=aluno,
            status=StatusPresenca.PENDENTE,
            sessao__status__in=status_que_reservam_horario,
            sessao__dataHora__lt=fim,
        ).exclude(sessao=self).select_related("sessao")

        if any(
            inscricao.sessao.dataHora + inscricao.sessao.duracao > self.dataHora
            for inscricao in inscricoes_conflitantes
        ):
            raise ValidationError(
                "Aluno já possui sessão em horário conflitante."
            )

        if aluno.creditos < self.creditosNecessarios:
            raise ValidationError("Créditos insuficientes.")

        if presenca:
            presenca.status = StatusPresenca.PENDENTE
            presenca.save(update_fields=["status"])
        else:
            presenca = Presenca.novaPresenca(self, aluno)
        aluno.creditos -= self.creditosNecessarios
        aluno.save(update_fields=["creditos"])

        return presenca

    @exigir_sessao_valida('A sessão precisa estar cadastrada para que um aluno possa ser removido.')
    @exigir_aluno_valido('O aluno precisa estar cadastrado para ser removido da sessão.')
    @transaction.atomic
    def removerAluno(self, aluno):
        """Cancela a inscrição e devolve créditos com 12h de antecedência."""
        from .presencaModel import Presenca

        agora = timezone.now()

        if self.dataHora <= agora:
            raise ValidationError("A sessão já começou.")

        aluno = Aluno.objects.select_for_update().get(pk=aluno.pk)
        presenca = Presenca.objects.filter(
            sessao=self, aluno=aluno
        ).first()

        if presenca is None or presenca.status != StatusPresenca.PENDENTE:
            raise ValidationError("O aluno não está inscrito nesta sessão.")

        if self.dataHora - agora >= timedelta(hours=12):
            aluno.creditos += self.creditosNecessarios
            aluno.save(update_fields=["creditos"])

        presenca.status = StatusPresenca.DESISTENTE
        presenca.save(update_fields=["status"])
