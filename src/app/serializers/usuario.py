from rest_framework import serializers
from app.models.usuario import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id', 
            'nome_completo',
            'nome_usuario',
            'senha',
        ]
        read_only_fields = ['id']