from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum, Count
from django.db.models.signals import pre_save
from django.dispatch import receiver



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
    def numeroUsuarios(cls, tipo):
        """
        Retorna el número de usuarios según el tipo especificado.
        """
        if tipo == 'administrador':
            return cls.objects.filter(is_superuser=True).count()
        elif tipo == 'usuario' or tipo == 'encargado_bodega':
            return cls.objects.filter(is_superuser=False).count()
        return 0
class Estado(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class EstadoProducto(models.Model):
    DISPONIBLE = 'Disponible'
    DAÑADO = 'Dañado'
    EN_REPARACION = 'En reparación'
    VENDIDO = 'Vendido'
    PENDIENTE = 'Pendiente'

    ESTADO_CHOICES = [
        (DISPONIBLE, 'Disponible'),
        (DAÑADO, 'Dañado'),
        (EN_REPARACION, 'En reparación'),
        (VENDIDO, 'Vendido'),
        (PENDIENTE, 'Pendiente'),
    ]

    nombre = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=DISPONIBLE)

    def __str__(self):
        return self.nombre


#--------------------------------MARCA--------------------------------------------------
class Marca(models.Model):
    """
    Modelo para representar las marcas de los productos.
    """
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
    
#--------------------------------BODEGA-------------------------------------------------
class Bodega(models.Model):
    """
    Modelo para representar las bodegas.
    """
    nombre = models.CharField(max_length=50)
    ubicacion = models.CharField(max_length=50)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre}"


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

#--------------------------------OPCIONES-----------------------------------------------
class Opciones(models.Model):
    """
    Modelo para representar las opciones del sistema.
    """
    moneda = models.CharField(max_length=20, null=True)
    nombre_negocio = models.CharField(max_length=25, null=True)
    mensaje_factura = models.TextField(null=True)

#-------------------------------PRODUCTO------------------------------------------------
class Producto(models.Model):
    descripcion = models.CharField(max_length=40)  # Equivale a 'nombre'
    precio_unitario = models.DecimalField(max_digits=9, decimal_places=2)
    precio_cash = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    codigo = models.CharField(max_length=50, unique=True, null=True)  # Código único basado en el id
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    # Relaciones
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.descripcion} ({self.marca})"

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

#--------------------------------EMPLEADO-----------------------------------------------
class Empleado(models.Model):
    """
    Modelo para representar a los empleados.
    """
    dui = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=40)
    nacimiento = models.DateField()
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(max_length=100)

    @classmethod
    def numeroRegistrados(cls):
        """
        Retorna el número total de empleados registrados.
        """
        return cls.objects.count()

    @classmethod
    def duisRegistradas(cls):
        """
        Retorna una lista de DUIs registrados.
        """
        objetos = cls.objects.all().order_by('nombre')
        arreglo = []
        for indice, objeto in enumerate(objetos):
            arreglo.append([objeto.dui, f"{objeto.nombre} {objeto.apellido}. C.I: {cls.formateardui(objeto.dui)}"])
        return arreglo

    @staticmethod
    def formateardui(dui):
        """
        Formatea el DUI.
        """
        return format(int(dui), ',d')


#--------------------------------FACTURA-----------------------------------------------
class Factura(models.Model):
    """
    Modelo para representar las facturas.
    """
    empleado = models.ForeignKey(Empleado, to_field='dui', on_delete=models.CASCADE)
    fecha = models.DateField()
    sub_monto = models.DecimalField(max_digits=20, decimal_places=2)
    monto_general = models.DecimalField(max_digits=20, decimal_places=2)

    @classmethod
    def numeroRegistrados(cls):
        """
        Retorna el número total de facturas registradas.
        """
        return cls.objects.count()

    @classmethod
    def ingresoTotal(cls):
        """
        Calcula el ingreso total de todas las facturas.
        """
        facturas = cls.objects.all()
        total = sum(factura.monto_general for factura in facturas)
        return total


#--------------------------------DETALLE FACTURA---------------------------------------
class DetalleFactura(models.Model):
    """
    Modelo para representar los detalles de las facturas.
    """
    id_factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    sub_total = models.DecimalField(max_digits=20, decimal_places=2)
    total = models.DecimalField(max_digits=20, decimal_places=2)

    @classmethod
    def productosVendidos(cls):
        """
        Retorna el número total de productos vendidos.
        """
        vendidos = cls.objects.all()
        totalVendidos = sum(producto.cantidad for producto in vendidos)
        return totalVendidos

    @classmethod
    def ultimasVentas(cls):
        """
        Retorna las últimas 10 ventas.
        """
        return cls.objects.all().order_by('-id')[:10]



#--------------------------------INVENTARIO--------------------------------------------
class Inventario(models.Model):
    """
    Modelo para representar el inventario de productos en las bodegas.
    """
    idbodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
    idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    stock = models.IntegerField()
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.ForeignKey(EstadoProducto, on_delete=models.CASCADE)  # Asegúrate de tener esta relación
    @classmethod
    def productosEnBodega(cls):
        """
        Retorna los productos que están en la bodega.
        """
        return cls.objects.filter(producto__estado__nombre='disponible').order_by('producto__descripcion')

    def actualizar_stock(self, cantidad, operacion='reducir'):
        """
        Actualiza el stock del producto en la bodega.
        """
        if operacion == 'reducir':
            self.stock -= cantidad
        elif operacion == 'aumentar':
            self.stock += cantidad
        self.save()

    def reducir_stock(self, cantidad):
        """
        Reduce el stock del producto en la bodega.
        """
        self.actualizar_stock(cantidad, operacion='reducir')

    def aumentar_stock(self, cantidad):
        """
        Aumenta el stock del producto en la bodega.
        """
        self.actualizar_stock(cantidad, operacion='aumentar')

    @classmethod
    def stock_total(cls, producto):
        """
        Calcula la cantidad total de un producto en todas las bodegas.
        """
        total_disponible = cls.objects.filter(producto=producto).aggregate(total=Sum('stock'))['total'] or 0
        total_asignado = MovimientoProducto.objects.filter(producto=producto).aggregate(total=Sum('cantidad'))['total'] or 0
        return total_disponible - total_asignado



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
        ('recepcion', 'Recepcion'),
        ('venta', 'Venta'),
        ('pendiente', 'Pendiente'),
    ]
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO_CHOICES)
    cantidad = models.IntegerField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    estado_producto = models.ForeignKey(EstadoProducto, on_delete=models.CASCADE)

#--------------------------------REGISTRO INVENTARIO------------------------------------
class RegistroInventario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
    estado = models.ForeignKey(EstadoProducto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=0)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.producto.descripcion} - {self.bodega.nombre} ({self.cantidad})"

    def ajustar_stock(self, cantidad):
        """
        Ajusta el stock del producto en la bodega.
        """
        self.cantidad += cantidad
        self.save()

    @classmethod
    def productos_disponibles(cls):
        """
        Retorna todos los productos que están en estado 'Disponible'.
        """
        return cls.objects.filter(estado__nombre=EstadoProducto.DISPONIBLE)

    @classmethod
    def productos_vendidos(cls):
        """
        Retorna todos los productos que están en estado 'Vendido'.
        """
        return cls.objects.filter(estado__nombre=EstadoProducto.VENDIDO)

    @classmethod
    def productos_vendidos_ultimo_mes(cls):
        """
        Retorna todos los productos vendidos en el último mes.
        """
        ultimo_mes = timezone.now() - timedelta(days=30)
        return cls.objects.filter(estado__nombre=EstadoProducto.VENDIDO, fecha_actualizacion__gte=ultimo_mes)

    @classmethod
    def productos_mas_vendidos(cls):
        """
        Retorna los productos más vendidos.
        """
        return cls.objects.filter(estado__nombre=EstadoProducto.VENDIDO).annotate(total_vendidos=Count('producto')).order_by('-total_vendidos')

#--------------------------------REPARACION--------------------------------------------
class Reparacion(models.Model):
    """
    Modelo para representar las reparaciones de productos.
    """
    idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    descripcion_problema = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_retorno = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=9, choices=[('pendiente', 'Pendiente'), ('reparado', 'Reparado')], default='pendiente')

#--------------------------------DEVOLUCION--------------------------------------------
class Devolucion(models.Model):
    """
    Modelo para representar las devoluciones de productos.
    """
    idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    idempleado = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    motivo = models.TextField()
    fecha_devolucion = models.DateTimeField(auto_now_add=True)

#--------------------------------ENTREGA------------------------------------------------
class Entrega(models.Model):
    idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    idbodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
    id_empleado_autorizo = models.ForeignKey(Usuario, related_name='autorizo_entregas', on_delete=models.CASCADE)
    id_empleado_recibio = models.ForeignKey(Empleado, related_name='recibio_entregas', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    fecha_entrega = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")

        inventario = Inventario.objects.get(bodega=self.idbodega, producto=self.idproducto)
        if inventario.stock < self.cantidad:
            raise ValidationError("No hay suficiente stock en la bodega.")
        inventario.reducir_stock(self.cantidad)

        if self.idproducto.estado.nombre != 'Vendido':
            estado_pendiente = EstadoProducto.objects.get(nombre='Pendiente')
            self.idproducto.estado = estado_pendiente
            self.idproducto.save()

        MovimientoProducto.objects.create(
            bodega=self.idbodega,
            producto=self.idproducto,
            tipo_movimiento='salida',
            cantidad=self.cantidad,
            usuario=self.id_empleado_autorizo,
            estado_producto=self.idproducto.estado
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Entrega de {self.cantidad} {self.idproducto.descripcion} desde {self.idbodega.nombre}"

#--------------------------------RECEPCION----------------------------------------------
class Recepcion(models.Model):
    TIPO_RECEPCION_CHOICES = [
        ('vendido', 'Vendido'),
        ('devuelto', 'Devuelto'),
        ('recepcion', 'Recepcion'),
    ]
    idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    idbodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
    id_empleado_autorizo = models.ForeignKey(Usuario, related_name='autorizo_recepciones', on_delete=models.CASCADE)
    id_empleado_recibio = models.ForeignKey(Usuario, related_name='recibio_recepciones', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    tipo_recepcion = models.CharField(max_length=9, choices=TIPO_RECEPCION_CHOICES)
    fecha_recepcion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")

        if self.tipo_recepcion == 'devuelto':
            inventario = Inventario.objects.get(bodega=self.idbodega, producto=self.idproducto)
            inventario.aumentar_stock(self.cantidad)
            self.idproducto.estado= EstadoProducto.objects.get(nombre='Disponible')
            self.idproducto.save()


        MovimientoProducto.objects.create(
            bodega=self.idbodega,
            producto=self.idproducto,
            tipo_movimiento='entrada',
            cantidad=self.cantidad,
            usuario=self.id_empleado_autorizo,
            estado_producto=self.idproducto.estado
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Recepción de {self.cantidad} {self.idproducto.descripcion} en {self.idbodega.nombre}"