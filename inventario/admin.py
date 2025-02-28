from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import LoginFormulario
from .models import  DetalleEntrega, Devolucion, Empleado, Entrega, EstadoProducto, Marca, MovimientoProducto, Proveedor, Reparacion, Usuario, Producto,Inventario,RegistroInventario,MovimientoPendiente

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'nivel')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('nivel', 'is_superuser')

    def save_model(self, request, obj, form, change):
        if obj.nivel == 1:
            obj.is_superuser = True
        else:
            obj.is_superuser = False
        super().save_model(request, obj, form, change)

# Registra el modelo y su configuración en el administrador
admin.site.register(Usuario, UsuarioAdmin)
 #ver productos
class ProductoAdmin(admin.ModelAdmin):
     list_display = ['descripcion', 'marca', 'precio_unitario', 'precio_cash', 'proveedor']
admin.site.register(Producto, ProductoAdmin)

class EstadoProductoAdmin(admin.ModelAdmin):
     list_display = ['nombre']
admin.site.register(EstadoProducto, EstadoProductoAdmin)

#Empleado
class EmpleadoAdmin(admin.ModelAdmin):
     list_display = ['nombre', 'apellido', 'telefono', 'correo']
admin.site.register(Empleado, EmpleadoAdmin)
class MarcaAdmin(admin.ModelAdmin):
     list_display = ['nombre']
admin.site.register(Marca, MarcaAdmin)

#PRoveedor
class ProveedorAdmin(admin.ModelAdmin):
     list_display = ['nombre', 'telefono', 'correo']
admin.site.register(Proveedor, ProveedorAdmin)
#movimiento producto
class MovimientoProductoAdmin(admin.ModelAdmin):
     list_display = ['producto', 'cantidad', 'fecha_movimiento','empleado','estado_producto']
admin.site.register(MovimientoProducto, MovimientoProductoAdmin)

#reparacion 
class ReparacionAdmin(admin.ModelAdmin):
     list_display = ['idproducto', 'fecha_retorno', 'idempleado','estado']
admin.site.register(Reparacion, ReparacionAdmin)

#devoluciones

admin.site.register(Devolucion)

#entrega

# class DetalleEntregaInline(admin.TabularInline):  # O tambiÃ©n puedes usar admin.StackedInline
#     model = DetalleEntrega
#     extra = 1  # NÃºmero de formularios vacÃ­os a mostrar

# class EntregaAdmin(admin.ModelAdmin):
#     inlines = [DetalleEntregaInline]  # Mostrar DetalleEntrega en la pÃ¡gina de Entrega

admin.site.register(Entrega)
admin.site.register(DetalleEntrega)  


admin.site.register(Inventario)


admin.site.register(MovimientoPendiente)
admin.site.register(RegistroInventario)
