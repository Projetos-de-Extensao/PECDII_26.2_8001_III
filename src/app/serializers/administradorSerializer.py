from app.models import Administrador

from .usuarioSerializer import UsuarioSerializer


class AdministradorSerializer(UsuarioSerializer):
    """
    Serializa os dados de um administrador do PKZ Lab.

    Reutiliza os campos definidos em UsuarioSerializer,
    acrescentando o atributo tipoContrato, específico
    da classe Administrador.

    A serialização não inclui a senha do usuário,
    evitando sua exposição nas respostas da API.
    """

    class Meta(UsuarioSerializer.Meta):
        """
        Define o modelo e os campos utilizados
        na serialização de administradores.
        """

        model = Administrador

        # Reutiliza os campos de Usuario e adiciona tipoContrato.
        fields = UsuarioSerializer.Meta.fields + [
            'tipoContrato',
        ]