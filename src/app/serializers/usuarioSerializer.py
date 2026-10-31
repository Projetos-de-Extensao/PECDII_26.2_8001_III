from rest_framework import serializers
from app.models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'telefone',
            'dataNascimento',
            'endereco',
        ]