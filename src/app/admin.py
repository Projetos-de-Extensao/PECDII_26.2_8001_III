from django.contrib import admin

# Register your models here.
from app.models.aluno import Aluno
from app.models.usuario import Usuario
from app.models.sala import Sala

admin.site.register(Aluno)
admin.site.register(Usuario)
admin.site.register(Sala)