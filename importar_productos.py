import os
import django
import pandas as pd
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema.settings')
django.setup()

from inventario.models import Producto
import os

def importar_desde_excel(ruta_archivo):
    # Leer el archivo Excel
    df = pd.read_excel(ruta_archivo)
    
    # Verificar que las columnas esperadas estén presentes
    columnas_esperadas = ['CODIGO', 'DESCRIPCION', 'Precio Unitario', 'Precio Cash']
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
        Producto.objects.update_or_create(
            codigo=str(row['CODIGO']),
            defaults={
                'descripcion': row['DESCRIPCION'],
                'precio_unitario': row['Precio Unitario'],
                'precio_cash': row['Precio Cash'],
                # proveedor y marca se pueden añadir después
            }
        )
    print(f"¡Importación completada! {len(df)} productos procesados.")

if __name__ == "__main__":
    importar_desde_excel(r'PRODUCTOS.xlsx')