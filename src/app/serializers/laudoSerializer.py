from rest_framework import serializers


from app.models import (
    Laudo, Sessao, Aluno, Presenca,
    Treinador, Fisioterapeuta, Psicologo, Nutricionista,
)
from app.Enums import StatusPresenca


class LaudoSerializer(serializers.ModelSerializer):
    """Valida os documentos emitidos pelos profissionais."""

    CAMPOS_DOCUMENTO = {
        "DESEMPENHO": ["desempenhoFisico", "evolucao", "recomendacoes"],
        "FISIOTERAPIA": ["avaliacaoFuncional", "evolucao", "recomendacoes"],
        "PSICOLOGIA": ["finalidade", "procedimentos", "analise", "conclusao"],
        "NUTRICAO": ["avaliacaoNutricional", "evolucao", "orientacoes"],
    }

    ESPECIALIDADES = {
        "DESEMPENHO": Treinador,
        "FISIOTERAPIA": Fisioterapeuta,
        "PSICOLOGIA": Psicologo,
        "NUTRICAO": Nutricionista,
    }

    class Meta:
        model = Laudo
        fields = [
            "id",
            "sessao",
            "aluno",
            "profissional",
            "tipoDocumento",
            "conteudo",
            "dataGeracao",
            "linkArquivo",
        ]
        read_only_fields = ["id", "profissional", "dataGeracao"]

    def validate(self, attrs):
        """Verifica a sessão, o aluno e o formulário do documento."""
        sessao = attrs.get("sessao")
        aluno = attrs.get("aluno")
        tipo = attrs.get("tipoDocumento")
        conteudo = attrs.get("conteudo")

        if not all([sessao, aluno, tipo]):
            raise serializers.ValidationError(
                "Sessão, aluno e tipo de documento são obrigatórios."
            )

        # O aluno precisa estar inscrito na sessão.
        if not Presenca.objects.filter(
            sessao=sessao, aluno=aluno
        ).exclude(status__in=[StatusPresenca.CANCELADA, StatusPresenca.DESISTENTE]).exists():
            raise serializers.ValidationError({
                "aluno": "O aluno não está inscrito nesta sessão."
            })

        # O tipo deve corresponder à especialidade do profissional.
        classe = self.ESPECIALIDADES.get(tipo)

        if classe is None or not classe.objects.filter(
            pk=sessao.profissional_id
        ).exists():
            raise serializers.ValidationError({
                "tipoDocumento": "Documento incompatível com a especialidade."
            })

        # Verifica os campos obrigatórios do formulário.
        if not isinstance(conteudo, dict):
            raise serializers.ValidationError({
                "conteudo": "O conteúdo deve ser um objeto JSON."
            })

        obrigatorios = self.CAMPOS_DOCUMENTO[tipo]

        faltantes = [
            campo for campo in obrigatorios
            if not isinstance(conteudo.get(campo), str)
            or not conteudo[campo].strip()
        ]

        if faltantes:
            raise serializers.ValidationError({
                "conteudo": f"Campos obrigatórios: {', '.join(faltantes)}"
            })

        return attrs