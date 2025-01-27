from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import LoginFormulario
from .models import  Empleado, EstadoProducto, Marca, MovimientoProducto, Proveedor, Reparacion, Usuario, Producto

class UsuarioAdmin(UserAdmin):
    add_form = LoginFormulario
    #form = CustomUserChangeForm
    model = Usuario
    list_display = ['email', 'username',]

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