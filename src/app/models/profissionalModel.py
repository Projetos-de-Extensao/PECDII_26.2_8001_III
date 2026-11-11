
from django.db import models
from django.core.exceptions import ValidationError

from .usuarioModel import Usuario
from .salaModel import Sala
#from .sessaoModel import Sessao


class Profissional(Usuario):
    tipoContrato = models.CharField(max_length=100)
    formacao = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Profissional"
        verbose_name_plural = "Profissionais"

    #class Meta:
        #abstract = True

    def solicitarSessao(self, sala, dataHora, duracao, creditosNecessarios):
        from .sessaoModel import Sessao
        if not isinstance(sala, Sala) or sala.pk is None:
            raise ValidationError(
                "A sala deve estar cadastrada."
            )

        sessao = Sessao.solicitar(self, sala, dataHora, duracao, creditosNecessarios)

        return sessao

    def cancelarSessao(self, sessao, motivo):
        from .sessaoModel import Sessao
        if not isinstance(sessao, Sessao):
            raise ValidationError(
                "A sessão informada é inválida."
            )

        sessao.cancelar(motivo)
