import os
import django
import datetime
import pytz  # Asegúrate de tener pytz instalado

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema.settings')
django.setup()

# Importa el modelo de MovimientoProducto
from inventario.models import MovimientoProducto

def listar_movimientos_23_febrero():
    # Configurar la zona horaria (ajusta según tu ubicación)
    zona_horaria = pytz.timezone('America/El_Salvador')  # Cambia a tu zona horaria si es necesario
    
    # Fecha de inicio y fin para el 23 de febrero de 2025
    fecha_inicio = zona_horaria.localize(datetime.datetime(2025, 2, 23, 0, 0, 0))  # 00:00 AM
    fecha_fin = zona_horaria.localize(datetime.datetime(2025, 2, 23, 23, 59, 59))  # 11:59 PM

    try:
        # Obtener los registros de la fecha especificada
        movimientos = MovimientoProducto.objects.filter(
            fecha_movimiento__range=[fecha_inicio, fecha_fin]
        ).order_by('id')

        # Imprimir los resultados
        if movimientos.exists():
            print(f"Registros encontrados para el 23 de febrero de 2025:")
            for movimiento in movimientos:
                print(f"ID: {movimiento.id}, Descripción: {movimiento.descripcion}, Fecha Movimiento: {movimiento.fecha_movimiento}")
        else:
            print("No se encontraron registros para el 23 de febrero de 2025.")

    except Exception as e:
        print(f"Error durante la consulta de movimientos: {e}")

if __name__ == "__main__":
    listar_movimientos_23_febrero()
