from django.db import models

from .usuarioModel import Usuario
from django.core.exceptions import ValidationError

class Administrador(Usuario):
    """
    Representa um administrador do sistema PKZ Lab.

    Herda os atributos e funcionalidades da classe Usuario,
    incluindo os recursos de autenticação do Django.

    O administrador é responsável por:
        - Cadastrar usuários.
        - Desativar usuários.
        - Cadastrar salas.
        - Aprovar sessões.
        - Desaprovar sessões.

    Atributos:
        tipoContrato (str): Tipo de contrato do administrador
            com a instituição.
    """

    tipoContrato = models.CharField(
        max_length=100
    )

    def __str__(self):
        """
        Retorna a representação textual do administrador.

        Returns:
            str: Nome de usuário do administrador.
        """
        return self.username




    def cadastrarUsuario(self, usuario):
        """
        Cadastra um usuário no sistema PKZ Lab.

        O método recebe uma instância de Usuario previamente
        preenchida e realiza seu cadastro no banco de dados.

        Args:
            usuario (Usuario): Usuário que será cadastrado.

        Raises:
            ValidationError: Caso o objeto informado não seja
                uma instância de Usuario ou já esteja cadastrado.
        """

        # Verifica se o objeto recebido pertence à classe Usuario.
        if not isinstance(usuario, Usuario):
            raise ValidationError(
                "O objeto informado deve ser um Usuario."
            )

        # Impede o cadastro duplicado de uma instância já salva.
        if not usuario._state.adding:
            raise ValidationError(
                "O usuário já está cadastrado."
            )

        # Executa as validações definidas no modelo.
        usuario.full_clean()

        # Registra o usuário no banco de dados.
        usuario.save()


    def desativarUsuario(self, usuario):
        """
        Desativa um usuário cadastrado no sistema PKZ Lab.

        A desativação não remove o registro do banco de dados.
        Apenas altera o atributo is_active para False,
        impedindo a autenticação pelos mecanismos padrão
        do Django que verificam esse atributo.

        Args:
            usuario (Usuario): Usuário que será desativado.

        Raises:
            ValidationError: Caso o objeto informado seja
                inválido ou ainda não esteja cadastrado.
        """

        # Verifica se o objeto informado é um usuário.
        if not isinstance(usuario, Usuario):
            raise ValidationError(
                "O objeto informado deve ser um Usuario."
            )

        # Impede a desativação de usuários ainda não cadastrados.
        if usuario._state.adding:
            raise ValidationError(
                "O usuário precisa estar cadastrado."
            )

        # Impede operações desnecessárias.
        if not usuario.is_active:
            raise ValidationError(
                "O usuário já está desativado."
            )

        # Desativa a conta sem excluir seus dados.
        usuario.is_active = False

        # Atualiza somente o campo necessário no banco.
        usuario.save(update_fields=["is_active"])