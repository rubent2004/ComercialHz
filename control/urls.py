# from django.urls import path
# from . import views

# app_name = "control"
# urlpatterns = [
#     path('listarProductos', views.ListarProductos.as_view(), name='listarProductos'),
#     path('agregarProducto', views.AgregarProducto.as_view(), name='agregarProducto'),
#     path('importarProductos', views.ImportarProductos.as_view(), name='importarProductos'),
#     path('exportarProductos', views.ExportarProductos.as_view(), name='exportarProductos'),
#     path('editarProducto/<int:p>', views.EditarProducto.as_view(), name='editarProducto'),

#     path('listarProveedores', views.ListarProveedores.as_view(), name='listarProveedores'),
#     path('agregarProveedor', views.AgregarProveedor.as_view(), name='agregarProveedor'),
#     path('editarProveedor/<int:p>', views.EditarProveedor.as_view(), name='editarProveedor'),

#     path('agregarPedido', views.AgregarPedido.as_view(), name='agregarPedido'),
#     path('listarPedidos', views.ListarPedidos.as_view(), name='listarPedidos'),
#     # path('detallesPedido', views.DetallesPedido.as_view(), name='detallesPedido'),
#     # path('verPedido/<int:p>',views.VerPedido.as_view(), name='verPedido'),
#     # path('validarPedido/<int:p>',views.ValidarPedido.as_view(), name='validarPedido'),
#     # path('generarPedido/<int:p>',views.GenerarPedido.as_view(), name='generarPedido'),
#     path('generarPedidoPDF/<int:p>',views.GenerarPedidoPDF.as_view(), name='generarPedidoPDF'),

#     path('agregarPedido/', views.AgregarPedido.as_view(), name='agregar_pedido'),
#     path('listaPedidos/', views.ListaPedidos.as_view(), name='lista_pedidos'),
#     path('detallePedido/<int:pk>/', views.DetallePedido.as_view(), name='detalle_pedido'),
#     path('procesarPedido/<int:pk>/', views.ProcesarPedido.as_view(), name='procesar_pedido'),
#     path('agregarPedidoItem/<int:pedido_id>/', views.AgregarPedidoItem.as_view(), name='agregar_pedido_item'),
#     path('editarPedidoItem/<int:item_id>/', views.EditarPedidoItem.as_view(), name='editar_pedido_item'),
#     path('eliminarPedidoItem/<int:item_id>/', views.EliminarPedidoItem.as_view(), name='eliminar_pedido_item'),
#     path('listaPedidoItems/<int:pedido_id>/', views.ListaPedidoItems.as_view(), name='lista_pedido_items'),
#     path('generarPedidoPDF/<int:pk>/', views.GenerarPedidoPDF.as_view(), name='generar_pedido_pdf'),

#     # Bodegas
#     path('listarBodegas/', views.ListaBodegas.as_view(), name='lista_bodegas'),
#     path('agregarBodega/', views.AgregarBodega.as_view(), name='agregar_bodega'),
#     path('editarBodega/<int:pk>/', views.EditarBodega.as_view(), name='editar_bodega'),

#     # Inventario
#     path('listarInventario/', views.ListaInventario.as_view(), name='lista_inventario'),

#     # Movimientos de Producto
#     path('listarMovimientosProducto/', views.ListaMovimientosProducto.as_view(), name='lista_movimientos_producto'),
#     path('agregarMovimientoProducto/', views.AgregarMovimientoProducto.as_view(), name='agregar_movimiento_producto'),

#     # Reparaciones
#     path('listarReparaciones/', views.ListaReparaciones.as_view(), name='lista_reparaciones'),
#     path('agregarReparacion/', views.AgregarReparacion.as_view(), name='agregar_reparacion'),

#     # Devoluciones
#     path('listarDevoluciones/', views.ListaDevoluciones.as_view(), name='lista_devoluciones'),
#     path('agregarDevolucion/', views.AgregarDevolucion.as_view(), name='agregar_devolucion'),

#     # Entregas
#     path('listarEntregas/', views.ListaEntregas.as_view(), name='lista_entregas'),
#     path('agregarEntrega/', views.AgregarEntrega.as_view(), name='agregar_entrega'),

#     # Recepciones
#     path('listarRecepciones/', views.ListaRecepciones.as_view(), name='lista_recepciones'),
#     path('agregarRecepcion/', views.AgregarRecepcion.as_view(), name='agregar_recepcion'),
# ]
