from rest_framework import serializers
from app.models.usuario import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id', 
            'nome_completo',
            'nome_usuario',
            'perfil',
        ]
        read_only_fields = ['id']