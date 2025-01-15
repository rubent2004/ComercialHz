from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Entrega, Recepcion, MovimientoProducto, EstadoProducto

@receiver(post_save, sender=Entrega)
def crear_movimiento_entrega(sender, instance, created, **kwargs):
    if created:
        MovimientoProducto.objects.create(
            bodega=instance.idbodega,
            producto=instance.idproducto,
            tipo_movimiento='salida',
            cantidad=instance.cantidad,
            usuario=instance.id_empleado_autorizo,
            estado_producto=instance.idproducto.estado
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
            estado_producto=instance.idproducto.estado
        )