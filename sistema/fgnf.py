import os
import sys
from django.conf import settings
from django.utils import timezone

# Agregar la ruta del proyecto al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema.settings')


# Configura Django para acceder a los ajustes
import django
django.setup()

# Ahora puedes usar timezone.now() y timezone.localtime()
fecha_movimiento = timezone.now()
print("Fecha UTC:", fecha_movimiento)

# Convierte la fecha a la zona horaria local definida en TIME_ZONE
fecha_local = timezone.localtime(fecha_movimiento)
print("Fecha local:", fecha_local)

# Imprime la zona horaria actual que Django está usando
print("Zona horaria actual:", timezone.get_current_timezone())

# Ejemplo adicional de obtener la fecha local con la función definida
def obtener_fecha_local():
    return timezone.localtime(timezone.now())

print("FECHAAAAAA: " + str(obtener_fecha_local()))
