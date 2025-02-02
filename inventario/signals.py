from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Entrega, Inventario, Recepcion, MovimientoProducto, EstadoProducto

@receiver(post_save, sender=Entrega)
def crear_movimiento_entrega(sender, instance, created, **kwargs):
    if created:
        # Obtener el inventario correspondiente al producto y la bodega
        inventario = Inventario.objects.get(idbodega=instance.idbodega, idproducto=instance.idproducto)
        
        # Crear el movimiento de producto
        MovimientoProducto.objects.create(
            bodega=instance.idbodega,
            producto=instance.idproducto,
            tipo_movimiento='salida',
            cantidad=instance.cantidad,
            usuario=instance.id_empleado_autorizo,
            empleado=instance.id_empleado_recibio,  # Asegúrate de usar el empleado correcto
            estado_producto=inventario.estado  # Usar el estado del inventario
        )

@receiver(post_save, sender=Recepcion)
def crear_movimiento_recepcion(sender, instance, created, **kwargs):
    if created:
        MovimientoProducto.objects.create(
            bodega=instance.idbodega,
            producto=instance.idproducto,
            tipo_movimiento=instance.tipo_recepcion,
            cantidad=instance.cantidad,
            usuario=instance.id_empleado_autorizo,
            empleado_recibio=instance.id_empleado_recibio,
            estado_producto=instance.inventario.estado
        )