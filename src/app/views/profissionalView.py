from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from app.models import Profissional
from app.serializers import ProfissionalSerializer


class ProfissionalView(ReadOnlyModelViewSet):
    """Permite consultar profissionais cadastrados."""

    def get_queryset(self):
        """Lista profissionais e permite filtrar por especialização."""
        queryset = Profissional.objects.all()
        tipo = self.request.query_params.get("tipo")

        especializacoes = {
            "treinador": "treinador",
            "fisioterapeuta": "fisioterapeuta",
            "psicologo": "psicologo",
            "nutricionista": "nutricionista",
        }

        if tipo in especializacoes:
            queryset = queryset.filter(
                **{f"{especializacoes[tipo]}__isnull": False}
            )
        elif tipo:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"tipo": "Especialização inválida."})

        return queryset
    serializer_class = ProfissionalSerializer
    permission_classes = [IsAuthenticated]