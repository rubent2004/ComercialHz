# import datetime
# from django.shortcuts import get_object_or_404, redirect, render
# from django.views.generic import ListView, DetailView
# #renderiza las vistas al usuario
# # para redirigir a otras paginas
# from django.http import HttpResponseRedirect, HttpResponse,FileResponse
# #el formulario de login
# from .forms import *
# from inventario.forms import LoginFormulario
# # clase para crear vistas basadas en sub-clases
# from django.views import View
# #verifica si el usuario esta logeado
# from django.contrib.auth.mixins import LoginRequiredMixin

# #modelos
# from .models import *
# #formularios dinamicos
# from django.forms import formset_factory
# #funciones personalizadas
# from .funciones import *
# #Mensajes de formulario
# from django.contrib import messages
# #Ejecuta un comando en la terminal externa
# from django.core.management import call_command
# #procesa archivos en .json
# from django.core import serializers
# #permite acceder de manera mas facil a los ficheros
# from django.core.files.storage import FileSystemStorage
# # Create your views here.



# #Muestra una lista de 10 productos por pagina----------------------------------------#
# class ListarProductos(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def get(self, request):
#         #Lista de productos de la BDD
#         productos = Producto.objects.all()
                               
#         contexto = {'tabla':productos}

#         contexto = complementarContexto(contexto,request.user)  

#         return render(request, 'inventario/producto/listarProductos.html',contexto)
# #Fin de vista-------------------------------------------------------------------------#




# #Maneja y visualiza un formulario--------------------------------------------------#
# class AgregarProducto(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self, request):
#         # Crea una instancia del formulario y la llena con los datos:
#         form = ProductoForm(request.POST)
#         # Revisa si es valido:
#         if form.is_valid():
#             # Procesa y asigna los datos con form.cleaned_data como se requiere
#             descripcion = form.cleaned_data['descripcion']
#             precio_unitario = form.cleaned_data['precio_unitario']
#             precio_cash = form.cleaned_data['precio_cash']
#             codigo = form.cleaned_data['codigo']
#             categoria = form.cleaned_data['categoria']
#             imagen = form.cleaned_data['imagen']
#             Proveedor = form.cleaned_data['Proveedor']
#             marca = form.cleaned_data['marca']
#             estado = form.cleaned_data['estado']
#             fecha_registro = datetime.now()
#             disponible = 0

#             prod = Producto(descripcion=descripcion, precio_unitario=precio_unitario, precio_cash=precio_cash, codigo=codigo, categoria=categoria, imagen=imagen, Proveedor=Proveedor, marca=marca, estado=estado, fecha_registro=fecha_registro, disponible=disponible)
#             prod.save()
            
#             form = ProductoForm()
#             messages.success(request, 'Ingresado exitosamente bajo la ID %s.' % prod.id)
#             request.session['productoProcesado'] = 'agregado'
#             return HttpResponseRedirect("/inventario/producto/agregarProducto")
#         else:
#             #De lo contrario lanzara el mismo formulario
#             return render(request, 'inventario/producto/agregarProducto.html', {'form': form})

#     # Si se llega por GET crearemos un formulario en blanco
#     def get(self,request):
#         form = ProductoForm()
#         #Envia al usuario el formulario para que lo llene
#         contexto = {'form':form , 'modo':request.session.get('productoProcesado')}   
#         contexto = complementarContexto(contexto,request.user)  
#         return render(request, 'inventario/producto/agregarProducto.html', contexto)
# #Fin de vista------------------------------------------------------------------------# 




# #Formulario simple que procesa un script para importar los productos-----------------#
# class ImportarProductos(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self,request):
#         form = ImportarProductosForm(request.POST)
#         if form.is_valid():
#             request.session['productosImportados'] = True
#             return HttpResponseRedirect("/inventario/importarProductos")

#     def get(self,request):
#         form = ImportarProductosForm()

#         if request.session.get('productosImportados') == True:
#             importado = request.session.get('productoImportados')
#             contexto = { 'form':form,'productosImportados': importado  }
#             request.session['productosImportados'] = False

#         else:
#             contexto = {'form':form}
#             contexto = complementarContexto(contexto,request.user) 
#         return render(request, 'inventario/producto/importarProductos.html',contexto)        

# #Fin de vista-------------------------------------------------------------------------#




# #Formulario simple que crea un archivo y respalda los productos-----------------------#
# class ExportarProductos(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self,request):
#         form = ExportarProductosForm(request.POST)
#         if form.is_valid():
#             request.session['productosExportados'] = True

#             #Se obtienen las entradas de producto en formato JSON
#             data = serializers.serialize("json", Producto.objects.all())
#             fs = FileSystemStorage('inventario/tmp/')

#             #Se utiliza la variable fs para acceder a la carpeta con mas facilidad
#             with fs.open("productos.json", "w") as out:
#                 out.write(data)
#                 out.close()  

#             with fs.open("productos.json", "r") as out:                 
#                 response = HttpResponse(out.read(), content_type="application/force-download")
#                 response['Content-Disposition'] = 'attachment; filename="productos.json"'
#                 out.close() 
#             #------------------------------------------------------------
#             return response

#     def get(self,request):
#         form = ExportarProductosForm()

#         if request.session.get('productosExportados') == True:
#             exportado = request.session.get('productoExportados')
#             contexto = { 'form':form,'productosExportados': exportado  }
#             request.session['productosExportados'] = False

#         else:
#             contexto = {'form':form}
#             contexto = complementarContexto(contexto,request.user) 
#         return render(request, 'inventario/producto/exportarProductos.html',contexto)
# #Fin de vista-------------------------------------------------------------------------#




# #Muestra el formulario de un producto especifico para editarlo----------------------------------#
# class EditarProducto(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self,request,p):
#         # Crea una instancia del formulario y la llena con los datos:
#         form = ProductoForm(request.POST)
#         # Revisa si es valido:
#         if form.is_valid():
#             # Procesa y asigna los datos con form.cleaned_data como se requiere
#             descripcion = form.cleaned_data['descripcion']
#             precio_unitario = form.cleaned_data['precio_unitario']
#             categoria = form.cleaned_data['categoria']
#             precio_cash = form.cleaned_data['precio_cash']
#             codigo = form.cleaned_data['codigo']
#             imagen = form.cleaned_data['imagen']
#             Proveedor = form.cleaned_data['Proveedor']
#             marca = form.cleaned_data['marca']
#             estado = form.cleaned_data['estado']
#             fecha_registro = form.cleaned_data['fecha_registro']
        

#             prod = Producto.objects.get(id=p)
#             prod.descripcion = descripcion
#             prod.precio_unitario = precio_unitario
#             prod.categoria = categoria
#             prod.precio_cash = precio_cash
#             prod.codigo = codigo
#             prod.imagen = imagen
#             prod.proveedor = Proveedor
#             prod.marca = marca
#             prod.estado = estado
#             #obtener fecha de forma automatica
#             #prod.fecha_registro = datetime.now()
#             prod.fecha_registro = fecha_registro
#             prod.save()
#             form = ProductoForm(instance=prod)
#             messages.success(request, 'Actualizado exitosamente el producto de ID %s.' % p)
#             request.session['productoProcesado'] = 'editado'            
#             return HttpResponseRedirect("/inventario/editarProducto/%s" % prod.id)
#         else:
#             #De lo contrario lanzara el mismo formulario
#             return render(request, 'inventario/producto/agregarProducto.html', {'form': form})

#     def get(self, request,p): 
#         prod = Producto.objects.get(id=p)
#         form = ProductoForm(instance=prod)
#         #Envia al usuario el formulario para que lo llene
#         contexto = {'form':form , 'modo':request.session.get('productoProcesado'),'editar':True}    
#         contexto = complementarContexto(contexto,request.user) 
#         return render(request, 'inventario/producto/agregarProducto.html', contexto)
# #Fin de vista------------------------------------------------------------------------------------#      

# #ahora pedido
# #Muestra una lista de 10 productos por pagina----------------------------------------#
# class ListarPedidos(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def get(self, request):
#         from django.db import models
#         #Lista de productos de la BDD
#         pedidos = Pedido.objects.all()
                               
#         contexto = {'tabla':pedidos}

#         contexto = complementarContexto(contexto,request.user)  

#         return render(request, 'inventario/pedido/listarPedidos.html',contexto)
# #Fin de vista-------------------------------------------------------------------------#
# #ingresar pedido 
# class AgregarPedido(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self, request):
#         form = PedidoForm(request.POST)
#         if form.is_valid():
#             pedido = form.save()
#             messages.success(request, f'Pedido {pedido.id} agregado exitosamente.')
#             return redirect('lista_pedidos')
#         else:
#             return render(request, 'inventario/pedido/agregarPedido.html', {'form': form})

#     def get(self, request):
#         form = PedidoForm()
#         return render(request, 'inventario/pedido/agregarPedido.html', {'form': form})
    
# class ListaPedidos(LoginRequiredMixin, ListView):
#     model = Pedido
#     template_name = 'inventario/pedido/listaPedidos.html'
#     context_object_name = 'pedidos'
#     login_url = '/inventario/login'
#     redirect_field_name = None
# class DetallePedido(LoginRequiredMixin, DetailView):
#     model = Pedido
#     template_name = 'inventario/pedido/detallePedido.html'
#     context_object_name = 'pedido'
#     login_url = '/inventario/login'
#     redirect_field_name = None

# class ProcesarPedido(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self, request, pk):
#         pedido = get_object_or_404(Pedido, pk=pk)
#         pedido.procesar_pedido()
#         messages.success(request, f'Pedido {pedido.id} procesado exitosamente.')
#         return redirect('detalle_pedido', pk=pedido.id)
    
# class AgregarPedidoItem(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self, request, pedido_id):
#         pedido = get_object_or_404(Pedido, id=pedido_id)
#         form = PedidoItemForm(request.POST)
#         if form.is_valid():
#             pedido_item = form.save(commit=False)
#             pedido_item.pedido = pedido
#             pedido_item.save()
#             messages.success(request, f'Producto agregado al pedido {pedido.id} exitosamente.')
#             return redirect('detalle_pedido', pk=pedido.id)
#         else:
#             return render(request, 'inventario/pedido/agregarPedidoItem.html', {'form': form, 'pedido': pedido})

#     def get(self, request, pedido_id):
#         pedido = get_object_or_404(Pedido, id=pedido_id)
#         form = PedidoItemForm()
#         return render(request, 'inventario/pedido/agregarPedidoItem.html', {'form': form, 'pedido': pedido})
    
# class EditarPedidoItem(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self, request, item_id):
#         pedido_item = get_object_or_404(PedidoItem, id=item_id)
#         form = PedidoItemForm(request.POST, instance=pedido_item)
#         if form.is_valid():
#             form.save()
#             messages.success(request, f'Producto en el pedido {pedido_item.pedido.id} actualizado exitosamente.')
#             return redirect('detalle_pedido', pk=pedido_item.pedido.id)
#         else:
#             return render(request, 'inventario/pedido/editarPedidoItem.html', {'form': form, 'pedido_item': pedido_item})

#     def get(self, request, item_id):
#         pedido_item = get_object_or_404(PedidoItem, id=item_id)
#         form = PedidoItemForm(instance=pedido_item)
#         return render(request, 'inventario/pedido/editarPedidoItem.html', {'form': form, 'pedido_item': pedido_item})

# class EliminarPedidoItem(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self, request, item_id):
#         pedido_item = get_object_or_404(PedidoItem, id=item_id)
#         pedido_id = pedido_item.pedido.id
#         pedido_item.delete()
#         messages.success(request, f'Producto eliminado del pedido {pedido_id} exitosamente.')
#         return redirect('detalle_pedido', pk=pedido_id)
    
# class ListaPedidoItems(LoginRequiredMixin, ListView):
#     model = PedidoItem
#     template_name = 'inventario/pedido/listaPedidoItems.html'
#     context_object_name = 'pedido_items'
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def get_queryset(self):
#         return PedidoItem.objects.filter(pedido_id=self.kwargs['pedido_id'])
    
# class GenerarPedidoPDF(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def get(self, request, p):

#         pedido = Pedido.objects.get(id=p)
#         general = Opciones.objects.get(id=1)
#         detalles = DetallePedido.objects.filter(id_pedido_id=p)


#         data = {
#             'pedido': pedido,
#             'general': general,
#             'detalles': detalles
#         }

#         nombre_pedido = "pedido_%s.pdf" % (pedido.id)

#         pdf = render_to_pdf('inventario/PDF/prueba.html', data)
#         response = HttpResponse(pdf,content_type='application/pdf')
#         response['Content-Disposition'] = 'attachment; filename="%s"' % nombre_pedido

#         return response 
#         #Fin de vista--------------------------------------------------------------------------------------#


# class ListarProveedores(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def get(self, request):
#         from django.db import models
#         #Saca una lista de todos los clientes de la BDD
#         proveedores = Proveedor.objects.all()                
#         contexto = {'tabla': proveedores}
#         contexto = complementarContexto(contexto,request.user)         

#         return render(request, 'inventario/proveedor/listarProveedores.html',contexto) 
# #Fin de vista--------------------------------------------------------------------------#




# #Crea y procesa un formulario para agregar a un proveedor---------------------------------#
# class AgregarProveedor(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self, request):
#         # Crea una instancia del formulario y la llena con los datos:
#         form = ProveedorForm(request.POST)
#         # Revisa si es valido:

#         if form.is_valid():
#             # Procesa y asigna los datos con form.cleaned_data como se requiere

#             nombre = form.cleaned_data['nombre']
#             apellido = form.cleaned_data['apellido']
#             direccion = form.cleaned_data['direccion']
#             telefono = form.cleaned_data['telefono']
#             correo = form.cleaned_data['correo']

#             proveedor = Proveedor(nombre=nombre, apellido=apellido, direccion=direccion, telefono=telefono, correo=correo)
#             proveedor.save()
#             form = ProveedorForm()

#             messages.success(request, 'Ingresado exitosamente bajo la ID %s.' % proveedor.id)
#             request.session['proveedorProcesado'] = 'agregado'
#             return HttpResponseRedirect("/inventario/agregarProveedor")
#         else:
#             #De lo contrario lanzara el mismo formulario
#             return render(request, 'inventario/proveedor/agregarProveedor.html', {'form': form})        

#     def get(self,request):
#         form = ProveedorForm()
#         #Envia al usuario el formulario para que lo llene
#         contexto = {'form':form , 'modo':request.session.get('proveedorProcesado')} 
#         contexto = complementarContexto(contexto,request.user)         
#         return render(request, 'inventario/proveedor/agregarProveedor.html', contexto)
# #Fin de vista-----------------------------------------------------------------------------#

# #Muestra el mismo formulario del cliente pero con los datos a editar----------------------#
# class EditarProveedor(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self,request,p):
#         # Crea una instancia del formulario y la llena con los datos:
#         proveedor = Proveedor.objects.get(id=p)
#         form = ProveedorForm(request.POST, instance=proveedor)
#         # Revisa si es valido:
      
#         if form.is_valid():           
#             # Procesa y asigna los datos con form.cleaned_data como se requiere
#             nombre = form.cleaned_data['nombre']
#             apellido = form.cleaned_data['apellido']
#             direccion = form.cleaned_data['direccion']
#             telefono = form.cleaned_data['telefono']
#             correo = form.cleaned_data['correo']


#             proveedor.nombre = nombre
#             proveedor.apellido = apellido
#             proveedor.direccion = direccion
#             proveedor.telefono = telefono
#             proveedor.correo = correo
#             proveedor.save()
#             form = ProveedorForm(instance=proveedor)

#             messages.success(request, 'Actualizado exitosamente el proveedor de ID %s.' % p)
#             request.session['proveedorProcesado'] = 'editado'            
#             return HttpResponseRedirect("/inventario/editarProveedor/%s" % proveedor.id)
#         else:
#             #De lo contrario lanzara el mismo formulario
#             return render(request, 'inventario/proveedor/agregarProveedor.html', {'form': form})

#     def get(self, request,p): 
#         proveedor = Proveedor.objects.get(id=p)
#         form = ProveedorForm(instance=proveedor)
#         #Envia al usuario el formulario para que lo llene
#         contexto = {'form':form , 'modo':request.session.get('proveedorProcesado'),'editar':True} 
#         contexto = complementarContexto(contexto,request.user)     
#         return render(request, 'inventario/proveedor/agregarProveedor.html', contexto)  
# #Fin de vista--------------------------------------------------------------------------------#

# #BODEGA
# class AgregarBodega(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self, request):
#         form = BodegaForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Bodega agregada exitosamente.')
#             return redirect('lista_bodegas')
#         else:
#             return render(request, 'inventario/bodega/agregarBodega.html', {'form': form})

#     def get(self, request):
#         form = BodegaForm()
#         return render(request, 'inventario/bodega/agregarBodega.html', {'form': form})
    
# class EditarBodega(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self, request, pk):
#         bodega = get_object_or_404(Bodega, pk=pk)
#         form = BodegaForm(request.POST, instance=bodega)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Bodega actualizada exitosamente.')
#             return redirect('lista_bodegas')
#         else:
#             return render(request, 'inventario/bodega/editarBodega.html', {'form': form})

#     def get(self, request, pk):
#         bodega = get_object_or_404(Bodega, pk=pk)
#         form = BodegaForm(instance=bodega)
#         return render(request, 'inventario/bodega/editarBodega.html', {'form': form})
    
# class ListaBodegas(LoginRequiredMixin, ListView):
#     model = Bodega
#     template_name = 'inventario/bodega/listaBodegas.html'
#     context_object_name = 'bodegas'
#     login_url = '/inventario/login'
#     redirect_field_name = None

# #INVENTARIO
# class ListaInventario(LoginRequiredMixin, ListView):
#     model = Inventario
#     template_name = 'inventario/inventario/listaInventario.html'
#     context_object_name = 'inventarios'
#     login_url = '/inventario/login'
#     redirect_field_name = None

# class AgregarMovimientoProducto(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self, request):
#         form = MovimientoProductoForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Movimiento de producto agregado exitosamente.')
#             return redirect('lista_movimientos_producto')
#         else:
#             return render(request, 'inventario/movimientoProducto/agregarMovimientoProducto.html', {'form': form})

#     def get(self, request):
#         form = MovimientoProductoForm()
#         return render(request, 'inventario/movimientoProducto/agregarMovimientoProducto.html', {'form': form})
    
# class ListaMovimientosProducto(LoginRequiredMixin, ListView):
#     model = MovimientoProducto
#     template_name = 'inventario/movimientoProducto/listaMovimientosProducto.html'
#     context_object_name = 'movimientos_producto'
#     login_url = '/inventario/login'
#     redirect_field_name = None

# class AgregarReparacion(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self, request):
#         form = ReparacionForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Reparación agregada exitosamente.')
#             return redirect('lista_reparaciones')
#         else:
#             return render(request, 'inventario/reparacion/agregarReparacion.html', {'form': form})

#     def get(self, request):
#         form = ReparacionForm()
#         return render(request, 'inventario/reparacion/agregarReparacion.html', {'form': form})
    
# class ListaReparaciones(LoginRequiredMixin, ListView):
#     model = Reparacion
#     template_name = 'inventario/reparacion/listaReparaciones.html'
#     context_object_name = 'reparaciones'
#     login_url = '/inventario/login'
#     redirect_field_name = None

# #AGREGAR DEVOLUCION
# class AgregarDevolucion(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self, request):
#         form = DevolucionForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Devolución agregada exitosamente.')
#             return redirect('lista_devoluciones')
#         else:
#             return render(request, 'inventario/devolucion/agregarDevolucion.html', {'form': form})

#     def get(self, request):
#         form = DevolucionForm()
#         return render(request, 'inventario/devolucion/agregarDevolucion.html', {'form': form})

# class ListaDevoluciones(LoginRequiredMixin, ListView):
#     model = Devolucion
#     template_name = 'inventario/devolucion/listaDevoluciones.html'
#     context_object_name = 'devoluciones'
#     login_url = '/inventario/login'
#     redirect_field_name = None

# class AgregarEntrega(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self, request):
#         form = EntregaForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Entrega agregada exitosamente.')
#             return redirect('lista_entregas')
#         else:
#             return render(request, 'inventario/entrega/agregarEntrega.html', {'form': form})

#     def get(self, request):
#         form = EntregaForm()
#         return render(request, 'inventario/entrega/agregarEntrega.html', {'form': form})
    
# class ListaEntregas(LoginRequiredMixin, ListView):
#     model = Entrega
#     template_name = 'inventario/entrega/listaEntregas.html'
#     context_object_name = 'entregas'
#     login_url = '/inventario/login'
#     redirect_field_name = None

# class AgregarRecepcion(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self, request):
#         form = RecepcionForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Recepción agregada exitosamente.')
#             return redirect('lista_recepciones')
#         else:
#             return render(request, 'inventario/recepcion/agregarRecepcion.html', {'form': form})

#     def get(self, request):
#         form = RecepcionForm()
#         return render(request, 'inventario/recepcion/agregarRecepcion.html', {'form': form})


# class ListaRecepciones(LoginRequiredMixin, ListView):
#     model = Recepcion
#     template_name = 'inventario/recepcion/listaRecepciones.html'
#     context_object_name = 'recepciones'
#     login_url = '/inventario/login'
#     redirect_field_name = None