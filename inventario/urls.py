from django.urls import path
from . import views

app_name = "inventario"

urlpatterns = [
path('login', views.Login.as_view(), name='login'),
path('panel', views.Panel.as_view(), name='panel'),
path('salir', views.Salir.as_view(), name='salir'),
path('perfil/<str:modo>/<int:pk>', views.Perfil.as_view(), name='perfil'),
path('eliminar/<str:modo>/<int:pk>', views.Eliminar.as_view(), name='eliminar'),

path('listarProductos', views.ListarProductos.as_view(), name='listarProductos'),
path('agregarProducto', views.AgregarProducto.as_view(), name='agregarProducto'),
path('importarProductos', views.ImportarProductos.as_view(), name='importarProductos'),
path('exportarProductos', views.ExportarProductos.as_view(), name='exportarProductos'),
path('editarProducto/<int:pk>', views.EditarProducto.as_view(), name='editarProducto'),

path('listarProveedores', views.ListarProveedores.as_view(), name='listarProveedores'),
path('agregarProveedor', views.AgregarProveedor.as_view(), name='agregarProveedor'),
path('importarProveedores', views.ImportarProveedores.as_view(), name='importarProveedores'),
path('exportarProveedores', views.ExportarProveedores.as_view(), name='exportarProveedores'),
path('editarProveedor/<int:pk>', views.EditarProveedor.as_view(), name='editarProveedor'),

path('agregarCompra', views.AgregarCompra.as_view(), name='agregarCompra'),
path('listarCompras', views.ListarCompras.as_view(), name='listarCompras'),
# path('detallesCompra', views.DetallesCompra.as_view(), name='detallesCompra'),
# path('verCompra/<int:p>',views.VerCompra.as_view(), name='verCompra'),
# path('validarCompra/<int:p>',views.ValidarCompra.as_view(), name='validarCompra'),
path('generarCompra/<int:p>',views.GenerarCompra.as_view(), name='generarCompra'),
path('generarCompraPDF/<int:pk>',views.GenerarCompraPDF.as_view(), name='generarCompraPDF'),

path('listarEmpleados', views.ListarEmpleados.as_view(), name='listarEmpleados'),
path('agregarEmpleado', views.AgregarEmpleado.as_view(), name='agregarEmpleado'),
path('importarEmpleados', views.ImportarEmpleados.as_view(), name='importarEmpleados'),
path('exportarEmpleados', views.ExportarEmpleados.as_view(), name='exportarEmpleados'),
path('editarEmpleado/<int:pk>', views.EditarEmpleado.as_view(), name='editarEmpleado'),

# path('emitirFactura', views.EmitirFactura.as_view(), name='emitirFactura'),
# path('detallesDeFactura', views.DetallesFactura.as_view(), name='detallesDeFactura'),
# path('listarFacturas',views.ListarFacturas.as_view(), name='listarFacturas'),
# path('verFactura/<int:p>',views.VerFactura.as_view(), name='verFactura'),
# path('generarFactura/<int:p>',views.GenerarFactura.as_view(), name='generarFactura'),
# path('generarFacturaPDF/<int:p>',views.GenerarFacturaPDF.as_view(), name='generarFacturaPDF'),

path('crearUsuario',views.CrearUsuario.as_view(), name='crearUsuario'),
path('listarUsuarios', views.ListarUsuarios.as_view(), name='listarUsuarios'),

path('importarBDD',views.ImportarBDD.as_view(), name='importarBDD'),
path('descargarBDD', views.DescargarBDD.as_view(), name='descargarBDD'),
path('configuracionGeneral', views.ConfiguracionGeneral.as_view(), name='configuracionGeneral'),

path('verManualDeUsuario/<str:pagina>/',views.VerManualDeUsuario.as_view(), name='verManualDeUsuario'),

#Comercial
path('listarEstadoProducto', views.ListarEstadoProducto.as_view(), name='listarEstadoProducto'),
path('agregarEstadoProducto', views.AgregarEstadoProducto.as_view(), name='agregarEstadoProducto'),
path('editarEstadoProducto/<int:pk>', views.EditarEstadoProducto.as_view(), name='editarEstadoProducto'),
    # path('eliminarEstadoProducto/<int:pk>', views.EliminarEstadoProducto.as_view(), name='eliminarEstadoProducto'),
path('listarMarca', views.ListarMarca.as_view(), name='listarMarca'),
path('agregarMarca', views.AgregarMarca.as_view(), name='agregarMarca'),
path('editarMarca/<int:pk>', views.EditarMarca.as_view(), name='editarMarca'),
]
