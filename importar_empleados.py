import os
import django
import pandas as pd

# Configurar Django para que cargue el entorno del proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema.settings')
django.setup()

from inventario.models import Empleado, Estado  # Asegúrate de importar el modelo correcto

def importar_empleados(ruta_archivo):
    # Leer el archivo Excel
    df = pd.read_excel(ruta_archivo)

    # Verificar que las columnas esperadas estén presentes
    columnas_esperadas = ['N° DE EMPLEADO', 'NOMBRE DE EMPLEADO', 'DUI']
    if not all(col in df.columns for col in columnas_esperadas):
        raise ValueError("El archivo Excel no tiene las columnas esperadas.")

    # Iterar sobre las filas del DataFrame
    for index, row in df.iterrows():
        # Obtener el código del empleado (N° DE EMPLEADO) y limpiarlo
        empleado_codigo = str(row['N° DE EMPLEADO']).strip()

        # Obtener el nombre completo y limpiarlo
        nombre_completo = str(row['NOMBRE DE EMPLEADO']).strip()

        # Obtener el DUI, validando que no esté vacío
        dui = str(row['DUI']).strip() if pd.notnull(row['DUI']) and str(row['DUI']).strip() != '' else None
        if not dui:
            print(f"Fila {index}: DUI ausente, se omite.")
            continue

        # Dividir el nombre completo: la primera palabra se asigna a 'nombre' y el resto a 'apellido'
        parts = nombre_completo.split()
        if len(parts) >= 2:
            nombre = parts[0]
            apellido = " ".join(parts[1:])
        else:
            nombre = nombre_completo
            apellido = ""

        # Convertir el número de empleado a entero para usarlo como id
        try:
            empleado_id = int(empleado_codigo)
        except ValueError:
            print(f"Fila {index}: N° DE EMPLEADO inválido: {empleado_codigo}. Se omite.")
            continue

        # Actualiza o crea el empleado utilizando el campo 'id'
        empleado, created = Empleado.objects.update_or_create(
            id=empleado_id,
            defaults={
                'codigo': empleado_codigo,  # Guarda el número en el campo 'codigo'
                'dui': dui,
                'nombre': nombre,
                'apellido': apellido,
                'nacimiento': None,    # No se proporciona en el Excel
                'telefono': None,      # No se proporciona en el Excel
                'correo': None,        # No se proporciona en el Excel
                'estado_id': 1,        # Se asume que el estado por defecto es el de ID=1
            }
        )

        if created:
            print(f"Empleado creado: {empleado}")
        else:
            print(f"Empleado actualizado: {empleado}")

    print(f"✅ ¡Importación completada! {len(df)} empleados procesados.")

if __name__ == "__main__":
    importar_empleados(r'EMPLEADOS.xlsx')  # Asegúrate de que el archivo se encuentre en la ruta correcta
