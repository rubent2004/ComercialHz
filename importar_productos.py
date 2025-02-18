import os
import django
import pandas as pd
from decimal import Decimal, InvalidOperation
import logging
from django.db import transaction

# Configurar el logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Configurar Django para que cargue el entorno del proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema.settings')
django.setup()

from inventario.models import Producto  # Asegúrate de importar el modelo correcto

def convertir_decimal(valor):
    """
    Convierte un valor a Decimal, eliminando caracteres especiales como '$' y ','.
    Retorna None si el valor es nulo o no se puede convertir.
    """
    if pd.isnull(valor):
        return None
    try:
        valor_str = str(valor).replace('$', '').replace(',', '').strip()
        return Decimal(valor_str)
    except (InvalidOperation, ValueError) as e:
        logger.error(f"Error al convertir '{valor}' a Decimal: {e}")
        return None

def importar_desde_excel(ruta_archivo):
    """
    Importa productos desde un archivo Excel.
    - Se espera que el Excel tenga las columnas: 'ID', 'DESCRIPCION', 'Precio Unitario', 'Precio Cash'.
    - Si un producto con el mismo ID ya existe, se actualiza con la información del Excel.
    - Se utiliza una transacción por cada fila para garantizar la integridad de la base de datos.
    """
    # Verificar existencia del archivo
    if not os.path.exists(ruta_archivo):
        logger.error(f"El archivo '{ruta_archivo}' no existe.")
        return

    # Intentar leer el archivo Excel
    try:
        df = pd.read_excel(ruta_archivo)
    except Exception as e:
        logger.error(f"Error al leer el archivo Excel: {e}")
        return

    # Verificar que el archivo contenga las columnas esperadas
    columnas_esperadas = ['ID', 'DESCRIPCION', 'Precio Unitario', 'Precio Cash']
    if not all(col in df.columns for col in columnas_esperadas):
        logger.error("El archivo Excel no tiene las columnas esperadas: " + ", ".join(columnas_esperadas))
        return

    # Convertir las columnas de precio a Decimal
    df['Precio Unitario'] = df['Precio Unitario'].apply(convertir_decimal)
    df['Precio Cash'] = df['Precio Cash'].apply(convertir_decimal)

    total_procesados = 0
    total_creados = 0
    total_actualizados = 0

    # Procesar cada fila del DataFrame
    for index, row in df.iterrows():
        producto_id = row['ID']
        descripcion = row['DESCRIPCION']
        precio_unitario = row['Precio Unitario']
        precio_cash = row['Precio Cash']

        try:
            with transaction.atomic():
                # update_or_create prioriza la información del Excel: si existe, se actualiza;
                # si no, se crea.
                producto, creado = Producto.objects.update_or_create(
                    id=producto_id,
                    defaults={
                        'descripcion': descripcion,
                        'precio_unitario': precio_unitario,
                        'precio_cash': precio_cash,
                    }
                )
            if creado:
                total_creados += 1
                logger.info(f"Producto creado: {producto.descripcion} (ID: {producto_id})")
            else:
                total_actualizados += 1
                logger.info(f"Producto actualizado: {producto.descripcion} (ID: {producto_id})")
            total_procesados += 1
        except Exception as e:
            logger.error(f"Error procesando el producto con ID '{producto_id}': {e}")
            # Se continúa con el siguiente producto sin detener toda la importación.
            continue

    logger.info(f"✅ ¡Importación completada! Total productos procesados: {total_procesados}. "
                f"Creados: {total_creados}, Actualizados: {total_actualizados}")

if __name__ == "__main__":
    importar_desde_excel(r'PRODUCTOS.xlsx')
