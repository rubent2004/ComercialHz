from django.urls import path
from . import views
from django.urls import path
from .views import ReporteInventarioPDF
from django.urls import path
from .views import ReporteInventarioView, ReporteInventarioPDF
from django.contrib import admin
from .views import ReporteProductoView, ReporteMovimientoView
from .views import ReporteProductoView
#from .views import ReporteProductosPDF
from django.urls import path, include

#from .views import AgregarProducto, ListarProductos, ImportarProductos, ExportarProductos, EditarProducto


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
path('buscar-producto/', views.buscar_producto, name='buscar_producto'),
path('buscar-productoNom/', views.buscar_productoNom, name='buscar_productoNom'),
path('buscar-empleado/', views.buscar_empleado, name='buscar_empleado'),
path('buscar-producto-por-id/', views.BuscarProductoPorId.as_view(), name='buscar_producto_por_id'),
path('buscar-sugerencias-nombre/', views.buscar_sugerencias_nombre, name='buscar_sugerencias_nombre'),
 path('buscar-sugerencias-empleado/', views.buscar_sugerencias_empleado, name='buscar_sugerencias_empleado'),

#con bodega filtro
path('buscar-producto2/', views.buscar_producto2, name='buscar_producto2'),
path('buscar-productoNom2/', views.buscar_productoNom2, name='buscar_productoNom2'),
path('buscar-sugerencias-nombre2/', views.buscar_sugerencias_nombre2, name='buscar_sugerencias_nombre2'),

path('listarProveedores', views.ListarProveedores.as_view(), name='listarProveedores'),
path('agregarProveedor', views.AgregarProveedor.as_view(), name='agregarProveedor'),
path('importarProveedores', views.ImportarProveedores.as_view(), name='importarProveedores'),
#path('exportarProveedores', views.ExportarProveedores.as_view(), name='exportarProveedores'),
path('editarProveedor/<int:pk>', views.EditarProveedor.as_view(), name='editarProveedor'),

# path('agregarCompra', views.AgregarCompra.as_view(), name='agregarCompra'),
# path('listarCompras', views.ListarCompras.as_view(), name='listarCompras'),
# path('detallesCompra', views.DetallesCompra.as_view(), name='detallesCompra'),
# path('verCompra/<int:p>',views.VerCompra.as_view(), name='verCompra'),
# path('validarCompra/<int:p>',views.ValidarCompra.as_view(), name='validarCompra'),
# path('generarCompra/<int:p>',views.GenerarCompra.as_view(), name='generarCompra'),
# path('generarCompraPDF/<int:pk>',views.GenerarCompraPDF.as_view(), name='generarCompraPDF'),

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

    # path('eliminarEstadoProducto/<int:pk>', views.EliminarEstadoProducto.as_view(), name='eliminarEstadoProducto'),
path('listarMarca', views.ListarMarca.as_view(), name='listarMarca'),
path('agregarMarca', views.AgregarMarca.as_view(), name='agregarMarca'),
path('editarMarca/<int:pk>', views.EditarMarca.as_view(), name='editarMarca'),

path('listarBodega', views.ListarBodega.as_view(), name='listarBodega'),
path('agregarBodega', views.AgregarBodega.as_view(), name='agregarBodega'),
path('editarBodega/<int:pk>', views.EditarBodega.as_view(), name='editarBodega'),
path('verificar-stock2/', views.verificar_stock2, name='verificar_stock2'),
path('listarEstado', views.ListarEstado.as_view(), name='listarEstado'),
path('agregarEstado', views.AgregarEstado.as_view(), name='agregarEstado'),
path('editarEstado/<int:pk>', views.EditarEstado.as_view(), name='editarEstado'),
#listar inventario
path('listarInventario', views.ListarInventario.as_view(), name='listarInventario'),
#registrar inventario
path('agregarInventario', views.AgregarInventario.as_view(), name='agregarInventario'),
#movimiento producto
path('listarMovimientoProducto', views.ListarMovimientoProducto.as_view(), name='listarMovimientoProducto'),
#Agregar entrega
path('agregarEntrega', views.agregarEntrega, name='agregarEntrega'),
path('verificar-stock/', views.verificar_stock, name='verificar_stock'),
#movimiento producto
path('listarMovimientoProducto', views.ListarMovimientoProducto.as_view(), name='listarMovimientoProducto'),
#Reparaciones
path('listarRep', views.ListarRep.as_view(), name='listarRep'),
path('agregarRep/', views.AgregarRep.as_view(), name='agregarRep'),
path('marcarRep/<int:pk>', views.MarcarRep.as_view(), name='marcarRep'),


#Reportes

path('reporte-inventario/', ReporteInventarioView.as_view(), name='reporte_inventario'),
path('reporte-inventario/pdf/', ReporteInventarioPDF.as_view(), name='reporte_inventario_pdf'),
path('reporteproductos/', ReporteProductoView.as_view(), name='reporte_productos'),
path('reporte_movimientos/', views.ReporteMovimientoView.as_view(), name='reporte_movimientos'),
path('reporte_ventas/', views.ProductosMasVendidosPDF.as_view(), name='reporte_ventas'),







#devoluciones
path('listarDev', views.ListarDev.as_view(), name='listarDev'),
path('agregarDev', views.AgregarDev.as_view(), name='agregarDev'),

#pruebas
path('reportes/<str:reporte_type>/', views.GeneradorReportesPDF.as_view(), name='generar_reporte'),
path('reportes/', views.GeneradorReportesPDF.as_view(), name='reportes'),
path('cambiarEstadoEmpleado/<int:id>/', views.cambiar_estado_empleado, name='cambiar_estado_empleado'),
#url para transferir_stock
path('transferir_stock/', views.TransferirStockView.as_view(), name='transferir_stock'),

# Listado de empleados con pendientes
path('listarEmpleadosPendientes/', views.ListarEmpleadosPendientes.as_view(), name='listar_empleados_pendientes'),

# Detalle de pendientes de un empleado (la URL incluye el id del empleado)
path('empleados/<int:empleado_id>/pendientes/', views.DetalleEmpleadoPendientes.as_view(), name='detalle_empleado_pendientes'),

# Recepción total de un producto en un movimiento
path('empleados/<int:empleado_id>/movimientos/<int:movimiento_id>/recepcion/', views.recepcion_todo_producto, name='recepcion_todo_producto'),

# Venta total de un producto en un movimiento
path('venta-total-producto/<int:empleado_id>/<int:movimiento_id>/', views.venta_total_producto, name='venta_total_producto'),# Transferir producto
path('productos/transferir/', views.transferir_producto, name='transferir_producto'),

# Procesar recepción parcial (maneja la recepción según la lógica del modal)
path('productos/recepcion/', views.recepcion_producto, name='recepcion_producto'),

path('productos-entregados/', views.ProductosEntregadosView.as_view(), name='productos_entregados'),
]



