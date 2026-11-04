from functools import wraps

from django.core.exceptions import ValidationError

def exigir_aluno_valido(mensagem):
    def decorator(func):
        @wraps(func)
        def wrapper(self, aluno, *args, **kwargs):
            from app.models.alunoModel import Aluno

            if not isinstance(aluno, Aluno) or aluno.pk is None:
                raise ValidationError(mensagem)

            if aluno._state.adding:
                raise ValidationError(mensagem)

            return func(self, aluno, *args, **kwargs)
        return wrapper
    return decorator
