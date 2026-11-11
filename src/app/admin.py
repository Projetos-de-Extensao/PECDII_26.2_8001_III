from django.contrib import admin

# Import your models here.
from app.models import Usuario
from app.models import Sala
from app.models import Aluno
from app.models import Sessao
from app.models import Presenca
from app.models import Profissional
from app.models import Treinador
from app.models import Nutricionista
from app.models import Psicologo
from app.models import Fisioterapeuta
from app.models import Administrador
from app.models import Responsavel
from app.models import VinculoResponsavel
from app.models import Laudo


admin.site.register(Usuario)
admin.site.register(Sala)
admin.site.register(Aluno)
admin.site.register(Profissional)
admin.site.register(Treinador)
admin.site.register(Nutricionista)
admin.site.register(Psicologo)
admin.site.register(Fisioterapeuta)
admin.site.register(Administrador)
admin.site.register(Responsavel)
admin.site.register(VinculoResponsavel)
admin.site.register(Laudo)


@admin.register(Sessao)
class SessaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'dataHora', 'sala', 'status')
    # Evita alterar o estado sem passar pelas regras do método cancelar().
    readonly_fields = ('status', 'motivoCancelamento')


@admin.register(Presenca)
class PresencaAdmin(admin.ModelAdmin):
    list_display = ('id', 'sessao', 'aluno', 'status')
    readonly_fields = ('sessao', 'aluno', 'status', 'justificativa')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False