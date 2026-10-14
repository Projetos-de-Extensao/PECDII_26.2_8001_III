from django.contrib import admin

# Register your models here.
from app.models import Produto
from .modelos.aluno import Aluno
from .modelos.usuario import Usuario

admin.site.register(Produto)
admin.site.register(Aluno)
admin.site.register(Usuario)