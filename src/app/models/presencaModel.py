from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Value
from django.db.models.functions import Length, Trim
from django.db.models.lookups import GreaterThan

from app.Enums import StatusPresenca, StatusSessao

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
            status_sessao = Sessao.objects.filter(pk=self.sessao_id).values_list(
                'status',
                flat=True,
            ).first()
            if status_sessao and status_sessao not in (
                StatusSessao.CONFIRMADA,
                StatusSessao.REALIZADA,
            ):
                errors['sessao'] = (
                    'A presença só pode ser registrada em sessões confirmadas '
                    'ou realizadas.'
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
            status=StatusPresenca.AUSENTE,
        )

    def registrarPresenca(self, status, justificativa):
        if self._state.adding:
            raise ValidationError(
                'A presença precisa estar cadastrada para ser atualizada.'
            )

        status_anterior = self.status
        justificativa_anterior = self.justificativa
        self.status = status
        self.justificativa = justificativa

        try:
            self.full_clean()
        except ValidationError:
            self.status = status_anterior
            self.justificativa = justificativa_anterior
            raise

        self.justificativa = self.justificativa.strip()
        self.save(update_fields=['status', 'justificativa'])

    def __str__(self):
        return f'{self.aluno} — sessão {self.sessao_id}: {self.get_status_display()}'
