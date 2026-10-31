from django.contrib import admin

# Import your models here.
from app.models import Usuario
from app.models import Sala
from app.models import Aluno


admin.site.register(Usuario)
admin.site.register(Sala)
admin.site.register(Aluno)