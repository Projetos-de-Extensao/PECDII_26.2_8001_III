from functools import wraps

from django.core.exceptions import ValidationError


def exigir_usuario_novo(msg='O usuário já está cadastrado.'):
    def decorator(func):
        @wraps(func)
        def wrapper(self, usuario, *args, **kwargs):
            from app.models.usuarioModel import Usuario

            if not isinstance(usuario, Usuario):
                raise ValidationError('O objeto informado deve ser um Usuario.')

            if not usuario._state.adding:
                raise ValidationError(msg)

            return func(self, usuario, *args, **kwargs)
        return wrapper
    return decorator


def exigir_usuario_cadastrado(msg='O usuário precisa estar cadastrado.'):
    def decorator(func):
        @wraps(func)
        def wrapper(self, usuario, *args, **kwargs):
            from app.models.usuarioModel import Usuario

            if not isinstance(usuario, Usuario):
                raise ValidationError('O objeto informado deve ser um Usuario.')

            if usuario._state.adding:
                raise ValidationError(msg)

            return func(self, usuario, *args, **kwargs)
        return wrapper
    return decorator


def exigir_usuario_ativo(msg='O usuário já está desativado.'):
    def decorator(func):
        @wraps(func)
        def wrapper(self, usuario, *args, **kwargs):
            if not usuario.is_active:
                raise ValidationError(msg)

            return func(self, usuario, *args, **kwargs)
        return wrapper
    return decorator