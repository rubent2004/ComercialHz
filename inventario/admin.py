from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import LoginFormulario
from .models import  Empleado, EstadoProducto, Usuario, Producto

class UsuarioAdmin(UserAdmin):
    add_form = LoginFormulario
    #form = CustomUserChangeForm
    model = Usuario
    list_display = ['email', 'username',]

admin.site.register(Usuario, UsuarioAdmin)

 #ver productos
class ProductoAdmin(admin.ModelAdmin):
     list_display = ['descripcion', 'marca', 'precio_unitario', 'precio_cash', 'disponible', 'proveedor']
admin.site.register(Producto, ProductoAdmin)

class EstadoProductoAdmin(admin.ModelAdmin):
     list_display = ['nombre']
admin.site.register(EstadoProducto, EstadoProductoAdmin)

#Empleado
class EmpleadoAdmin(admin.ModelAdmin):
     list_display = ['nombre', 'apellido', 'telefono', 'correo']
admin.site.register(Empleado, EmpleadoAdmin)
