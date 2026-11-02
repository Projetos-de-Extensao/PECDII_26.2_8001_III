from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from app.models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializa e valida os dados dos usuários do PKZ Lab.

    Permite receber senhas no cadastro e na atualização,
    utilizando os mecanismos de segurança do Django.

    A senha é utilizada apenas como entrada e nunca
    aparece nas respostas da API.
    """

    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
        trim_whitespace=False,
        validators=[validate_password],
        style={"input_type": "password"}
    )

    class Meta:
        """
        Define os campos disponíveis na API de usuários.
        """

        model = Usuario

        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "telefone",
            "dataNascimento",
            "endereco",
            "password",
        ]

        read_only_fields = ["id"]

    def validate(self, attrs):
        """
        Exige uma senha durante o cadastro.

        Em atualizações, a senha é opcional, permitindo
        alterar outros atributos sem redefini-la.
        """

        # Na criação, a senha deve ser informada.
        if self.instance is None and not attrs.get("password"):
            raise serializers.ValidationError({
                "password": "A senha é obrigatória no cadastro."
            })

        return attrs

    def create(self, validated_data):
        """
        Cria um usuário com a senha protegida por hash.

        Utiliza create_user(), disponibilizado pelo
        gerenciador de usuários do Django.
        """

        return Usuario.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """
        Atualiza os atributos de um usuário existente.

        Caso uma nova senha seja informada, utiliza
        set_password() antes de salvar as alterações.
        """

        # Remove a senha dos dados comuns de atualização.
        senha = validated_data.pop("password", None)

        # Atualiza os demais atributos recebidos.
        for atributo, valor in validated_data.items():
            setattr(instance, atributo, valor)

        # Aplica hashing caso uma nova senha seja informada.
        if senha is not None:
            instance.set_password(senha)

        # Persiste as alterações no banco de dados.
        instance.save()

        return instance