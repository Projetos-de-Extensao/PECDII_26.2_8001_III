from django.contrib import admin

# Import your models here.
from app.models import Usuario
from app.models import Sala
from app.models import Aluno
from app.models import Sessao
from app.models import Presenca


admin.site.register(Usuario)
admin.site.register(Sala)
admin.site.register(Aluno)


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