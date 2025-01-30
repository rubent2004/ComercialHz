import os
import	django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema.settings')
django.setup()

from inventario.models import Usuario

# Crear un usuario administrador
admin_user = Usuario.objects.create_superuser(
    username="admin",
    email="admin@example.com",
    password="admin",
    first_name="BMartz",
    last_name="BUser",
)

# Asignar nivel 1
admin_user.nivel = 1
admin_user.save()

print("Usuario administrador creado con éxito")
