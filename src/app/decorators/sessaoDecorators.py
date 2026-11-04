from functools import wraps
from django.core.exceptions import ValidationError
from app.Enums import StatusSessao


def exigir_sessao_valida(msg='A sessão precisa estar cadastrada.'):
    def decorator(func):
        @wraps(func)
        def wrapper(self, sessao, *args, **kwargs):
            from app.models.sessaoModel import Sessao

            if not isinstance(sessao, Sessao):
                raise ValidationError('O objeto informado deve ser uma Sessao.')

            if sessao._state.adding:
                raise ValidationError(msg)

            return func(self, sessao, *args, **kwargs)
        return wrapper
    return decorator


def exigir_status_confirmada(msg='A sessão precisa estar CONFIRMADA.'):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.status != StatusSessao.CONFIRMADA:
                raise ValidationError(msg)

            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def exigir_status_solicitada(msg='A sessão precisa estar SOLICITADA.'):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.status != StatusSessao.SOLICITADA:
                raise ValidationError(msg)

            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def exigir_status_cancelada(msg='A sessão precisa estar CANCELADA.'):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.status != StatusSessao.CANCELADA:
                raise ValidationError(msg)

            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def exigir_status_rejeitada(msg='A sessão precisa estar REJEITADA.'):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.status != StatusSessao.REJEITADA:
                raise ValidationError(msg)

            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def exigir_status_realizada(msg='A sessão precisa estar REALIZADA.'):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.status != StatusSessao.REALIZADA:
                raise ValidationError(msg)

            return func(self, *args, **kwargs)
        return decorator
    return decorator


def exigir_motivo(msg='O motivo é obrigatório.'):
    def decorator(func):
        @wraps(func)
        def wrapper(self, motivo, *args, **kwargs):
            if not isinstance(motivo, str) or not motivo.strip():
                raise ValidationError(msg)

            return func(self, motivo, *args, **kwargs)
        return wrapper
    return decorator