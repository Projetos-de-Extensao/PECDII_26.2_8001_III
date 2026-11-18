from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Value
from django.db.models.functions import Length, Trim
from django.db.models.lookups import GreaterThan
from django.db import transaction
from django.utils import timezone

from app.Enums import StatusPresenca, StatusSessao
from app.Enums.StatusPresencaEnum import STATUS_CHAMADA, STATUS_INSCRICAO_ATIVA

from .alunoModel import Aluno
from .sessaoModel import Sessao


class Presenca(models.Model):
    sessao = models.ForeignKey(
        Sessao,
        on_delete=models.PROTECT,
        related_name='presencas',
    )
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.PROTECT,
        related_name='presencas',
    )
    status = models.CharField(
        max_length=12,
        choices=StatusPresenca.choices,
    )
    justificativa = models.TextField(blank=True, default='')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('sessao', 'aluno'),
                name='presenca_unica_sessao_aluno',
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=StatusPresenca.values),
                name='presenca_status_valido',
            ),
            models.CheckConstraint(
                condition=(
                    ~models.Q(status=StatusPresenca.JUSTIFICADO)
                    | GreaterThan(Length(Trim('justificativa')), Value(0))
                ),
                name='presenca_justificativa_obrigatoria',
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}

        if self.sessao_id:
            sessao = Sessao.objects.filter(pk=self.sessao_id).values(
                "status", "dataHora"
            ).first()
            if sessao and (
                (
                    sessao["status"] == StatusSessao.CANCELADA
                    and self.status != StatusPresenca.CANCELADA
                )
                or (
                    sessao["status"] not in (
                        StatusSessao.CONFIRMADA,
                        StatusSessao.REALIZADA,
                        StatusSessao.CANCELADA,
                    )
                )
            ):
                errors['sessao'] = (
                    'A presença só pode ser registrada em sessões confirmadas '
                    'ou realizadas.'
                )

            if (
                sessao
                and self.status in STATUS_CHAMADA
                and sessao["dataHora"] > timezone.now()
            ):
                errors["sessao"] = (
                    "A chamada só pode ser registrada após o início da sessão."
                )

        if (
            self.status in STATUS_CHAMADA
            and not self._state.adding
            and not Presenca.objects.filter(
                pk=self.pk,
                status__in=STATUS_INSCRICAO_ATIVA,
            ).exists()
        ):
            errors["status"] = (
                "Não é possível registrar chamada para uma inscrição inativa."
            )

        if (
            self.status == StatusPresenca.JUSTIFICADO
            and (
                not isinstance(self.justificativa, str)
                or not self.justificativa.strip()
            )
        ):
            errors['justificativa'] = (
                'A justificativa é obrigatória para o status JUSTIFICADO.'
            )

        if errors:
            raise ValidationError(errors)
    

    @classmethod
    def novaPresenca(cls, sessao, aluno):
        """Cria uma inscrição, impedindo duplicidade."""
        if cls.objects.filter(sessao=sessao, aluno=aluno).exists():
            raise ValidationError("Aluno já inscrito nesta sessão.")

        return cls.objects.create(
            sessao=sessao,
            aluno=aluno,
            status=StatusPresenca.PENDENTE,
        )

    @transaction.atomic
    def registrarPresenca(self, status, justificativa):
        if self._state.adding:
            raise ValidationError(
                'A presença precisa estar cadastrada para ser atualizada.'
            )

        if status not in STATUS_CHAMADA:
            raise ValidationError({
                "status": "Informe PRESENTE, AUSENTE ou JUSTIFICADO."
            })
        if not isinstance(justificativa, str):
            raise ValidationError({
                "justificativa": "A justificativa deve ser um texto."
            })

        Sessao.objects.select_for_update().get(pk=self.sessao_id)
        presenca = type(self).objects.select_for_update().get(pk=self.pk)
        if presenca.status not in STATUS_INSCRICAO_ATIVA:
            raise ValidationError({
                "status": (
                    "Não é possível registrar chamada para uma inscrição inativa."
                )
            })

        presenca.status = status
        presenca.justificativa = justificativa.strip()
        presenca.full_clean()
        presenca.save(update_fields=['status', 'justificativa'])
        self.status = presenca.status
        self.justificativa = presenca.justificativa

    def __str__(self):
        return f'{self.aluno} — sessão {self.sessao_id}: {self.get_status_display()}'
