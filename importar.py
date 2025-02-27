import os
import django
import pandas as pd
import logging
from django.db import transaction
from django.apps import apps

# Configurar el logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Configurar Django para que cargue el entorno del proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema.settings')
django.setup()

# Función para obtener el modelo correspondiente por el nombre de la tabla
def obtener_modelo_por_tabla(nombre_tabla):
    try:
        # Buscar el modelo en las aplicaciones instaladas
        modelo = apps.get_model('inventario', nombre_tabla)
        return modelo
    except LookupError:
        logger.error(f"No se encontró el modelo para la tabla: {nombre_tabla}")
        return None

# Función para importar todos los datos desde un archivo Excel
def importar_todas_las_tablas_desde_excel(ruta_archivo):
    """
    Importa todos los datos desde un archivo Excel donde cada hoja es una tabla.
    Los nombres de las hojas deben coincidir con los nombres de los modelos de Django.
    """
    # Verificar existencia del archivo
    if not os.path.exists(ruta_archivo):
        logger.error(f"El archivo '{ruta_archivo}' no existe.")
        return

    try:
        # Leer el archivo Excel
        df = pd.read_excel(ruta_archivo, sheet_name=None)  # Lee todas las hojas
    except Exception as e:
        logger.error(f"Error al leer el archivo Excel: {e}")
        return

    total_procesados = 0
    total_creados = 0
    total_actualizados = 0

    # Iterar sobre cada hoja
    for nombre_hoja, data in df.items():
        logger.info(f"Importando datos para la tabla '{nombre_hoja}'...")
        # Obtener el modelo correspondiente al nombre de la hoja
        modelo = obtener_modelo_por_tabla(nombre_hoja)

        if modelo is None:
            continue

        # Procesar cada fila de la hoja
        for index, row in data.iterrows():
            try:
                # Creamos un diccionario con los valores de la fila
                row_dict = row.to_dict()

                with transaction.atomic():
                    # Usar update_or_create para evitar duplicados y actualizar datos
                    objeto, creado = modelo.objects.update_or_create(
                        **{modelo._meta.pk.name: row_dict[modelo._meta.pk.name]},
                        defaults=row_dict
                    )
                    
                if creado:
                    total_creados += 1
                    logger.info(f"Registro creado en {nombre_hoja}: {objeto}")
                else:
                    total_actualizados += 1
                    logger.info(f"Registro actualizado en {nombre_hoja}: {objeto}")

                total_procesados += 1
            except Exception as e:
                logger.error(f"Error al procesar la fila {index} de la tabla {nombre_hoja}: {e}")
                continue

    logger.info(f"✅ ¡Importación completada! Total registros procesados: {total_procesados}. "
                f"Creados: {total_creados}, Actualizados: {total_actualizados}")

if __name__ == "__main__":
    importar_todas_las_tablas_desde_excel(r'export.xlsx')
