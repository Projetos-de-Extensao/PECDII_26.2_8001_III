from rest_framework import serializers
from app.models.aluno import Aluno

class AlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = [
            'id',
            'tipo_aluno', 
            'nome',
            'nascimento', 
            'categoria', 
            'telefone',
            'observacoes',
            'servicos',
            'plano_mensal_creditos'
        ]
        read_only_fields = ['id']