from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError
from django.urls import reverse



# MODELOS

#--------------------------------USUARIO------------------------------------------------
class Usuario(AbstractUser):
    #id
    username = models.CharField(max_length=80, unique=True)
    password = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=60)
    nivel = models.IntegerField(null=True) 

    @classmethod
    def numeroRegistrados(self):
        return int(self.objects.all().count() )   

    @classmethod
    def numeroUsuarios(self,tipo):
        if tipo == 'administrador':
            return int(self.objects.filter(is_superuser = True).count() )
        elif tipo == 'usuario':
            return int(self.objects.filter(is_superuser = False).count() )
        elif tipo == 'encargado_bodega':
            return int(self.objects.filter(is_superuser = False).count() )

class Estado(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class EstadoProducto(models.Model):
    nombre = models.CharField(max_length=255)
    def __str__(self):
        return self.nombre

class Marca(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

# Modelo Bodega
class Bodega(models.Model):
    nombre = models.CharField(max_length=50)
    ubicacion = models.CharField(max_length=50)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)

    def __str__(self):
        #agregar fecha_registro automaticamente

        return f"{self.nombre} - {self.fecha_registro}"


#------------------------------------------PROVEEDOR-----------------------------------
# models.py
class Proveedor(models.Model):
    # id
    dui = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=40)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    correo = models.CharField(max_length=100)

    @classmethod
    def duisRegistradas(self):
        objetos = self.objects.all().order_by('nombre')
        arreglo = []
        for indice, objeto in enumerate(objetos):
            arreglo.append([])
            arreglo[indice].append(objeto.dui)
            nombre_empleado = objeto.nombre + " " + objeto.empleado
            arreglo[indice].append("%s. C.I: %s" % (nombre_empleado, self.formateardui(objeto.dui)))
        return arreglo

    @staticmethod
    def formateardui(dui):
        return format(int(dui), ',d')

    def __str__(self):
        # Aquí puedes retornar lo que desees, por ejemplo el nombre y apellido
        return f"{self.nombre} {self.apellido}"  # Se mostrará nombre y apellido del proveedor

    
#---------------------------------------------------------------------------------------    
class Opciones(models.Model):
    #id
    moneda = models.CharField(max_length=20, null=True)
    nombre_negocio = models.CharField(max_length=25,null=True)
    mensaje_factura = models.TextField(null=True)

#---------------------------------------------------------------------------------------

 
#-------------------------------PRODUCTO------------------------------------------------

   # Modelo Producto
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
#from django.urls import reverse


class Producto(models.Model):
    descripcion = models.CharField(max_length=40)  # Equivale a 'nombre'
    precio_unitario = models.DecimalField(max_digits=9, decimal_places=2)
    precio_cash = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    codigo = models.CharField(max_length=50, unique=True, null=True)  # Código único basado en el id
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    # Relaciones
    proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE)
    marca = models.ForeignKey('Marca', on_delete=models.CASCADE)

    def __str__(self):
        return self.descripcion

    @classmethod
    def numeroRegistrados(cls):
        return cls.objects.all().count()

    @classmethod
    def productosRegistrados(cls):
        return cls.objects.all().order_by('descripcion')

    @classmethod
    def preciosProductos(cls):
        objetos = cls.objects.all().order_by('id')
        arreglo = []
        etiqueta = True
        extra = 1

        for indice, objeto in enumerate(objetos):
            arreglo.append([])
            if etiqueta:
                arreglo[indice].append(0)
                arreglo[indice].append("------")
                etiqueta = False
                arreglo.append([])

            arreglo[indice + extra].append(objeto.id)
            precio_producto = objeto.precio_unitario
            arreglo[indice + extra].append("%d" % (precio_producto))

        return arreglo

    @classmethod
    def productosDisponibles(cls):
        objetos = cls.objects.all().order_by('id')
        arreglo = []
        etiqueta = True
        extra = 1

        for indice, objeto in enumerate(objetos):
            arreglo.append([])
            if etiqueta:
                arreglo[indice].append(0)
                arreglo[indice].append("------")
                etiqueta = False
                arreglo.append([])

            arreglo[indice + extra].append(objeto.id)
            productos_disponibles = objeto.disponible
            arreglo[indice + extra].append("%d" % (productos_disponibles))  

        return arreglo

# Señal para autogenerar el código cuando el producto es guardado
@receiver(pre_save, sender=Producto)
def asignar_codigo(sender, instance, **kwargs):
    if not instance.codigo:  # Solo genera el código si aún no tiene uno asignado
        ultimo_id = Producto.objects.count() + 1  # Incrementa el ID actual
        instance.codigo = f"{ultimo_id:07d}"  # Genera un código como 0000001, 0000002, etc.

#---------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------


#------------------------------------------CLIENTE--------------------------------------
class Empleado(models.Model):
    #id
    dui = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=40)
    nacimiento = models.DateField()
    telefono = models.CharField(max_length=20)
    correo = models.CharField(max_length=100)

    @classmethod
    def numeroRegistrados(self):
        return int(self.objects.all().count() )

    @classmethod
    def duisRegistradas(self):
        objetos = self.objects.all().order_by('nombre')
        arreglo = []
        for indice,objeto in enumerate(objetos):
            arreglo.append([])
            arreglo[indice].append(objeto.dui)
            nombre_empleado = objeto.nombre + " " + objeto.apellido
            arreglo[indice].append("%s. C.I: %s" % (nombre_empleado,self.formateardui(objeto.dui)) )
 
        return arreglo   


    @staticmethod
    def formateardui(dui):
        return format(int(dui), ',d')        
#-----------------------------------------------------------------------------------------        



# #-------------------------------------FACTURA---------------------------------------------
class Factura(models.Model):
    #id
    empleado = models.ForeignKey(Empleado,to_field='dui', on_delete=models.CASCADE)
    fecha = models.DateField()
    sub_monto = models.DecimalField(max_digits=20,decimal_places=2)
    monto_general = models.DecimalField(max_digits=20,decimal_places=2)

    @classmethod
    def numeroRegistrados(self):
        return int(self.objects.all().count() )

    @classmethod
    def ingresoTotal(self):
        facturas = self.objects.all()
        total = 0

        for factura in facturas:
            total += factura.monto_general

        return total
# #-----------------------------------------------------------------------------------------


# #-------------------------------------DETALLES DE FACTURA---------------------------------
class DetalleFactura(models.Model):
    #id
    id_factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    sub_total = models.DecimalField(max_digits=20,decimal_places=2)
    total = models.DecimalField(max_digits=20,decimal_places=2)

    @classmethod
    def productosVendidos(self):
        vendidos = self.objects.all()
        totalVendidos = 0
        for producto in vendidos:
            totalVendidos += producto.cantidad

        return totalVendidos  

    @classmethod
    def ultimasVentas(self):
        objetos = self.objects.all().order_by('-id')[:10]

        return objetos
# #---------------------------------------------------------------------------------------
# Modelo Estado



#----------------------------------------PEDIDO-----------------------------------------
class Inventario(models.Model):
    idbodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
    idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    stock = models.IntegerField()
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    @classmethod
    def productosEnBodega(cls):
        return cls.objects.filter(producto__estado__nombre='en_bodega').order_by('producto__descripcion')

    def actualizar_stock(self, cantidad, operacion='reducir'):
        if operacion == 'reducir':
            self.stock -= cantidad
        elif operacion == 'aumentar':
            self.stock += cantidad
        self.save()

    def reducir_stock(self, cantidad):
        self.actualizar_stock(cantidad, operacion='reducir')

    def aumentar_stock(self, cantidad):
        self.actualizar_stock(cantidad, operacion='aumentar')


class Compra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha = models.DateField()
    sub_monto = models.DecimalField(max_digits=20, decimal_places=2)
    monto_general = models.DecimalField(max_digits=20, decimal_places=2)

    def procesar_compra(self):
        for item in self.items.all():
            inventario, created = Inventario.objects.get_or_create(
                idbodega=item.bodega,
                idproducto=item.producto,
                defaults={'stock': 0}
            )
            inventario.aumentar_stock(item.cantidad)
            estado_bodega = EstadoProducto.objects.get(nombre='en_bodega')
            item.producto.estado = estado_bodega
            item.producto.save()

class CompraItem(models.Model):
    compra = models.ForeignKey(Compra, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

#---------------------------------------------------------------------------------------    


#-------------------------------------DETALLES DE PEDIDO-------------------------------
class DetalleCompra(models.Model):
    #id
    id_compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    sub_total = models.DecimalField(max_digits=20,decimal_places=2)
    total = models.DecimalField(max_digits=20,decimal_places=2)
#---------------------------------------------------------------------------------------


#------------------------------------NOTIFICACIONES------------------------------------
class Notificaciones(models.Model):
    #id
    autor = models.ForeignKey(Usuario,to_field='username', on_delete=models.CASCADE)
    mensaje = models.TextField()
#---------------------------------------------------------------------------------------

class MovimientoProducto(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('reparacion', 'Reparacion'),
        ('devolucion', 'Devolucion'),
        ('entrega', 'Entrega'),
        ('pendiente', 'Pendiente'),
    ]
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO_CHOICES)
    cantidad = models.IntegerField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    estado_producto = models.ForeignKey(EstadoProducto, on_delete=models.CASCADE)

class Reparacion(models.Model):
    idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    descripcion_problema = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_retorno = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=9, choices=[('pendiente', 'Pendiente'), ('reparado', 'Reparado')], default='pendiente')

class Devolucion(models.Model):
    idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    idempleado = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    motivo = models.TextField()
    fecha_devolucion = models.DateTimeField(auto_now_add=True)

class Entrega(models.Model):
    idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    idbodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
    id_empleado_autorizo = models.ForeignKey(Usuario, related_name='autorizo_entregas', on_delete=models.CASCADE)
    id_empleado_recibio = models.ForeignKey(Usuario, related_name='recibio_entregas', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    fecha_entrega = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Validar que la cantidad no sea negativa
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")

        # Reducir el stock en la bodega
        inventario = Inventario.objects.get(bodega=self.bodega, producto=self.producto)
        if inventario.stock < self.cantidad:
            raise ValidationError("No hay suficiente stock en la bodega.")
        inventario.reducir_stock(self.cantidad)

        # Actualizar el estado del producto a "pendiente"
        estado_pendiente = EstadoProducto.objects.get(nombre='pendiente')
        # Crear un movimiento de producto
        MovimientoProducto.objects.create(
            bodega=self.idbodega,
            producto=self.idproducto,
            tipo_movimiento='salida',
            cantidad=self.cantidad,
            usuario=self.id_empleado_autorizo,
            estado_producto=self.idproducto.estado
        )
        self.producto.estado = estado_pendiente
        self.producto.save()

        super().save(*args, **kwargs)

class Recepcion(models.Model):
    TIPO_RECEPCION_CHOICES = [
        ('vendido', 'Vendido'),
        ('devuelto', 'Devuelto'),
    ]
    idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    idbodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
    id_empleado_autorizo = models.ForeignKey(Usuario, related_name='autorizo_recepciones', on_delete=models.CASCADE)
    id_empleado_devolvio = models.ForeignKey(Usuario, related_name='devolvio_recepciones', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    tipo_recepcion = models.CharField(max_length=8, choices=TIPO_RECEPCION_CHOICES)
    fecha_recepcion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Validar que la cantidad no sea negativa
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")

        # Actualizar el estado del producto según el tipo de recepción
        if self.tipo_recepcion == 'vendido':
            estado_vendido = EstadoProducto.objects.get(nombre='vendido')
            self.producto.estado = estado_vendido
        elif self.tipo_recepcion == 'devuelto':
            estado_bodega = EstadoProducto.objects.get(nombre='en_bodega')
            self.producto.estado = estado_bodega

            # Aumentar el stock en la bodega
            inventario = Inventario.objects.get_or_create(bodega=self.bodega, producto=self.producto, defaults={'stock': 0})
            # Crear un movimiento de producto
            MovimientoProducto.objects.create(
                bodega=self.idbodega,
                producto=self.idproducto,
                tipo_movimiento=self.tipo_recepcion,
                cantidad=self.cantidad,
                usuario=self.id_empleado_autorizo,
                estado_producto=self.idproducto.estado
            )
            inventario.aumentar_stock(self.cantidad)

        self.producto.save()
        super().save(*args, **kwargs)
