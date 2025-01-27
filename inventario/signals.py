from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Entrega, Inventario,  MovimientoProducto, EstadoProducto

@receiver(post_save, sender=Entrega)
def crear_movimiento_entrega(sender, instance, created, **kwargs):
    if created:
        # Obtener el inventario correspondiente al producto y la bodega
        inventario = Inventario.objects.get(idbodega=instance.idbodega, idproducto=instance.idproducto)
         # Obtener el estado "Pendiente"
        estado_pendiente = EstadoProducto.objects.get(nombre=EstadoProducto.PENDIENTE)

        # Crear el movimiento de producto
        MovimientoProducto.objects.create(
            bodega=instance.idbodega,
            producto=instance.idproducto,
            cantidad=instance.cantidad,
            usuario=instance.id_empleado_autorizo,
            empleado=instance.id_empleado_recibio,  # Asegúrate de usar el empleado correcto
            estado_producto= estado_pendiente # Usar el estado del inventario
        )

