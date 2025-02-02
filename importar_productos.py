import os
import django
import pandas as pd
from decimal import Decimal

# Configurar Django para que cargue el entorno del proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema.settings')
django.setup()

from inventario.models import Producto  # Asegúrate de importar el modelo correcto

def importar_desde_excel(ruta_archivo):
    # Leer el archivo Excel
    df = pd.read_excel(ruta_archivo)

    # Verificar que las columnas esperadas estén presentes
    columnas_esperadas = ['DESCRIPCION', 'Precio Unitario', 'Precio Cash']
    if not all(col in df.columns for col in columnas_esperadas):
        raise ValueError("El archivo Excel no tiene las columnas esperadas.")

    # Convertir precios a Decimal
    df['Precio Unitario'] = df['Precio Unitario'].apply(
        lambda x: Decimal(str(x).replace('$', '').replace(',', '').strip()) if pd.notnull(x) else None
    )
    df['Precio Cash'] = df['Precio Cash'].apply(
        lambda x: Decimal(str(x).replace('$', '').replace(',', '').strip()) if pd.notnull(x) else None
    )

    # Iterar sobre las filas del DataFrame
    for index, row in df.iterrows():
        producto = Producto.objects.create(
            descripcion=row['DESCRIPCION'],
            precio_unitario=row['Precio Unitario'],
            precio_cash=row['Precio Cash'],
        )
        print(f"Producto creado: {producto.descripcion}")

    print(f"✅ ¡Importación completada! {len(df)} productos procesados.")

if __name__ == "__main__":
    importar_desde_excel(r'PRODUCTOS.xlsx')  # Asegúrate de que el archivo está en la raíz del proyecto
