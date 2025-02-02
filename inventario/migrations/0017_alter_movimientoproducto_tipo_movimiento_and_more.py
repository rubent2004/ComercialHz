# Generated by Django 5.1.4 on 2025-01-20 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0016_inventario_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movimientoproducto',
            name='tipo_movimiento',
            field=models.CharField(choices=[('entrada', 'Entrada'), ('salida', 'Salida'), ('reparacion', 'Reparacion'), ('devolucion', 'Devolucion'), ('entrega', 'Entrega'), ('recepcion', 'Recepcion'), ('venta', 'Venta'), ('pendiente', 'Pendiente')], max_length=10),
        ),
        migrations.AlterField(
            model_name='recepcion',
            name='tipo_recepcion',
            field=models.CharField(choices=[('vendido', 'Vendido'), ('devuelto', 'Devuelto'), ('recepcion', 'Recepcion')], max_length=9),
        ),
    ]
