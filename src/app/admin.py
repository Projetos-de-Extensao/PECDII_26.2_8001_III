from django.contrib import admin

# Import your models here.
from app.models import Usuario
from app.models import Sala


admin.site.register(Usuario)
admin.site.register(Sala)