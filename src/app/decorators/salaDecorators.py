from functools import wraps

from django.core.exceptions import ValidationError

from app.models.salaModel import Sala

def exigir_sala_nova(msg='A sala já está cadastrada.'):
    def decorator(func):
        @wraps(func)
        def wrapper(self, sala, *args, **kwargs):
            from app.models.salaModel import Sala

            if not isinstance(sala, Sala):
                raise ValidationError('O objeto informado deve ser uma Sala.')

            if not sala._state.adding:
                raise ValidationError(msg)

            return func(self, sala, *args, **kwargs)
        return wrapper
    return decorator


def exigir_sala_valida(msg='A sala precisa estar cadastrada.'):
    def decorator(func):
        @wraps(func)
        def wrapper(self, sala, *args, **kwargs):

            if not isinstance(sala, Sala):
                raise ValidationError('O objeto informado deve ser uma Sala.')

            if sala._state.adding:
                raise ValidationError(msg)

            return func(self, sala, *args, **kwargs)
        return wrapper
    return decorator
