from datetime import timedelta
from gettext import translation

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum, Count
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models.signals import post_migrate



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

    #si es admin sera nivel 1 si es usurio nivel 2 

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
        elif tipo == 'usuario':
            return cls.objects.filter(is_superuser=False).count()
        return 0
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class Estado(models.Model):
    ACTIVO = 'Activo'
    INACTIVO = 'Inactivo'

    ESTADO_CHOICES = [
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
    ]

    nombre = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ACTIVO)

    def __str__(self):
        return self.nombre

    # Señal para agregar estados predeterminados
    @receiver(post_migrate)
    def crear_estados_predeterminados(sender, **kwargs):
        # Establece los valores predeterminados para 'Activo' e 'Inactivo'
        estados = [Estado.ACTIVO, Estado.INACTIVO]
        for estado in estados:
            Estado.objects.get_or_create(nombre=estado)

#--------------------------------ESTADO PRODUCTO----------------------------------------


class EstadoProducto(models.Model):
    DISPONIBLE = 'Disponible'
    DAÑADO = 'Dañado'
    EN_REPARACION = 'En reparación'
    REPARADO = 'Reparado'
    VENDIDO = 'Vendido'
    PENDIENTE = 'Pendiente'

    ESTADO_CHOICES = [
        (DISPONIBLE, 'Disponible'),
        (DAÑADO, 'Dañado'),
        (EN_REPARACION, 'En reparación'),
        (REPARADO, 'Reparado'),
        (VENDIDO, 'Vendido'),
        (PENDIENTE, 'Pendiente'),
    ]

    nombre = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=DISPONIBLE)

    def __str__(self):
        return self.nombre

    # Señal para agregar estados predeterminados
    @receiver(post_migrate)
    def crear_estados_predeterminados(sender, **kwargs):
        estados = [EstadoProducto.DISPONIBLE, EstadoProducto.DAÑADO, EstadoProducto.EN_REPARACION, EstadoProducto.VENDIDO, EstadoProducto.PENDIENTE,EstadoProducto.REPARADO]
        for estado in estados:
            EstadoProducto.objects.get_or_create(nombre=estado)

    # Método para contar los productos vendidos
    @classmethod
    def productos_vendidos(cls):
        """
        Retorna el número total de productos que están en estado 'Vendido'.
        """
        return RegistroInventario.objects.filter(estado__nombre=EstadoProducto.VENDIDO).count()

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

    @classmethod
    def numeroRegistrados(cls):
        """
        Método de clase para obtener el número de bodegas registradas.
        """
        return cls.objects.count()

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
            nombre_proveedor = objeto.nombre + " " + objeto.proveedor
            arreglo[indice].append("%s. C.I: %s" % (nombre_proveedor, self.formateardui(objeto.dui)))
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
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, null=True)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, null=True)

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
    def total_precio(cls):
        """
        Calcula la suma total del precio unitario de todos los productos.
        """
        total = cls.objects.all().aggregate(total=Sum('precio_unitario'))['total'] or 0
        return total
        

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
    #return nombre
    
    def __str__(self):
        return f"{self.nombre}"


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
from django.db.models import Sum

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
            if self.stock - cantidad < 0:
                raise ValidationError("No se puede reducir el stock por debajo de cero.")
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

    def obtener_bodega(self):
        """
        Obtiene la bodega donde se encuentra el inventario.
        """
        return self.idbodega
        
    @classmethod
    def stock_total(cls, producto):
        """
        Calcula el stock total de un producto sumando entradas y restando salidas.
        """
        total_entradas = MovimientoProducto.objects.filter(
            producto=producto, tipo_movimiento='entrada'
        ).aggregate(total=Sum('cantidad'))['total'] or 0
        total_salidas = MovimientoProducto.objects.filter(
            producto=producto, tipo_movimiento='salida'
        ).aggregate(total=Sum('cantidad'))['total'] or 0
        return total_entradas - total_salidas

    def ajustar_stock(self, cantidad):
        """
        Ajusta el stock del producto en la bodega.
        """
        if self.stock + cantidad < 0:
            raise ValidationError("No se puede reducir el stock por debajo de cero.")
        self.stock += cantidad
        self.save()

    @classmethod
    def total_stock(cls):
        """
        Calcula el total de stock de todos los productos en todas las bodegas.
        """
        return cls.objects.aggregate(total_stock=Sum('stock'))['total_stock'] or 0
    #total de dinero en stock
    @classmethod
    def total_dinero_stock(cls):
        """
        Calcula el total de dinero en stock.
        """
        total = 0
        for inventario in cls.objects.all():
            total += inventario.stock * inventario.idproducto.precio_unitario
        return total
    
#------------------------------------NOTIFICACIONES------------------------------------
class Notificaciones(models.Model):
    #id
    autor = models.ForeignKey(Usuario,to_field='username', on_delete=models.CASCADE)
    mensaje = models.TextField()
#---------------------------------------------------------------------------------------class MovimientoProducto(models.Model):class MovimientoProducto(models.Model):
class MovimientoProducto(models.Model):    
    TIPO_MOVIMIENTO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('reparacion', 'Reparacion'),
        ('devolucion', 'Devolucion'),
        ('entrega', 'Entrega'),
        ('recepcion', 'Recepción'),
        ('venta', 'Venta'),
        ('pendiente', 'Pendiente'),
    ]

    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO_CHOICES)
    cantidad = models.IntegerField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, null=True)
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    estado_producto = models.ForeignKey(EstadoProducto, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('bodega', 'producto', 'fecha_movimiento')

    @classmethod
    def movimientos_por_fecha(cls, fecha_inicial, fecha_final):
        return cls.objects.filter(fecha_movimiento__range=[fecha_inicial, fecha_final])

    @classmethod
    def productosPendientes(cls):
        return cls.objects.filter(estado_producto__nombre='Pendiente')

    @classmethod
    def productos_pendientes_por_empleado(cls, empleado):
        return cls.objects.filter(empleado=empleado, estado_producto__nombre='Pendiente')
  
    
    # REPORTES

    @classmethod
    def productos_mas_vendidos(cls):
        """
        Retorna una lista de productos más vendidos, con la cantidad de ventas para cada uno.
        """
        productos = MovimientoProducto.objects.filter(estado_producto__nombre=EstadoProducto.VENDIDO) \
            .select_related('producto') \
            .values('producto') \
            .annotate(total_vendidos=Count('producto')) \
            .order_by('-total_vendidos')

        productos_vendidos = [
            {'nombre': Producto.objects.get(id=producto['producto']).descripcion, 'cantidadVendida': producto['total_vendidos']}
            for producto in productos
        ]
        return productos_vendidos

    @classmethod
    def total_productos_vendidos(cls):
        """
        Retorna el número total de productos vendidos.
        """
        total = MovimientoProducto.objects.filter(estado_producto__nombre=EstadoProducto.VENDIDO) \
            .aggregate(total=Sum('cantidad'))['total']
        return total if total is not None else 0
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
        if self.cantidad + cantidad < 0:
            raise ValidationError("No se puede reducir el stock por debajo de cero.")
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

    def clean(self):
        if self.cantidad < 0:
            raise ValidationError("El stock no puede ser negativo.")

#--------------------------------REPARACION--------------------------------------------
class Reparacion(models.Model):
    """
    Modelo para representar las reparaciones de productos.
    """
    idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    bodega_origen = models.ForeignKey(Bodega, on_delete=models.CASCADE)
    idempleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    motivo = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_retorno = models.DateTimeField(null=True, blank=True)
    estado = models.ForeignKey(EstadoProducto, on_delete=models.CASCADE)
    desde_devolucion = models.BooleanField(default=False)  # Nuevo campo para identificar devoluciones
    @classmethod
    def totalReparacionesPendientes(cls):
        return cls.objects.filter(estado__nombre="pendiente").count()

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Si la reparación no viene de una devolución, verificar y reducir el stock
            if not self.desde_devolucion:
                # Verificar stock disponible en la bodega
                inventario = Inventario.objects.filter(
                    idbodega=self.bodega_origen,
                    idproducto=self.idproducto
                ).first()

                if not inventario:
                    raise ValidationError("El producto no existe en esta bodega.")
                
                if inventario.stock < 1:
                    raise ValidationError(f"Stock insuficiente: disponible {inventario.stock}, solicitado {1}.")
                
                # Reducir el stock en el inventario
                inventario.reducir_stock(1)

            # Guardar la reparación
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Reparación {self.idproducto} - {self.estado}"
    

#--------------------------------DEVOLUCION--------------------------------------------
class Devolucion(models.Model):
    """
    Modelo para representar las devoluciones de productos.
    """
    idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    idempleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    idempleado_recibio = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    idbodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    motivo = models.TextField()
    dañado = models.BooleanField(default=False)
    fecha_devolucion = models.DateTimeField(auto_now_add=True)
    enviado_a_reparacion = models.BooleanField(default=False)
   
   #si dañado es igual a false se le sumara la cantidad al inventario
    def save(self, *args, **kwargs):
        with transaction.atomic():
            inventario = Inventario.objects.filter(idbodega=self.idbodega, idproducto=self.idproducto).first()
            if self.dañado:
                # # Reducir el stock en el inventario
                # inventario.reducir_stock(self.cantidad)
                #mensaje de notificacion
                mensaje = f"Se ha devuelto {self.cantidad} unidades del producto {self.idproducto.descripcion} por daño."
            else:
                # Aumentar el stock en el inventario
                inventario.aumentar_stock(self.cantidad)
                #mensaje de notificacion
            # Guardar la devolución

            super().save(*args, **kwargs)

    def __str__(self):
        return f"Devolución {self.idproducto} - {self.cantidad} unidades"
    #total devoluciones
    @classmethod
    def totalDevoluciones(cls):
        return cls.objects.count()

#--------------------------------ENTREGA------------------------------------------------
from django.db import models, transaction

class Entrega(models.Model):
    id_empleado_autorizo = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_empleado_recibio = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    @transaction.atomic
    def procesar_entrega(self):
        estado_pendiente = EstadoProducto.objects.get(nombre= EstadoProducto.PENDIENTE)
        for detalle in self.detalles.select_related('producto', 'bodega'):
            inventario = Inventario.objects.select_for_update().get(
                idbodega=detalle.bodega,
                idproducto=detalle.producto
            )
            if inventario.stock < detalle.cantidad:
                raise ValidationError(f"Stock insuficiente para {detalle.producto.descripcion}")
            
            inventario.reducir_stock(detalle.cantidad)
            
            MovimientoProducto.objects.create(
                producto=detalle.producto,
                bodega=detalle.bodega,
                tipo_movimiento='salida',
                cantidad=detalle.cantidad,
                usuario=self.id_empleado_autorizo,
                empleado=self.id_empleado_recibio,
                estado_producto=estado_pendiente
            )

class DetalleEntrega(models.Model):
    entrega = models.ForeignKey(Entrega, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    class Meta:
        unique_together = ('entrega', 'producto', 'bodega')