# from django.db import models
# from django.contrib.auth.models import AbstractUser
# from django.forms import ValidationError

# from inventario.models import Usuario
# # Create your models here.

# # Modelo Estado
# class Estado(models.Model):
#     estado = models.CharField(max_length=50)

#     def __str__(self):
#         return self.estado


# # Modelo Categoría
# class Categoria(models.Model):
#     nombre = models.CharField(max_length=50)

#     def __str__(self):
#         return self.nombre

# class EstadoProducto(models.Model):
#     nombre = models.CharField(max_length=255)
#     def __str__(self):
#         return self.nombre

# class Marca(models.Model):
#     marca = models.CharField(max_length=50)

#     def __str__(self):
#         return self.nombre

# # Modelo Bodega
# class Bodega(models.Model):
#     nombre = models.CharField(max_length=50)
#     ubicacion = models.CharField(max_length=50)
#     fecha_registro = models.DateTimeField(auto_now_add=True)
#     estado = models.ForeignKey(Estado, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.nombre


# class Proveedor(models.Model):
#     #id
#     nombre = models.CharField(max_length=40, unique=True)
#     apellido = models.CharField(max_length=40)
#     direccion = models.CharField(max_length=200)
#     telefono = models.CharField(max_length=20, null=True)
#     correo = models.CharField(max_length=100, null=True)
#     def __str__(self):
#             return self.nombre

    
# #---------------------------------------------------------------------------------------    

#    # Modelo Producto
# class Producto(models.Model):
#     descripcion = models.CharField(max_length=40)  # Equivale a 'nombre'
#     precio_unitario = models.DecimalField(max_digits=9, decimal_places=2)
#     precio_cash = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
#     codigo = models.CharField(max_length=50, unique=True)
#     fecha_registro = models.DateTimeField(auto_now_add=True)
#     disponible = models.IntegerField(null=True, default=0)  # Calculado a partir de Inventario
#     imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

#     # Relaciones
#     categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
#     proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
#     marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
#     estado = models.ForeignKey(EstadoProducto, on_delete=models.CASCADE)  # Estado del producto

#     def __str__(self):
#         return self.descripcion

#     @classmethod
#     def numeroRegistrados(cls):
#         return cls.objects.all().count()

#     @classmethod
#     def productosRegistrados(cls):
#         return cls.objects.all().order_by('descripcion')

#     @classmethod
#     def preciosProductos(cls):
#         objetos = cls.objects.all().order_by('id')
#         arreglo = []
#         etiqueta = True
#         extra = 1

#         for indice, objeto in enumerate(objetos):
#             arreglo.append([])
#             if etiqueta:
#                 arreglo[indice].append(0)
#                 arreglo[indice].append("------")
#                 etiqueta = False
#                 arreglo.append([])

#             arreglo[indice + extra].append(objeto.id)
#             precio_producto = objeto.precio_unitario
#             arreglo[indice + extra].append("%d" % (precio_producto))

#         return arreglo
#     @classmethod
#     def productosDisponibles(self):
#         objetos = self.objects.all().order_by('id')
#         arreglo = []
#         etiqueta = True
#         extra = 1

#         for indice,objeto in enumerate(objetos):
#             arreglo.append([])
#             if etiqueta:
#                 arreglo[indice].append(0)
#                 arreglo[indice].append("------")
#                 etiqueta = False
#                 arreglo.append([])

#             arreglo[indice + extra].append(objeto.id)
#             productos_disponibles = objeto.disponible
#             arreglo[indice + extra].append("%d" % (productos_disponibles) )  

#         return arreglo 
# #---------------------------------------------------------------------------------------


# class Pedido(models.Model):
#     proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
#     fecha = models.DateField()
#     sub_monto = models.DecimalField(max_digits=20, decimal_places=2)
#     monto_general = models.DecimalField(max_digits=20, decimal_places=2)
#     presente = models.BooleanField(null=True)

#     def procesar_pedido(self):
#         # Asumiendo que tienes una relación de muchos a muchos entre Pedido y Producto
#         for item in self.items.all():
#             inventario, created = Inventario.objects.get_or_create(
#                 bodega=item.bodega,
#                 producto=item.producto,
#                 defaults={'stock': 0}
#             )
#             inventario.aumentar_stock(item.cantidad)

# class PedidoItem(models.Model):
#     pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
#     producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
#     bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
#     cantidad = models.IntegerField()

# class Inventario(models.Model):
#     idbodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
#     idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
#     stock = models.IntegerField()
#     fecha_actualizacion = models.DateTimeField(auto_now=True)
    
#     @classmethod
#     def productosEnBodega(cls):
#         return cls.objects.filter(producto__estado__nombre='en_bodega').order_by('producto__descripcion')

#     def actualizar_stock(self, cantidad, operacion='reducir'):
#         if operacion == 'reducir':
#             self.stock -= cantidad
#         elif operacion == 'aumentar':
#             self.stock += cantidad
#         self.save()

#     def reducir_stock(self, cantidad):
#         self.actualizar_stock(cantidad, operacion='reducir')

#     def aumentar_stock(self, cantidad):
#         self.actualizar_stock(cantidad, operacion='aumentar')

# class MovimientoProducto(models.Model):
#     TIPO_MOVIMIENTO_CHOICES = [
#         ('entrada', 'Entrada'),
#         ('salida', 'Salida'),
#         ('reparacion', 'Reparacion'),
#         ('devolucion', 'Devolucion'),
#         ('entrega', 'Entrega'),
#         ('pendiente', 'Pendiente'),
#     ]
#     bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
#     producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
#     tipo_movimiento = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO_CHOICES)
#     cantidad = models.IntegerField()
#     usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
#     fecha_movimiento = models.DateTimeField(auto_now_add=True)
#     estado_producto = models.ForeignKey(EstadoProducto, on_delete=models.CASCADE)

# class Reparacion(models.Model):
#     idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
#     descripcion_problema = models.TextField()
#     fecha_envio = models.DateTimeField(auto_now_add=True)
#     fecha_retorno = models.DateTimeField(null=True, blank=True)
#     estado = models.CharField(max_length=9, choices=[('pendiente', 'Pendiente'), ('reparado', 'Reparado')], default='pendiente')

# class Devolucion(models.Model):
#     idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
#     idempleado = models.ForeignKey(Usuario, on_delete=models.CASCADE)
#     motivo = models.TextField()
#     fecha_devolucion = models.DateTimeField(auto_now_add=True)

# class Entrega(models.Model):
#     idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
#     idbodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
#     id_empleado_autorizo = models.ForeignKey(Usuario, related_name='autorizo_entregas', on_delete=models.CASCADE)
#     id_empleado_recibio = models.ForeignKey(Usuario, related_name='recibio_entregas', on_delete=models.CASCADE)
#     cantidad = models.IntegerField()
#     fecha_entrega = models.DateTimeField(auto_now_add=True)

#     def save(self, *args, **kwargs):
#         # Validar que la cantidad no sea negativa
#         if self.cantidad <= 0:
#             raise ValidationError("La cantidad debe ser mayor que cero.")

#         # Reducir el stock en la bodega
#         inventario = Inventario.objects.get(bodega=self.bodega, producto=self.producto)
#         if inventario.stock < self.cantidad:
#             raise ValidationError("No hay suficiente stock en la bodega.")
#         inventario.reducir_stock(self.cantidad)

#         # Actualizar el estado del producto a "pendiente"
#         estado_pendiente = EstadoProducto.objects.get(nombre='pendiente')
#         self.producto.estado = estado_pendiente
#         self.producto.save()

#         super().save(*args, **kwargs)

# class Recepcion(models.Model):
#     TIPO_RECEPCION_CHOICES = [
#         ('vendido', 'Vendido'),
#         ('devuelto', 'Devuelto'),
#     ]
#     idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
#     idbodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
#     id_empleado_autorizo = models.ForeignKey(Usuario, related_name='autorizo_recepciones', on_delete=models.CASCADE)
#     id_empleado_devolvio = models.ForeignKey(Usuario, related_name='devolvio_recepciones', on_delete=models.CASCADE)
#     cantidad = models.IntegerField()
#     tipo_recepcion = models.CharField(max_length=8, choices=TIPO_RECEPCION_CHOICES)
#     fecha_recepcion = models.DateTimeField(auto_now_add=True)

#     def save(self, *args, **kwargs):
#         # Validar que la cantidad no sea negativa
#         if self.cantidad <= 0:
#             raise ValidationError("La cantidad debe ser mayor que cero.")

#         # Actualizar el estado del producto según el tipo de recepción
#         if self.tipo_recepcion == 'vendido':
#             estado_vendido = EstadoProducto.objects.get(nombre='vendido')
#             self.producto.estado = estado_vendido
#         elif self.tipo_recepcion == 'devuelto':
#             estado_bodega = EstadoProducto.objects.get(nombre='en_bodega')
#             self.producto.estado = estado_bodega

#             # Aumentar el stock en la bodega
#             inventario = Inventario.objects.get_or_create(bodega=self.bodega, producto=self.producto, defaults={'stock': 0})
#             inventario.aumentar_stock(self.cantidad)

#         self.producto.save()
#         super().save(*args, **kwargs)

# class Opciones(models.Model):
#     nombre = models.CharField(max_length=100)
#     valor = models.CharField(max_length=100)

#     def __str__(self):
#         return self.nombre