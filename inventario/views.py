#renderiza las vistas al usuario
import calendar
from collections import defaultdict
import datetime
import json
from .services import EntregaService
from django.shortcuts import render
from django.views import View

from time import timezone
from urllib import request
from venv import logger
from django.shortcuts import get_object_or_404, redirect, render
# para redirigir a otras paginas
from django.http import HttpResponseRedirect, HttpResponse,FileResponse, JsonResponse
#el formulario de login
from .forms import *
# clase para crear vistas basadas en sub-clases
from django.views import View
from django.urls import reverse
from django.db.models import Count, Prefetch, F
#autentificacion de usuario e inicio de sesion
from django.contrib.auth import authenticate, login, logout
#verifica si el usuario esta logeado
from django.contrib.auth.mixins import LoginRequiredMixin

#modelos
from .models import *
#formularios dinamicos
from django.forms import formset_factory, modelformset_factory
#funciones personalizadas
from .funciones import *
#Mensajes de formulario
from django.contrib import messages
#Ejecuta un comando en la terminal externa
from django.core.management import call_command
#procesa archivos en .json
from django.core import serializers
#permite acceder de manera mas facil a los ficheros
from django.core.files.storage import FileSystemStorage
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models.functions import TruncDate
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from inventario.decorators import nivel_requerido
#Vistas endogenas.


#Interfaz de inicio de sesion----------------------------------------------------#
class Login(View):
    #Si el usuario ya envio el formulario por metodo post
    def post(self,request):
        # Crea una instancia del formulario y la llena con los datos:
        form = LoginFormulario(request.POST)
        # Revisa si es valido:
        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            usuario = form.cleaned_data['username']
            clave = form.cleaned_data['password']
            # Se verifica que el usuario y su clave existan
            logeado = authenticate(request, username=usuario, password=clave)
            if logeado is not None:
                login(request,logeado)
                #Si el login es correcto lo redirige al panel del sistema:
                return HttpResponseRedirect('/inventario/panel')
            else:
                #De lo contrario lanzara el mismo formulario
                return render(request, 'inventario/login.html', {'form': form})

    # Si se llega por GET crearemos un formulario en blanco
    def get(self,request):
        if request.user.is_authenticated == True:
            return HttpResponseRedirect('/inventario/panel')

        form = LoginFormulario()
        #Envia al usuario el formulario para que lo llene
        return render(request, 'inventario/login.html', {'form': form})
#Fin de vista---------------------------------------------------------------------#        



from datetime import date

# Panel de inicio y vista principal
from django.shortcuts import render
from .models import Producto, RegistroInventario, Empleado, Usuario, Bodega, Inventario, EstadoProducto

class Panel(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        # Recupera los datos del usuario después del login
        contexto = {
            'usuario': request.user.username,
            'id_usuario': request.user.id,
            'nombre': request.user.first_name,
            'apellido': request.user.last_name,
            'correo': request.user.email,
            'fecha': date.today(),
            'productosRegistrados': Producto.numeroRegistrados(),
            'productosVendidos': RegistroInventario.productos_vendidos(),  # Recuento de productos vendidos
            'empleadosRegistrados': Empleado.numeroRegistrados(),
            'usuariosRegistrados': Usuario.numeroRegistrados(),
            'administradores': Usuario.numeroUsuarios('administrador'),
            'usuarios': Usuario.numeroUsuarios('usuario'),
            'numeroBodegas': Bodega.numeroRegistrados(),  # Número de bodegas
            'totalStock': Inventario.total_stock(),  # Total de stock de productos
            'totalprecio': Inventario.total_dinero_stock(),  # Suma del precio unitario de todos los productos
            'totalvendidos': MovimientoProducto.total_productos_vendidos(),  # Total de productos vendidos
            'productosMasVendidos': MovimientoProducto.productos_mas_vendidos(),  # Producto más vendido
        }
        contexto = complementarContexto(contexto,request.user)

        return render(request, 'inventario/panel.html', contexto)

#Fin de vista----------------------------------------------------------------------#




#Maneja la salida del usuario------------------------------------------------------#
class Salir(LoginRequiredMixin, View):
    #Sale de la sesion actual
    login_url = 'inventario/login'
    redirect_field_name = None

    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/inventario/login')
#Fin de vista----------------------------------------------------------------------#
#requiere que el usuario este logeado para acceder a las vistas

#Muestra el perfil del usuario logeado actualmente---------------------------------#
class Perfil(LoginRequiredMixin, View):
    login_url = 'inventario/login'
    redirect_field_name = None

    #se accede al modo adecuado y se valida al usuario actual para ver si puede modificar al otro usuario-
    #-el cual es obtenido por la variable 'p'
    def get(self, request, modo, pk):
        if modo == 'editar':
            perf = Usuario.objects.get(id=pk)
            editandoSuperAdmin = False

            if pk == 1:
                if request.user.nivel != 2:
                    messages.error(request, 'No puede editar el perfil del administrador por no tener los permisos suficientes')
                    return HttpResponseRedirect('/inventario/perfil/ver/%s' % pk)
                editandoSuperAdmin = True
            else:
                if request.user.is_superuser != True: 
                    messages.error(request, 'No puede cambiar el perfil por no tener los permisos suficientes')
                    return HttpResponseRedirect('/inventario/perfil/ver/%s' % pk) 

                else:
                    if perf.is_superuser == True:
                        if request.user.nivel == 2:
                            pass

                        elif perf.id != request.user.id:
                            messages.error(request, 'No puedes cambiar el perfil de un usuario de tu mismo nivel')

                            return HttpResponseRedirect('/inventario/perfil/ver/%s' % pk) 

            if editandoSuperAdmin:
                form = UsuarioFormulario()
                form.fields['level'].disabled = True
            else:
                form = UsuarioFormulario()

            #Me pregunto si habia una manera mas facil de hacer esto, solo necesitaba hacer que el formulario-
            #-apareciera lleno de una vez, pero arrojaba User already exists y no pasaba de form.is_valid()
            form['username'].field.widget.attrs['value']  = perf.username
            form['first_name'].field.widget.attrs['value']  = perf.first_name
            form['last_name'].field.widget.attrs['value']  = perf.last_name
            form['email'].field.widget.attrs['value']  = perf.email
            form['level'].field.widget.attrs['value']  = perf.nivel

            #Envia al usuario el formulario para que lo llene
            contexto = {'form':form,'modo':request.session.get('perfilProcesado'),'editar':'perfil',
            'nombreUsuario':perf.username}

            contexto = complementarContexto(contexto,request.user)
            return render(request,'inventario/perfil/perfil.html', contexto)


        elif modo == 'clave':  
            perf = Usuario.objects.get(id=pk)
            if pk == 1:
                if request.user.nivel != 2:
                   
                    messages.error(request, 'No puede cambiar la clave del administrador por no tener los permisos suficientes')
                    return HttpResponseRedirect('/inventario/perfil/ver/%s' % pk)  
            else:
                if request.user.is_superuser != True: 
                    messages.error(request, 'No puede cambiar la clave de este perfil por no tener los permisos suficientes')
                    return HttpResponseRedirect('/inventario/perfil/ver/%s' % pk) 

                else:
                    if perf.is_superuser == True:
                        if request.user.nivel == 2:
                            pass

                        elif perf.id != request.user.id:
                            messages.error(request, 'No puedes cambiar la clave de un usuario de tu mismo nivel')
                            return HttpResponseRedirect('/inventario/perfil/ver/%s' % pk) 


            form = ClaveFormulario(request.POST)
            contexto = { 'form':form, 'modo':request.session.get('perfilProcesado'),
            'editar':'clave','nombreUsuario':perf.username }            

            contexto = complementarContexto(contexto,request.user)
            return render(request, 'inventario/perfil/perfil.html', contexto)

        elif modo == 'ver':
            perf = Usuario.objects.get(id=pk)
            contexto = { 'perfil':perf }      
            contexto = complementarContexto(contexto,request.user)
          
            return render(request,'inventario/perfil/verPerfil.html', contexto)



    def post(self,request,modo,pk):
        if modo ==  'editar':
            # Crea una instancia del formulario y la llena con los datos:
            form = UsuarioFormulario(request.POST)
            # Revisa si es valido:
            
            if form.is_valid():
                perf = Usuario.objects.get(id=pk)
                # Procesa y asigna los datos con form.cleaned_data como se requiere
                if pk != 1:
                    level = form.cleaned_data['level']        
                    perf.nivel = level
                    perf.is_superuser = level

                username = form.cleaned_data['username']
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']

                perf.username = username
                perf.first_name = first_name
                perf.last_name = last_name
                perf.email = email

                perf.save()
                
                form = UsuarioFormulario()
                messages.success(request, 'Actualizado exitosamente el perfil de ID %s.' % pk)
                request.session['perfilProcesado'] = True           
                return HttpResponseRedirect("/inventario/perfil/ver/%s" % perf.id)
            else:
                #De lo contrario lanzara el mismo formulario
                return render(request, 'inventario/perfil/perfil.html', {'form': form})

        elif modo == 'clave':
            form = ClaveFormulario(request.POST)

            if form.is_valid():
                error = 0
                clave_nueva = form.cleaned_data['clave_nueva']
                repetir_clave = form.cleaned_data['repetir_clave']
                #clave = form.cleaned_data['clave']

                #Comentare estas lineas de abajo para deshacerme de la necesidad
                #   de obligar a que el usuario coloque la clave nuevamente
                #correcto = authenticate(username=request.user.username , password=clave)


                #if correcto is not None:
                    #if clave_nueva != clave:
                        #pass
                    #else:
                        #error = 1
                        #messages.error(request,"La clave nueva no puede ser identica a la actual") 

                usuario = Usuario.objects.get(id=pk) 

                if clave_nueva == repetir_clave:
                    pass
                else:
                    error = 1
                    messages.error(request,"La clave nueva y su repeticion tienen que coincidir")

                #else:
                    #error = 1
                    #messages.error(request,"La clave de acceso actual que ha insertado es incorrecta")

                if(error == 0):
                    messages.success(request, 'La clave se ha cambiado correctamente!')
                    usuario.set_password(clave_nueva)
                    usuario.save()
                    return HttpResponseRedirect("/inventario/login")

                else:
                    return HttpResponseRedirect("/inventario/perfil/clave/%s" % pk)
    



  
#----------------------------------------------------------------------------------#   


#Elimina usuarios, productos, empleados o proveedores----------------------------
class Eliminar(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, modo, pk):

        if modo == 'producto':
            prod = Producto.objects.get(id=pk)
            prod.delete()
            messages.success(request, 'Producto de ID %s borrado exitosamente.' % pk)
            return HttpResponseRedirect("/inventario/listarProductos")         
           
        elif modo == 'empleado':
            empleado = Empleado.objects.get(id=pk)
            empleado.delete()
            messages.success(request, 'Empleado de ID %s borrado exitosamente.' % pk)
            return HttpResponseRedirect("/inventario/listarEmpleados")            


        elif modo == 'proveedor':
            proveedor = Proveedor.objects.get(id=pk)
            proveedor.delete()
            messages.success(request, 'Proveedor de ID %s borrado exitosamente.' % pk)
            return HttpResponseRedirect("/inventario/listarProveedores")
        
        elif modo == 'marca':
            marca = Marca.objects.get(id=pk)
            marca.delete()
            messages.success(request, 'Marca de ID %s borrado exitosamente.' % pk)
            return HttpResponseRedirect("/inventario/listarMarca")
        
        elif modo == 'bodega':
            bodega = Bodega.objects.get(id=pk)
            bodega.delete()
            messages.success(request, 'Bodega de ID %s borrado exitosamente.' % pk)
            return HttpResponseRedirect("/inventario/listarBodega")
        
        elif modo == 'estadoproducto':
            estadoProducto = EstadoProducto.objects.get(id=pk)
            estadoProducto.delete()
            messages.success(request, 'estadoProducto de ID %s borrado exitosamente.' % pk)
            return HttpResponseRedirect("/inventario/listarEstadoProducto")
        
        elif modo == 'empleado':
            entity = Empleado.objects.get(id=pk)
            entity.delete()
            messages.success(request, 'Empleado de ID %s borrado exitosamente.' % pk)
            return HttpResponseRedirect("/inventario/listarEmpleado")
        
        elif modo == 'estado':
            entity = Estado.objects.get(id=pk)
            entity.delete()
            messages.success(request, 'Estado de ID %s borrado exitosamente.' % pk)
            return HttpResponseRedirect("/inventario/listarEstado")
        


        elif modo == 'usuario':
            if request.user.is_superuser == False:
                messages.error(request, 'No tienes permisos suficientes para borrar usuarios')  
                return HttpResponseRedirect('/inventario/listarUsuarios')

            elif pk== 1:
                messages.error(request, 'No puedes eliminar al super-administrador.')
                return HttpResponseRedirect('/inventario/listarUsuarios')  

            elif request.user.id == pk:
                messages.error(request, 'No puedes eliminar tu propio usuario.')
                return HttpResponseRedirect('/inventario/listarUsuarios')  
         

            else:
                usuario = Usuario.objects.get(id=pk)
                usuario.delete()
                messages.success(request, 'Usuario de ID %s borrado exitosamente.' % pk)
                return HttpResponseRedirect("/inventario/listarUsuarios")   
                 


#Fin de vista-------------------------------------------------------------------   

class AgregarInventario(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None
    
    def post(self, request, producto_id):
        producto = get_object_or_404(Producto, id=producto_id)  # Obtener producto por ID
        
        form = RegistroInventarioFormulario(request.POST)
        if form.is_valid():
            # Guardamos el registro de inventario, pero no confirmamos la base de datos aún
            registro = form.save(commit=False)

            # Obtenemos el inventario o lo creamos si no existe
            inventario, _ = Inventario.objects.get_or_create(
                idbodega=registro.bodega,
                idproducto=producto,  # Usamos el producto recibido
                defaults={'stock': 0, 'estado': EstadoProducto.objects.get(nombre='Disponible')}
            )

            # Aumentamos el stock de inventario
            inventario.aumentar_stock(registro.cantidad)
            inventario.save()

            # Actualizamos el estado del registro de inventario y ajustamos el stock
            registro.estado = EstadoProducto.objects.get(nombre='Disponible')
            registro.ajustar_stock(registro.cantidad)

            # Registramos el movimiento de producto
            MovimientoProducto.objects.create(
                producto=producto,
                bodega=registro.bodega,
                tipo_movimiento='entrada',  # Tipo de movimiento, 'entrada' para agregar productos
                cantidad=registro.cantidad / 2,
                usuario=request.user,
                empleado=None,
                estado_producto=registro.estado
            )

            # Mensaje de éxito
            messages.success(request, 'Registro de inventario agregado exitosamente y stock actualizado.')
            return HttpResponseRedirect("/inventario/agregarInventario")

        else:
            return render(request, 'inventario/inventario/agregarInventario.html', {'form': form, 'producto': producto})

    def get(self, request, producto_id):
        producto = get_object_or_404(Producto, id=producto_id)  # Obtener producto por ID
        form = RegistroInventarioFormulario()
        contexto = {'form': form, 'producto': producto}
        return render(request, 'inventario/inventario/agregarInventario.html', contexto)


#Muestra una lista de 10 productos por pagina----------------------------------------#
class ListarProductos(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None
 
    def get(self, request):
        from django.db import models

        #Lista de productos de la BDD
        productos = Producto.objects.all()
                               
        contexto = {'tabla':productos}

        contexto = complementarContexto(contexto,request.user)  

        return render(request, 'inventario/producto/listarProductos.html',contexto)
#Fin de vista-------------------------------------------------------------------------#



class AgregarProducto(View):
    login_url = '/inventario/login'
    redirect_field_name = None
    @nivel_requerido(nivel_minimo=1)
    def post(self, request):
        form = ProductoFormulario(request.POST)
        if form.is_valid():
            try:
                producto = form.save()
                messages.success(request, f'Producto ingresado exitosamente con ID {producto.id}.')
                request.session['productoProcesado'] = 'agregado'
                return HttpResponseRedirect(reverse('inventario:agregarProducto'))  # Aquí se hace la redirección a 'agregarProducto'
            
            except Exception as e:
                messages.error(request, f'Error al guardar el producto: {str(e)}')

        return render(request, 'inventario/producto/agregarProducto.html', {'form': form})

    def get(self, request):
        form = ProductoFormulario()
        contexto = {
            'form': form,
            'modo': request.session.pop('productoProcesado', None),
        }
        contexto = complementarContexto(contexto,request.user)
        return render(request, 'inventario/producto/agregarProducto.html', contexto)


#Formulario simple que procesa un script para importar los productos-----------------#
class ImportarProductos(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request):
        form = ImportarProductosFormulario(request.POST)
        if form.is_valid():
            request.session['productosImportados'] = True
            return HttpResponseRedirect("/inventario/importarProductos")

    def get(self,request):
        form = ImportarProductosFormulario()

        if request.session.get('productosImportados') == True:
            importado = request.session.get('productoImportados')
            contexto = { 'form':form,'productosImportados': importado  }
            request.session['productosImportados'] = False

        else:
            contexto = {'form':form}
            contexto = complementarContexto(contexto,request.user) 
        return render(request, 'inventario/producto/importarProductos.html',contexto)        

#Fin de vista-------------------------------------------------------------------------#




#Formulario simple que crea un archivo y respalda los productos-----------------------#
class ExportarProductos(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request):
        form = ExportarProductosFormulario(request.POST)
        if form.is_valid():
            request.session['productosExportados'] = True

            #Se obtienen las entradas de producto en formato JSON
            data = serializers.serialize("json", Producto.objects.all())
            fs = FileSystemStorage('inventario/tmp/')

            #Se utiliza la variable fs para acceder a la carpeta con mas facilidad
            with fs.open("productos.json", "w") as out:
                out.write(data)
                out.close()  

            with fs.open("productos.json", "r") as out:                 
                response = HttpResponse(out.read(), content_type="application/force-download")
                response['Content-Disposition'] = 'attachment; filename="productos.json"'
                out.close() 
            #------------------------------------------------------------
            return response

    def get(self,request):
        form = ExportarProductosFormulario()

        if request.session.get('productosExportados') == True:
            exportado = request.session.get('productoExportados')
            contexto = { 'form':form,'productosExportados': exportado  }
            request.session['productosExportados'] = False

        else:
            contexto = {'form':form}
            contexto = complementarContexto(contexto,request.user) 
        return render(request, 'inventario/producto/exportarProductos.html',contexto)
#Fin de vista-------------------------------------------------------------------------#




#Muestra el formulario de un producto especifico para editarlo----------------------------------#
class EditarProducto(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request,pk):
        # Crea una instancia del formulario y la llena con los datos:
        form = ProductoFormulario(request.POST)
        # Revisa si es valido:
        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            descripcion = form.cleaned_data['descripcion']
            precio_unitario = form.cleaned_data['precio_unitario']
            precio_cash = form.cleaned_data['precio_cash']
            marca = form.cleaned_data['marca']
            proveedor = form.cleaned_data['proveedor']

            prod = Producto.objects.get(id=pk)
            prod.descripcion = descripcion
            prod.precio_unitario = precio_unitario
            prod.precio_cash = precio_cash
            prod.marca = marca
            prod.proveedor = proveedor
            prod.save()
            form = ProductoFormulario(instance=prod)
            messages.success(request, 'Actualizado exitosamente el producto de ID %s.' % pk)
            request.session['productoProcesado'] = 'editado'            
            return HttpResponseRedirect("/inventario/editarProducto/%s" % prod.id)
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/producto/agregarProducto.html', {'form': form})

    def get(self, request,pk): 
        prod = Producto.objects.get(id=pk)
        form = ProductoFormulario(instance=prod)
        #Envia al usuario el formulario para que lo llene
        contexto = {'form':form , 'modo':request.session.get('productoProcesado'),'editar':True}    
        contexto = complementarContexto(contexto,request.user) 
        return render(request, 'inventario/producto/agregarProducto.html', contexto)
#Fin de vista------------------------------------------------------------------------------------#      


#Crea una lista de los empleados, 10 por pagina----------------------------------------#
class ListarEmpleados(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        from django.db import models
        #Saca una lista de todos los empleados de la BDD
        empleados = Empleado.objects.all()                
        contexto = {'tabla': empleados}
        contexto = complementarContexto(contexto,request.user)         

        return render(request, 'inventario/empleado/listarEmpleados.html',contexto) 
#Fin de vista--------------------------------------------------------------------------#




#Crea y procesa un formulario para agregar a un empleado---------------------------------#
class AgregarEmpleado(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None
    @nivel_requerido(nivel_minimo=1)
    def post(self, request):
        # Crea una instancia del formulario y la llena con los datos:
        form = EmpleadoFormulario(request.POST)
        # Revisa si es valido:

        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere

            dui = form.cleaned_data['dui']
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            nacimiento = form.cleaned_data['nacimiento']
            telefono = form.cleaned_data['telefono']
            correo = form.cleaned_data['correo']

            empleado = Empleado(dui=dui,nombre=nombre,apellido=apellido,
                nacimiento=nacimiento,telefono=telefono,
                correo=correo)
            empleado.save()
            form = EmpleadoFormulario()

            messages.success(request, 'Ingresado exitosamente bajo la ID %s.' % empleado.id)
            request.session['empleadoProcesado'] = 'agregado'
            return HttpResponseRedirect("/inventario/agregarEmpleado")
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/empleado/agregarEmpleado.html', {'form': form})        

    def get(self,request):
        form = EmpleadoFormulario()
        #Envia al usuario el formulario para que lo llene
        contexto = {'form':form , 'modo':request.session.get('empleadoProcesado')} 
        contexto = complementarContexto(contexto,request.user)      # Agregar para reflejar user   
        return render(request, 'inventario/empleado/agregarEmpleado.html', contexto)
#Fin de vista-----------------------------------------------------------------------------#        




#Formulario simple que procesa un script para importar los empleados-----------------#
class ImportarEmpleados(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request):
        form = ImportarEmpleadosFormulario(request.POST)
        if form.is_valid():
            request.session['empleadosImportados'] = True
            return HttpResponseRedirect("/inventario/importarEmpleados")

    def get(self,request):
        form = ImportarEmpleadosFormulario()

        if request.session.get('empleadosImportados') == True:
            importado = request.session.get('empleadosImportados')
            contexto = { 'form':form,'empleadosImportados': importado  }
            request.session['empleadosImportados'] = False

        else:
            contexto = {'form':form}
            contexto = complementarContexto(contexto,request.user)             
        return render(request, 'inventario/empleado/importarEmpleados.html',contexto)
#Fin de vista-------------------------------------------------------------------------#




#Formulario simple que crea un archivo y respalda los empleados-----------------------#
class ExportarEmpleados(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request):
        form = ExportarEmpleadosFormulario(request.POST)
        if form.is_valid():
            request.session['empleadosExportados'] = True

            #Se obtienen las entradas de producto en formato JSON
            data = serializers.serialize("json", Empleado.objects.all())
            fs = FileSystemStorage('inventario/tmp/')

            #Se utiliza la variable fs para acceder a la carpeta con mas facilidad
            with fs.open("empleados.json", "w") as out:
                out.write(data)
                out.close()  

            with fs.open("empleados.json", "r") as out:                 
                response = HttpResponse(out.read(), content_type="application/force-download")
                response['Content-Disposition'] = 'attachment; filename="empleados.json"'
                out.close() 
            #------------------------------------------------------------
            return response

    def get(self,request):
        form = ExportarEmpleadosFormulario()

        if request.session.get('empleadosExportados') == True:
            exportado = request.session.get('empleadosExportados')
            contexto = { 'form':form,'empleadosExportados': exportado  }
            request.session['empleadosExportados'] = False

        else:
            contexto = {'form':form}
            contexto = complementarContexto(contexto,request.user) 
        return render(request, 'inventario/empleado/exportarEmpleados.html',contexto)
#Fin de vista-------------------------------------------------------------------------#




#Muestra el mismo formulario del empleado pero con los datos a editar----------------------#
class EditarEmpleado(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None
    @nivel_requerido(nivel_minimo=1)
    def post(self,request,pk):
        # Crea una instancia del formulario y la llena con los datos:
        empleado = Empleado.objects.get(id=pk)
        form = EmpleadoFormulario(request.POST, instance=empleado)
        # Revisa si es valido:
    
        if form.is_valid():           
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            dui = form.cleaned_data['dui']
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            nacimiento = form.cleaned_data['nacimiento']
            telefono = form.cleaned_data['telefono']
            correo = form.cleaned_data['correo']

            empleado.dui = dui
            empleado.nombre = nombre
            empleado.apellido = apellido
            empleado.nacimiento = nacimiento
            empleado.telefono = telefono
            empleado.correo = correo
            empleado.save()
            form = EmpleadoFormulario(instance=empleado)

            messages.success(request, 'Actualizado exitosamente el empleado de ID %s.' % pk)
            request.session['empleadoProcesado'] = 'editado'            
            return HttpResponseRedirect("/inventario/editarEmpleado/%s" % empleado.id)
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/empleado/agregarEmpleado.html', {'form': form})

    def get(self, request,pk): 
        empleado = Empleado.objects.get(id=pk)
        form = EmpleadoFormulario(instance=empleado)
        #Envia al usuario el formulario para que lo llene
        contexto = {'form':form , 'modo':request.session.get('empleadoProcesado'),'editar':True} 
        contexto = complementarContexto(contexto,request.user)     
        return render(request, 'inventario/empleado/agregarEmpleado.html', contexto)  
#Fin de vista--------------------------------------------------------------------------------# 


# #Genera la factura en PDF--------------------------------------------------------------------------#
# class GenerarFacturaPDF(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def get(self, request, p):
#         import io
#         from reportlab.pdfgen import canvas
#         import datetime

#         factura = Factura.objects.get(id=pk)
#         general = Opciones.objects.get(id=1)
#         detalles = DetalleFactura.objects.filter(id_factura_id=pk)          

#         data = {
#              'fecha': factura.fecha, 
#              'monto_general': factura.monto_general,
#             'nombre_empleado': factura.empleado.nombre + " " + factura.empleado.apellido,
#             'dui_empleado': factura.empleado.dui,
#             'id_reporte': factura.id,
#             'iva': factura.iva.valor_iva,
#             'detalles': detalles,
#             'modo': 'factura',
#             'general':general
#         }

#         nombre_factura = "factura_%s.pdf" % (factura.id)

#         pdf = render_to_pdf('inventario/PDF/prueba.html', data)
#         response = HttpResponse(pdf,content_type='application/pdf')
#         response['Content-Disposition'] = 'attachment; filename="%s"' % nombre_factura

#         return response  

#         #Fin de vista--------------------------------------------------------------------------------------#


#Crea una lista de los empleados, 10 por pagina----------------------------------------#
class ListarProveedores(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        from django.db import models
        #Saca una lista de todos los empleados de la BDD
        proveedores = Proveedor.objects.all()                
        contexto = {'tabla': proveedores}
        contexto = complementarContexto(contexto,request.user)         

        return render(request, 'inventario/proveedor/listarProveedores.html',contexto) 
#Fin de vista--------------------------------------------------------------------------#


#Crea y procesa un formulario para agregar a un proveedor---------------------------------#
class AgregarProveedor(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        # Crea una instancia del formulario y la llena con los datos:
        form = ProveedorFormulario(request.POST)
        # Revisa si es valido:
        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            proveedor = form.save()
            
            messages.success(request, 'Ingresado exitosamente bajo la ID %s.' % proveedor.id)
            request.session['proveedorProcesado'] = 'agregado'
            return HttpResponseRedirect("/inventario/agregarProveedor")
        else:
            # De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/proveedor/agregarProveedor.html', {'form': form})

    def get(self, request):
        form = ProveedorFormulario()
        # Envia al usuario el formulario para que lo llene
        contexto = {'form': form, 'modo': request.session.get('proveedorProcesado')}
        return render(request, 'inventario/proveedor/agregarProveedor.html', contexto)#Formulario simple que procesa un script para importar los proveedores-----------------#

class ImportarProveedores(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request):
        form = ImportarEmpleadosFormulario(request.POST)
        if form.is_valid():
            request.session['empleadosImportados'] = True
            return HttpResponseRedirect("/inventario/importarEmpleados")

    def get(self,request):
        form = ImportarEmpleadosFormulario()

        if request.session.get('empleadosImportados') == True:
            importado = request.session.get('empleadosImportados')
            contexto = { 'form':form,'empleadosImportados': importado  }
            request.session['empleadosImportados'] = False

        else:
            contexto = {'form':form}
            contexto = complementarContexto(contexto,request.user)             
        return render(request, 'inventario/importarEmpleados.html',contexto)
#Fin de vista-------------------------------------------------------------------------#




#Muestra el mismo formulario del empleado pero con los datos a editar----------------------#
class EditarProveedor(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request,pk):
        # Crea una instancia del formulario y la llena con los datos:
        proveedor = Proveedor.objects.get(id=pk)
        form = ProveedorFormulario(request.POST, instance=proveedor)
        # Revisa si es valido:
      
        if form.is_valid():           
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            dui = form.cleaned_data['dui']
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            direccion = form.cleaned_data['direccion']
            telefono = form.cleaned_data['telefono']
            correo = form.cleaned_data['correo']

            proveedor.dui = dui
            proveedor.nombre = nombre
            proveedor.apellido = apellido
            proveedor.direccion = direccion
            proveedor.telefono = telefono
            proveedor.correo = correo
            proveedor.save()
            form = ProveedorFormulario(instance=proveedor)

            messages.success(request, 'Actualizado exitosamente el proveedor de ID %s.' % pk)
            request.session['proveedorProcesado'] = 'editado'            
            return HttpResponseRedirect("/inventario/editarProveedor/%s" % proveedor.id)
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/proveedor/agregarProveedor.html', {'form': form})

    def get(self, request,pk): 
        proveedor = Proveedor.objects.get(id=pk)
        form = ProveedorFormulario(instance=proveedor)
        #Envia al usuario el formulario para que lo llene
        contexto = {'form':form , 'modo':request.session.get('proveedorProcesado'),'editar':True} 
        contexto = complementarContexto(contexto,request.user)     
        return render(request, 'inventario/proveedor/agregarProveedor.html', contexto)  
#Fin de vista--------------------------------------------------------------------------------#



# #Genera el compra en PDF--------------------------------------------------------------------------#
# class GenerarCompraPDF(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def get(self, request, p):

#         compra = Compra.objects.get(id=pk)
#         general = Opciones.objects.get(id=1)
#         detalles = DetalleCompra.objects.filter(id_compra_id=pk)


#         data = {
#              'fecha': compra.fecha, 
#              'monto_general': compra.monto_general,
#             'nombre_proveedor': compra.proveedor.nombre + " " + compra.proveedor.apellido,
#             'dui_proveedor': compra.proveedor.dui,
#             'id_reporte': compra.id,
#             'detalles': detalles,
#             'modo' : 'compra',
#             'general': general
#         }

#         nombre_compra = "compra_%s.pdf" % (compra.id)

#         pdf = render_to_pdf('inventario/PDF/prueba.html', data)
#         response = HttpResponse(pdf,content_type='application/pdf')
#         response['Content-Disposition'] = 'attachment; filename="%s"' % nombre_compra

#         return response 
#         #Fin de vista--------------------------------------------------------------------------------------#


#Crea un nuevo usuario--------------------------------------------------------------#
class CrearUsuario(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None    
    @nivel_requerido(nivel_minimo=1)
    def get(self, request):
        if request.user.is_superuser:
            form = NuevoUsuarioFormulario()
            #Envia al usuario el formulario para que lo llene
            contexto = {'form':form , 'modo':request.session.get('usuarioCreado')}   
            contexto = complementarContexto(contexto,request.user)  
            return render(request, 'inventario/usuario/crearUsuario.html', contexto)
        else:
            messages.error(request, 'No tiene los permisos para crear un usuario nuevo')
            return HttpResponseRedirect('/inventario/panel')

    def post(self, request):
        form = NuevoUsuarioFormulario(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            rep_password = form.cleaned_data['rep_password']
            level = form.cleaned_data['level']

            error = 0

            if password == rep_password:
                pass

            else:
                error = 1
                messages.error(request, 'La clave y su repeticion tienen que coincidir')

            if usuarioExiste(Usuario,'username',username) is False:
                pass

            else:
                error = 1
                messages.error(request, "El nombre de usuario '%s' ya existe. eliga otro!" % username)


            if usuarioExiste(Usuario,'email',email) is False:
                pass

            else:
                error = 1
                messages.error(request, "El correo '%s' ya existe. eliga otro!" % email)                    

            if(error == 0):
                if level == '0':
                    nuevoUsuario = Usuario.objects.create_user(username=username,password=password,email=email)
                    nivel = 0
                elif level == '1':
                    nuevoUsuario = Usuario.objects.create_superuser(username=username,password=password,email=email)
                    nivel = 1

                nuevoUsuario.first_name = first_name
                nuevoUsuario.last_name = last_name
                nuevoUsuario.nivel = nivel
                nuevoUsuario.save()

                messages.success(request, 'Usuario creado exitosamente')
                return HttpResponseRedirect('/inventario/crearUsuario')

            else:
                return HttpResponseRedirect('/inventario/crearUsuario')
                        
                   



#Fin de vista----------------------------------------------------------------------


#Lista todos los usuarios actuales--------------------------------------------------------------#
class ListarUsuarios(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None    

    def get(self, request):
        usuarios = Usuario.objects.all()
        #Envia al usuario el formulario para que lo llene
        contexto = {'tabla':usuarios}   
        contexto = complementarContexto(contexto,request.user)  
        return render(request, 'inventario/usuario/listarUsuarios.html', contexto)

    def post(self, request):
        pass   

#Fin de vista----------------------------------------------------------------------



#Importa toda la base de datos, primero crea una copia de la actual mientras se procesa la nueva--#
class ImportarBDD(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        if request.user.is_superuser == False:
            messages.error(request, 'Solo los administradores pueden importar una nueva base de datos')  
            return HttpResponseRedirect('/inventario/panel')

        form = ImportarBDDFormulario()
        contexto = { 'form': form }
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/BDD/importar.html', contexto)

    def post(self, request):
        form = ImportarBDDFormulario(request.POST, request.FILES)

        if form.is_valid():
            ruta = 'inventario/archivos/BDD/inventario_respaldo.xml'
            manejarArchivo(request.FILES['archivo'],ruta)

            try:
                call_command('loaddata', ruta, verbosity=0)
                messages.success(request, 'Base de datos subida exitosamente')
                return HttpResponseRedirect('/inventario/importarBDD')
            except Exception:
                messages.error(request, 'El archivo esta corrupto')
                return HttpResponseRedirect('/inventario/importarBDD')





#Fin de vista--------------------------------------------------------------------------------


#Descarga toda la base de datos en un archivo---------------------------------------------#
class DescargarBDD(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        #Se obtiene la carpeta donde se va a guardar y despues se crea el respaldo ahi
        fs = FileSystemStorage('inventario/archivos/tmp/')
        with fs.open('inventario_respaldo.xml','w') as output:
            call_command('dumpdata','inventario',indent=4,stdout=output,format='xml', 
                exclude=['contenttypes', 'auth.permission'])

            output.close()

        #Lo de abajo es para descargarlo
        with fs.open('inventario_respaldo.xml','r') as output:
            response = HttpResponse(output.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'attachment; filename="inventario_respaldo.xml"'

            #Cierra el archivo
            output.close()

            #Borra el archivo
            ruta = 'inventario/archivos/tmp/inventario_respaldo.xml'
            call_command('erasefile',ruta)

            #Regresa el archivo a descargar
            return response


#Fin de vista--------------------------------------------------------------------------------


#Configuracion general de varios elementos--------------------------------------------------#
class ConfiguracionGeneral(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        conf = Opciones.objects.get(id=1)
        form = OpcionesFormulario()
        
        #Envia al usuario el formulario para que lo llene

        form['moneda'].field.widget.attrs['value']  = conf.moneda
        form['valor_iva'].field.widget.attrs['value']  = conf.valor_iva
        form['mensaje_factura'].field.widget.attrs['value']  = conf.mensaje_factura
        form['nombre_negocio'].field.widget.attrs['value']  = conf.nombre_negocio

        contexto = {'form':form}    
        contexto = complementarContexto(contexto,request.user) 
        return render(request, 'inventario/opciones/configuracion.html', contexto)

    def post(self,request):
        # Crea una instancia del formulario y la llena con los datos:
        form = OpcionesFormulario(request.POST,request.FILES)
        # Revisa si es valido:

        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            moneda = form.cleaned_data['moneda']
            valor_iva = form.cleaned_data['valor_iva']
            mensaje_factura = form.cleaned_data['mensaje_factura']
            nombre_negocio = form.cleaned_data['nombre_negocio']
            imagen = request.FILES.get('imagen',False)

            #Si se subio un logo se sobreescribira en la carpeta ubicada
            #--en la siguiente ruta
            if imagen:
                manejarArchivo(imagen,'inventario/static/inventario/assets/logo/logo3.png')

            conf = Opciones.objects.get(id=1)
            conf.moneda = moneda
            conf.valor_iva = valor_iva
            conf.mensaje_factura = mensaje_factura
            conf.nombre_negocio = nombre_negocio
            conf.save()


            messages.success(request, 'Configuracion actualizada exitosamente!')          
            return HttpResponseRedirect("/inventario/configuracionGeneral")
        else:
            form = OpcionesFormulario(instance=conf)
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/opciones/configuracion.html', {'form': form})

#Fin de vista--------------------------------------------------------------------------------


#Accede a los modulos del manual de usuario---------------------------------------------#
class VerManualDeUsuario(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, pagina):
        if pagina == 'inicio':
            return render(request, 'inventario/manual/index.html') 

        if pagina == 'producto':
            return render(request, 'inventario/manual/producto.html') 

        if pagina == 'proveedor':
            return render(request, 'inventario/manual/proveedor.html') 

        if pagina == 'compra':
            return render(request, 'inventario/manual/compra.html') 

        if pagina == 'empleados':
            return render(request, 'inventario/manual/empleados.html') 

        if pagina == 'factura':
            return render(request, 'inventario/manual/factura.html') 

        if pagina == 'usuarios':
            return render(request, 'inventario/manual/usuarios.html')

        if pagina == 'opciones':
            return render(request, 'inventario/manual/opciones.html')

#listar Marca
class ListarMarca(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        marcas = Marca.objects.all()
        contexto = {'tabla': marcas}
        contexto = complementarContexto(contexto,request.user) 
        return render(request, 'inventario/marca/listarMarca.html', contexto)
#Agregar Marca

class AgregarMarca(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        # Crea una instancia del formulario y la llena con los datos:
        form = MarcaFormulario(request.POST)
        # Revisa si es valido:
        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            nombre = form.cleaned_data['nombre']

            marca =Marca(nombre=nombre)
            marca.save()
            
            form = MarcaFormulario()
            messages.success(request, 'Ingresado exitosamente bajo la ID %s.' % marca.id)
            request.session['marcaProcesado'] = 'agregado'
            return HttpResponseRedirect("/inventario/agregarMarca")
        else:
            # De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/marca/agregarMarca.html', {'form': form})

    # Si se llega por GET crearemos un formulario en blanco
    def get(self, request):
        form = MarcaFormulario()
        # Envia al usuario el formulario para que lo llene
        contexto = {'form': form, 'modo': request.session.get('marcaProcesado')}
        contexto = complementarContexto(contexto,request.user) 
        return render(request, 'inventario/marca/agregarMarca.html', contexto)
    

#editar Marca
class EditarMarca(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request,pk):
        marca = Marca.objects.get(id=pk)
        form = MarcaFormulario(request.POST, instance=marca)
        if form.is_valid():           
            nombre = form.cleaned_data['nombre']
            marca.nombre = nombre
            marca.save()
            form = MarcaFormulario(instance=marca)
            messages.success(request, 'Actualizado exitosamente la marca de ID %s.' % pk)
            request.session['marcaProcesado'] = 'editado'            
            return HttpResponseRedirect("/inventario/editarMarca/%s" % marca.id)
        else:
            return render(request, 'inventario/marca/agregarMarca.html', {'form': form})
    def get(self, request,pk): 
        marca = Marca.objects.get(id=pk)
        form = MarcaFormulario(instance=marca)
        contexto = {'form':form , 'modo':request.session.get('marcaProcesado'),'editar':True} 
        contexto = complementarContexto(contexto,request.user)     
        return render(request, 'inventario/marca/agregarMarca.html', contexto)
    
#Listar Estado
class ListarEstado(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        from django.db import models
        estados = Estado.objects.all()
        contexto = {'tabla': estados}
        contexto = complementarContexto(contexto,request.user)    
        return render(request, 'inventario/estado/listarEstado.html', contexto)
    
class AgregarEstado(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None
    @nivel_requerido(nivel_minimo=1)
    def post(self, request):
        # Crea una instancia del formulario y la llena con los datos:
        form = EstadoFormulario(request.POST)
        # Revisa si es valido:
        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            nombre = form.cleaned_data['nombre']

            estado = Estado(nombre=nombre)
            estado.save()
            
            form = EstadoProductoFormulario()
            messages.success(request, 'Ingresado exitosamente bajo la ID %s.' % estado.id)
            request.session['estadoProductoProcesado'] = 'agregado'
            return HttpResponseRedirect("/inventario/agregarEstado")
        else:
            # De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/estado/agregarEstado.html', {'form': form})

    # Si se llega por GET crearemos un formulario en blanco
    def get(self, request):
        form = EstadoProductoFormulario()
        # Envia al usuario el formulario para que lo llene
        contexto = {'form': form, 'modo': request.session.get('estadoProcesado')}
        return render(request, 'inventario/estado/agregarEstado.html', contexto)
    

class EditarEstado(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None
    @nivel_requerido(nivel_minimo=1)
    def post(self,request,pk):
        # Crea una instancia del formulario y la llena con los datos:
        form = EstadoFormulario(request.POST)
        # Revisa si es valido:
        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            nombre = form.cleaned_data['nombre']
            entity = Estado.objects.get(id=pk)
            entity.nombre = nombre
            entity.save()
            form = EstadoProductoFormulario(instance=entity)
            messages.success(request, 'Actualizado exitosamente el estado de ID %s.' % pk)
            request.session['estadoProcesado'] = 'editado'            
            return HttpResponseRedirect("/inventario/editarEstado/%s" % entity.id)
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/estado/agregarEstado.html', {'form': form})

    def get(self, request,pk): 
        entity = Estado.objects.get(id=pk)
        form = EstadoFormulario(instance=entity)
        #Envia al usuario el formulario para que lo llene
        contexto = {'form':form , 'modo':request.session.get('estadoProcesado'),'editar':True}    
        contexto = complementarContexto(contexto,request.user) 
        return render(request, 'inventario/estado/agregarEstado.html', contexto)
#Fin de vista------------------------------------------------------------------------------------#  
#listar Bodega
class ListarBodega(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        entity = Bodega.objects.all()
        contexto = {'tabla': entity}
        contexto = complementarContexto(contexto,request.user) 
        return render(request, 'inventario/bodega/listarBodega.html', contexto)
#Agregar Bodega

class AgregarBodega(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None
    @nivel_requerido(nivel_minimo=1)
    def post(self, request):
        # Crea una instancia del formulario y la llena con los datos:
        form = BodegaFormulario(request.POST)
        # Revisa si es valido:
        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            nombre = form.cleaned_data['nombre']
            ubicacion = form.cleaned_data['ubicacion']
            estado = form.cleaned_data['estado']

            bodega =Bodega(nombre=nombre,ubicacion=ubicacion,estado=estado)
            bodega.save()
            
            form = BodegaFormulario()
            messages.success(request, 'Ingresado exitosamente bajo la ID %s.' % bodega.id)
            request.session['bodegaProcesado'] = 'agregado'
            return HttpResponseRedirect("/inventario/agregarBodega")
        else:
            # De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/bodega/agregarBodega.html', {'form': form})

    # Si se llega por GET crearemos un formulario en blanco
    def get(self, request):
        form = BodegaFormulario()
        # Envia al usuario el formulario para que lo llene
        contexto = {'form': form, 'modo': request.session.get('bodegaProcesado')}
        contexto = complementarContexto(contexto,request.user) 
        return render(request, 'inventario/bodega/agregarBodega.html', contexto)
    

#editar Marca
class EditarBodega(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None
    @nivel_requerido(nivel_minimo=1)
    def post(self,request,pk):
        bodega = Bodega.objects.get(id=pk)
        form = BodegaFormulario(request.POST, instance=bodega)
        if form.is_valid():           
            nombre = form.cleaned_data['nombre']
            ubicacion = form.cleaned_data['ubicacion']
            estado = form.cleaned_data['estado']

            bodega.nombre = nombre
            bodega.ubicacion = ubicacion
            bodega.estado = estado

            bodega.save()
            form = BodegaFormulario(instance=bodega)
            messages.success(request, 'Actualizado exitosamente la bodega de ID %s.' % pk)
            request.session['bodegaProcesado'] = 'editado'            
            return HttpResponseRedirect("/inventario/editarBodega/%s" % bodega.id)
        else:
            return render(request, 'inventario/bodega/agregarBodega.html', {'form': form})
    def get(self, request,pk): 
        bodega = Bodega.objects.get(id=pk)
        form = BodegaFormulario(instance=bodega)
        contexto = {'form':form , 'modo':request.session.get('bodegaProcesado'),'editar':True} 
        contexto = complementarContexto(contexto,request.user)     
        return render(request, 'inventario/bodega/agregarBodega.html', contexto)

#Reparacion
#listar Rep

class ListarRep(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        # Crear el formulario con los datos GET
        form = FiltrosRep(request.GET)

        # Obtener todas las reparaciones
        reparaciones = Reparacion.objects.all()

        # Aplicar filtros si el formulario es válido
        if form.is_valid():
            if form.cleaned_data.get('idproducto'):
                reparaciones = reparaciones.filter(idproducto=form.cleaned_data['idproducto'])
            # Filtro por fecha_retorno
            fecha_retorno = form.cleaned_data.get('fecha_retorno')
            if fecha_retorno:
                reparaciones = reparaciones.annotate(fecha_solo_fecha=TruncDate('fecha_retorno')).filter(fecha_solo_fecha=fecha_retorno)

            if form.cleaned_data.get('estado'):
                reparaciones = reparaciones.filter(estado=form.cleaned_data['estado'])

        # Ordenar por fecha de retorno (descendente por defecto)
        orden = request.GET.get('orden', '-fecha_retorno')
        reparaciones = reparaciones.order_by(orden)

        # Preparar el contexto para la plantilla
        contexto = {
            'reparaciones': reparaciones,
            'form': form,
        }

        # Complementar con datos adicionales (si aplica)
        contexto = complementarContexto(contexto, request.user)

        return render(request, 'inventario/reparacion/listarRep.html', contexto)

#Agregar Rep
class AgregarRep(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None
    

    def get(self, request):
        form = ReparacionFormulario()
        contexto = {'form': form}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/reparacion/agregarRep.html', contexto)


    def post(self, request):
        form = ReparacionFormulario(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    idproducto = form.cleaned_data['idproducto']
                    bodega_origen = form.cleaned_data['bodega_origen']
                    idempleado = form.cleaned_data['idempleado']
                    fecha_retorno = form.cleaned_data['fecha_retorno']
                    motivo = form.cleaned_data['motivo']
                    desde_devolucion = request.POST.get('desde_devolucion', 'false') == 'true'

                    if desde_devolucion:
                        devolucion = Devolucion.objects.get(idproducto=idproducto, idempleado=idempleado,motivo=motivo)
                        if devolucion.cantidad == 1:
                            devolucion.enviado_a_reparacion = True
                        devolucion.cantidad -= 1
                        devolucion.save()

                    # Crear la reparación
                    rep = Reparacion(
                        idproducto=idproducto,
                        bodega_origen=bodega_origen,
                        idempleado=idempleado,
                        fecha_retorno=fecha_retorno,
                        estado=EstadoProducto.objects.get(nombre='En reparación'),
                        motivo=motivo,
                        desde_devolucion=desde_devolucion,
                    )
                    rep.save()
                    
                    # Crear el movimiento
                    movimiento = MovimientoProducto(
                        producto=idproducto,
                        empleado=idempleado,
                        usuario=request.user,
                        bodega=bodega_origen,
                        estado_producto=EstadoProducto.objects.get(nombre='En reparación'),
                        cantidad=1,
                        tipo_movimiento='Reparacion',
                    )
                    movimiento.save()

                # Mensaje de éxito
                messages.success(request, f'Reparación registrada exitosamente bajo la ID {rep.id}.')
                request.session['repProcesado'] = 'agregado'
                if desde_devolucion:
                    return redirect('inventario:listarDev')
                else:
                    return redirect('inventario:agregarRep')

            except ValidationError as e:
                messages.error(request, f"Error de validación: {e}")
            except Exception as e:
                messages.error(request, f"Error inesperado: {e}")
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario.")

        contexto = {'form': form}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/reparacion/agregarRep.html', contexto)

class MarcarRep(View):
    def post(self, request, pk):
        # Obtener la reparación correspondiente
        reparacion = get_object_or_404(Reparacion, id=pk)

        # Asegurarse de que el artículo esté reparado
        if reparacion.estado != EstadoProducto.objects.get(nombre='Reparado'):
            reparacion.estado = EstadoProducto.objects.get(nombre='Reparado')
            

            # Actualizar el inventario: Aumentar el stock del producto reparado
            inventario = Inventario.objects.get(idproducto=reparacion.idproducto, idbodega=reparacion.bodega_origen)
            inventario.aumentar_stock(1)

            # Registrar el movimiento como reparado
            movimiento= MovimientoProducto.objects.create(
                producto=reparacion.idproducto,
                empleado = reparacion.idempleado,
                usuario = request.user,
                bodega=reparacion.bodega_origen,
                cantidad=1,
                estado_producto=EstadoProducto.objects.get(nombre='Reparado'),
                tipo_movimiento="Entrada",  # O lo que corresponda
            )
            movimiento.save()
            reparacion.save()
            messages.success(request, "El artículo ha sido marcado como reparado y el inventario actualizado.")
        else:
            messages.warning(request, "Este artículo ya está marcado como reparado.")

        # Redirigir a la página de listar reparaciones
        return redirect('inventario:listarRep')
    
#Estado producto
class ListarEstadoProducto(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        from django.db import models
        estados = EstadoProducto.objects.all()
        contexto = {'tabla': estados}
        contexto = complementarContexto(contexto,request.user)    
        return render(request, 'inventario/estadoproducto/listarEstadoProducto.html', contexto)
    
class AgregarEstadoProducto(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None
    @nivel_requerido(nivel_minimo=1)
    def post(self, request):
        # Crea una instancia del formulario y la llena con los datos:
        form = EstadoProductoFormulario(request.POST)
        # Revisa si es valido:
        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            nombre = form.cleaned_data['nombre']

            estado_producto = EstadoProducto(nombre=nombre)
            estado_producto.save()
            
            form = EstadoProductoFormulario()
            messages.success(request, 'Ingresado exitosamente bajo la ID %s.' % estado_producto.id)
            request.session['estadoProductoProcesado'] = 'agregado'
            return HttpResponseRedirect("/inventario/agregarEstadoProducto")
        else:
            # De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/estadoproducto/agregarEstadoProducto.html', {'form': form})

    # Si se llega por GET crearemos un formulario en blanco
    def get(self, request):
        form = EstadoProductoFormulario()
        # Envia al usuario el formulario para que lo llene
        contexto = {'form': form, 'modo': request.session.get('estadoProductoProcesado')}
        return render(request, 'inventario/estadoproducto/agregarEstadoProducto.html', contexto)
    

class EditarEstadoProducto(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None
    @nivel_requerido(nivel_minimo=1)
    def post(self,request,pk):
        # Crea una instancia del formulario y la llena con los datos:
        form = EstadoProductoFormulario(request.POST)
        # Revisa si es valido:
        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            nombre = form.cleaned_data['nombre']
            prod = EstadoProducto.objects.get(id=pk)
            prod.nombre = nombre
            prod.save()
            form = EstadoProductoFormulario(instance=prod)
            messages.success(request, 'Actualizado exitosamente el estado de ID %s.' % pk)
            request.session['estadoProductoProcesado'] = 'editado'            
            return HttpResponseRedirect("/inventario/editarEstadoProducto/%s" % prod.id)
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/estadoproducto/agregarEstadoProducto.html', {'form': form})

    def get(self, request,pk): 
        prod = EstadoProducto.objects.get(id=pk)
        form = EstadoProductoFormulario(instance=prod)
        #Envia al usuario el formulario para que lo llene
        contexto = {'form':form , 'modo':request.session.get('estadoProductoProcesado'),'editar':True}    
        contexto = complementarContexto(contexto,request.user) 
        return render(request, 'inventario/estadoproducto/agregarEstadoProducto.html', contexto)
#Fin de vista------------------------------------------------------------------------------------#  

# Inventario
class ListarInventario(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        form = BuscarInventarioFormulario(request.GET)
        inventarios = Inventario.objects.all()

        # Filtrar según los criterios del formulario
        if form.is_valid():
            if form.cleaned_data['bodega']:
                inventarios = inventarios.filter(idbodega=form.cleaned_data['bodega'])
            if form.cleaned_data['producto']:
                inventarios = inventarios.filter(idproducto=form.cleaned_data['producto'])

        # Calcular el total de stock
        total_stock = sum(item.stock for item in inventarios)

        # Preparar el contexto
        contexto = {'tabla': inventarios, 'form': form, 'total_stock': total_stock}
        contexto = complementarContexto(contexto, request.user)

        # Renderizar la página con el contexto adecuado
        return render(request, 'inventario/inventario/listarInventario.html', contexto)
# Registro Inventario
class AgregarInventario(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        form = RegistroInventarioFormulario(request.POST)
        if form.is_valid():
            # Guardamos el registro de inventario, pero no confirmamos la base de datos aún
            registro = form.save(commit=False)

            # Obtenemos el inventario o lo creamos si no existe
            inventario, _ = Inventario.objects.get_or_create(
                idbodega=registro.bodega,
                idproducto=registro.producto,
                defaults={'stock': 0, 'estado': EstadoProducto.objects.get(nombre='Disponible')}
            )

            # Aumentamos el stock de inventario
            inventario.aumentar_stock(registro.cantidad)
            inventario.save()

            # Actualizamos el estado del registro de inventario y ajustamos el stock
            registro.estado = EstadoProducto.objects.get(nombre='Disponible')
            registro.ajustar_stock(registro.cantidad)
            # Registramos el movimiento de producto
            MovimientoProducto.objects.create(
                producto=registro.producto,
                bodega=registro.bodega,
                tipo_movimiento='entrada',  # Tipo de movimiento, 'entrada' para agregar productos
                cantidad=registro.cantidad/2,
                usuario=request.user,
                empleado=None,
                estado_producto=registro.estado
            )

            # Mensaje de éxito
            messages.success(request, 'Registro de inventario agregado exitosamente y stock actualizado.')
            return HttpResponseRedirect("/inventario/agregarInventario")
        else:
            return render(request, 'inventario/inventario/agregarInventario.html', {'form': form})

    def get(self, request):
        form = RegistroInventarioFormulario()
        contexto = {'form': form}
        
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/inventario/agregarInventario.html', contexto)



from django.utils.dateparse import parse_date

class ListarMovimientoProducto(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    template_name = 'inventario/movimientoproducto/listarMovimientoProducto.html'

    def get(self, request):
        form = MovimientoProductoFormulario(request.GET)
        movimientos = MovimientoProducto.objects.all().order_by('-fecha_movimiento')
        
        # Manejo de fechas
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        
        if fecha_inicio:
            fecha_inicio = parse_date(fecha_inicio)
            if fecha_inicio:
                movimientos = movimientos.filter(fecha_movimiento__date__gte=fecha_inicio)
        
        if fecha_fin:
            fecha_fin = parse_date(fecha_fin)
            if fecha_fin:
                movimientos = movimientos.filter(fecha_movimiento__date__lte=fecha_fin)

        # Aplicar filtros
        if form.is_valid():
            data = form.cleaned_data
            if data['bodega']: movimientos = movimientos.filter(bodega=data['bodega'])
            if data['producto']: movimientos = movimientos.filter(producto=data['producto'])
            if data['empleado']: movimientos = movimientos.filter(empleado=data['empleado'])
            if data['estado_producto']: movimientos = movimientos.filter(estado_producto=data['estado_producto'])
            if data['tipo_movimiento']: movimientos = movimientos.filter(tipo_movimiento=data['tipo_movimiento'])

        # Nuevo agrupamiento por empleado y fecha
        grupos = defaultdict(lambda: {
            'empleado': None,
            'fecha': None,
            'detalles': [],
            'resumen': {
                'total_movimientos': 0,
                'total_cantidad': 0,
                'tipos_movimiento': set()
            }
        })

        for movimiento in movimientos:
            clave = (movimiento.empleado, movimiento.fecha_movimiento.date())
            grupo = grupos[clave]
            
            if not grupo['empleado']:
                grupo['empleado'] = movimiento.empleado
                grupo['fecha'] = movimiento.fecha_movimiento.date()
            
            grupo['detalles'].append(movimiento)
            grupo['resumen']['total_movimientos'] += 1
            grupo['resumen']['total_cantidad'] += movimiento.cantidad
            grupo['resumen']['tipos_movimiento'].add(movimiento.get_tipo_movimiento_display())

        # Preparar datos para template
        grupos_ordenados = sorted(grupos.values(), key=lambda x: x['fecha'], reverse=True)
        
        context = {
            'grupos_movimientos': grupos_ordenados,
            'form': form,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        }
        context = complementarContexto(context, request.user)
        return render(request, self.template_name, context)
    
    
def verificar_stock(request):
    bodega_id = request.GET.get('bodega')
    producto_id = request.GET.get('producto')
    cantidad = int(request.GET.get('cantidad', 0))
    print('cantidad :' , cantidad)
    try:
        inventario = Inventario.objects.get(
            idbodega_id=bodega_id,
            idproducto_id=producto_id
        )
        return JsonResponse({
            'disponible': inventario.stock >= cantidad,
            'stock_actual': inventario.stock
        })
    except Inventario.DoesNotExist:
        return JsonResponse({'disponible': False, 'error': 'Producto no encontrado'})
    
    
@transaction.atomic
def agregarEntrega(request):
    if request.method == "POST":
        try:
            detalles = json.loads(request.POST.get('detalles', '[]'))
            if not detalles:
                raise ValidationError("Debe agregar al menos un producto")
            
            with transaction.atomic():
                entrega = Entrega.objects.create(
                    id_empleado_recibio_id=request.POST.get('empleado'),
                    id_empleado_autorizo=request.user
                )
                
                # Crear detalles
                detalles_a_crear = [
                    DetalleEntrega(
                        entrega=entrega,
                        producto_id=detalle['producto'],
                        bodega_id=detalle['bodega'],
                        cantidad=detalle['cantidad']
                    ) for detalle in detalles
                ]
                DetalleEntrega.objects.bulk_create(detalles_a_crear)
                
                # Procesar entrega
                entrega.procesar_entrega()
            
            messages.success(request, 'Entrega registrada exitosamente!')
            return redirect('inventario:agregarEntrega')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('inventario:agregarEntrega')
    
    return render(request, 'inventario/entrega/agregarEntrega.html', {
        'bodegas': Bodega.objects.all(),
        'empleados': Empleado.objects.all(),
        'productos': Producto.objects.all()
    })
# views.py


class ListarEmpleadosPendientes(LoginRequiredMixin, View):
    def get(self, request):
        # Obtener los movimientos pendientes
        movimientos_pendientes = MovimientoProducto.objects.filter(
            estado_producto__nombre='Pendiente'
        ).select_related('producto', 'empleado')

        # Organizar datos por empleado
        empleados = defaultdict(lambda: {'nombre': '', 'apellido': '', 'productos': {}})
        for movimiento in movimientos_pendientes:
            empleado_id = movimiento.empleado.id
            empleados[empleado_id]['nombre'] = movimiento.empleado.nombre
            empleados[empleado_id]['apellido'] = movimiento.empleado.apellido
            producto_id = movimiento.producto.id
            if producto_id not in empleados[empleado_id]['productos']:
                empleados[empleado_id]['productos'][producto_id] = {
                    'descripcion': movimiento.producto.descripcion,
                    'cantidad': movimiento.cantidad,
                    'movimiento_id': movimiento.id
                }

        # Obtener las bodegas disponibles
        bodegas = Bodega.objects.all()

        # Asegurarse de que empleados es un diccionario normal
        contexto = {
            'empleados': dict(empleados),
            'bodegas': bodegas,  # Agregar bodegas al contexto
        }
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/recepcion/empleadosPendientes.html', contexto)

    @method_decorator(csrf_exempt)
    def post(self, request):
        movimientos_pendientes = MovimientoProducto.objects.filter(
            estado_producto__nombre='Pendiente'
        ).select_related('producto', 'empleado')

        empleados = defaultdict(lambda: {'productos': []})
        for movimiento in movimientos_pendientes:
            empleado_id = movimiento.empleado.id
            empleados[empleado_id]['nombre'] = movimiento.empleado.nombre
            empleados[empleado_id]['apellido'] = movimiento.empleado.apellido
            empleados[empleado_id]['productos'].append({
                'descripcion': movimiento.producto.descripcion,
                'cantidad': movimiento.cantidad,
            })

        contexto = {'empleados': empleados}
        listado_html = render_to_string('inventario/recepcion/empleadosPendientes.html', contexto)
        
        contexto = complementarContexto(contexto, request.user)
        return JsonResponse({'success': True, 'listado_html': listado_html})

@require_POST
@transaction.atomic
def recepcion_producto(request):
    try:
        # Obtener datos del formulario
        producto_id = request.POST.get('producto_id')
        movimiento_id = request.POST.get('movimiento_id')
        cantidad_vendida = request.POST.get('cantidad_vendida', '0')  # Usamos '0' como valor predeterminado
        cantidad_recibida = request.POST.get('cantidad_recibida', '0')
        cantidad_recibida = int(cantidad_recibida) if cantidad_recibida else 0
        cantidad_vendida = int(cantidad_vendida) if cantidad_vendida else 0
        bodega_id = request.POST.get('bodega_id', '1')

        # Validaciones de cantidades
        if cantidad_vendida < 0 or cantidad_recibida < 0:
            raise ValueError("Las cantidades no pueden ser negativas.")

        # Obtener movimiento pendiente
        producto_pendiente = get_object_or_404(MovimientoProducto, id=movimiento_id, estado_producto__nombre='Pendiente')
        total_pendiente = producto_pendiente.cantidad
        
        # Validar que la suma de cantidades no exceda la cantidad pendiente
        if cantidad_vendida + cantidad_recibida > total_pendiente:
            raise ValueError(f"La suma excede la cantidad pendiente ({total_pendiente}).")

        # Procesar venta
        if cantidad_vendida > 0:
            MovimientoProducto.objects.create(
                bodega=producto_pendiente.bodega,
                producto=producto_pendiente.producto,
                tipo_movimiento='venta',
                cantidad=cantidad_vendida,
                usuario=request.user,
                empleado=producto_pendiente.empleado,
                estado_producto=get_object_or_404(EstadoProducto, nombre='Vendido')
            )

        # Procesar recepcion 
        if cantidad_recibida > 0:
            bodega = get_object_or_404(Bodega, id=int(bodega_id))
            MovimientoProducto.objects.create(
                bodega=bodega,
                producto=producto_pendiente.producto,
                tipo_movimiento='recepcion',
                cantidad=cantidad_recibida,
                usuario=request.user,
                empleado=producto_pendiente.empleado,
                estado_producto=get_object_or_404(EstadoProducto, nombre='Disponible')
            )

            # Obtenemos el inventario o lo creamos si no existe
            inventario, _ = Inventario.objects.get_or_create(
                idbodega=bodega,
                idproducto=producto_pendiente.producto,
                defaults={'stock': 0, 'estado': EstadoProducto.objects.get(nombre='Disponible')}
            )

            # Aumentamos el stock de inventario
            inventario.aumentar_stock(cantidad_recibida)
            inventario.save()

            #inventario.ajustar_stock(cantidad_recibida)
            # Mensaje de éxito
            messages.success(request, 'Registro de inventario agregado exitosamente y stock actualizado.')

        # Actualizar o eliminar el movimiento pendiente
        if cantidad_vendida + cantidad_recibida == total_pendiente:
            producto_pendiente.delete()
        else:
            producto_pendiente.cantidad -= (cantidad_vendida + cantidad_recibida)
            producto_pendiente.save()

        messages.success(request, "Recepción procesada correctamente.")
    except ValueError as ve:
        messages.error(request, f"Error de validación: {ve}")
    except Exception as e:
        messages.error(request, f"Error inesperado: {e}")

    return redirect('inventario:listarEmpleadosPendientes') 
    # Volver a listar los empleados pendientes
    # movimientos_pendientes = MovimientoProducto.objects.filter(
    #     estado_producto__nombre='Pendiente'
    # ).select_related('producto', 'empleado')

    # empleados = defaultdict(lambda: {'nombre': '', 'apellido': '', 'productos': {}})
    # for movimiento in movimientos_pendientes:
    #     empleado_id = movimiento.empleado.id
    #     empleados[empleado_id]['nombre'] = movimiento.empleado.nombre
    #     empleados[empleado_id]['apellido'] = movimiento.empleado.apellido
    #     producto_id = movimiento.producto.id
    #     if producto_id not in empleados[empleado_id]['productos']:
    #         empleados[empleado_id]['productos'][producto_id] = {
    #             'descripcion': movimiento.producto.descripcion,
    #             'cantidad': movimiento.cantidad,
    #             'movimiento_id': movimiento.id
    #         }
    # bodegas = Bodega.objects.all()
    # contexto = {'empleados': dict(empleados),
    #         'bodegas': bodegas,  # Agregar bodegas al contexto
    #             }
    # contexto = complementarContexto(contexto, request.user)

    # return render(request, 'inventario/recepcion/empleadosPendientes.html', contexto)

#Devoluciones
#@method_decorator(nivel_requerido(1), name='dispatch')
class ListarDev(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    #con filtros
    def get(self, request):
        form = FiltrosDev(request.GET)
        devoluciones = Devolucion.objects.all()

        if form.is_valid():
            if form.cleaned_data.get('idproducto'):
                devoluciones = devoluciones.filter(idproducto=form.cleaned_data['idproducto'])
            fecha_devolucion = form.cleaned_data.get('fecha_devolucion')
            if fecha_devolucion:
                devoluciones = devoluciones.annotate(fecha_solo_fecha=TruncDate('fecha_devolucion')).filter(fecha_solo_fecha=fecha_devolucion)
            if form.cleaned_data.get('idbodega'):
                devoluciones = devoluciones.filter(idbodega=form.cleaned_data['idbodega'])
            if form.cleaned_data.get('dañado'):
                devoluciones = devoluciones.filter(dañado=form.cleaned_data['dañado'])
        #ordenar por fecha de devolucion
        orden = request.GET.get('orden', '-fecha_devolucion')
        devoluciones = devoluciones.order_by(orden)
        #total de elementos listados para el html
        total = Devolucion.totalDevoluciones()
        contexto = {'tabla': devoluciones, 'form': form, 'total': total}

        contexto = complementarContexto(contexto, request.user)

        return render(request, 'inventario/recepcion/listarDev.html', contexto)
class AgregarDev(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        form = DevolucionFormulario(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    devolucion = form.save(commit=False)
                    devolucion.idempleado_recibio = request.user
                    #movimiento de devolucion
                    if form.cleaned_data['dañado']:
                        movimiento = MovimientoProducto(
                            producto=devolucion.idproducto,
                            empleado=devolucion.idempleado,
                            usuario=request.user,
                            bodega=devolucion.idbodega,
                            estado_producto=EstadoProducto.objects.get(nombre='Dañado'),
                            cantidad=devolucion.cantidad,
                            tipo_movimiento='Devolucion',
                        )
                    else:
                        movimiento = MovimientoProducto(
                            producto=devolucion.idproducto,
                            empleado=devolucion.idempleado,
                            usuario=request.user,
                            bodega=devolucion.idbodega,
                            estado_producto=EstadoProducto.objects.get(nombre='Disponible'),
                            cantidad=devolucion.cantidad,
                            tipo_movimiento='Devolucion',
                        )
                    movimiento.save()
                    devolucion.save()
                messages.success(request, 'Devolución registrada exitosamente.')
                return redirect('inventario:agregarDev')
            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"Error inesperado: {e}")
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
        
        contexto = {'form': form}
        
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/recepcion/agregarDev.html', contexto)

    def get(self, request):
        form = DevolucionFormulario()
        return render(request, 'inventario/recepcion/agregarDev.html', {'form': form})


from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Inventario
from django.template.loader import render_to_string
#import pdfkit


from django.shortcuts import render
from django.views import View
from .forms import ReporteInventarioForm
from .models import Inventario

class ReporteInventarioView(View):
    def get(self, request, *args, **kwargs):
        # Inicializar el formulario con los parámetros GET (si existen)
        form = ReporteInventarioForm(request.GET)
        
        # Obtener los productos filtrados basados en el formulario
        inventarios = Inventario.objects.all()
        if form.is_valid():
            fecha_inicio = form.cleaned_data.get('fecha_inicio')
            fecha_fin = form.cleaned_data.get('fecha_fin')
            bodega = form.cleaned_data.get('bodega')

            if fecha_inicio:
                inventarios = inventarios.filter(fecha__gte=fecha_inicio)
            if fecha_fin:
                inventarios = inventarios.filter(fecha__lte=fecha_fin)
            if bodega:
                inventarios = inventarios.filter(idbodega__nombre__icontains=bodega)

        # Renderizar la plantilla con el formulario y los inventarios
        context = {
            'form': form,
            'inventarios': inventarios
        }
        return render(request, 'inventario/reportes/createReport.html', context)


class ReporteInventarioPDF(View):
    def get(self, request, *args, **kwargs):
        # Inicializamos el formulario con los datos de la URL (GET)
        form = ReporteInventarioForm(request.GET)

        # Si el formulario es válido, obtenemos los datos de los filtros
        if form.is_valid():
            fecha_inicio = form.cleaned_data.get('fecha_inicio')
            fecha_fin = form.cleaned_data.get('fecha_fin')
            bodega = form.cleaned_data.get('bodega')

            # Filtrar el inventario según los parámetros
            inventarios = Inventario.objects.all()

            if fecha_inicio:
                inventarios = inventarios.filter(fecha__gte=fecha_inicio)
            if fecha_fin:
                inventarios = inventarios.filter(fecha__lte=fecha_fin)
            if bodega:
                inventarios = inventarios.filter(idbodega__nombre__icontains=bodega)

        else:
            # Si el formulario no es válido, mostramos todos los productos
            inventarios = Inventario.objects.all()

        # Crear el PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_inventario.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter

        # Título del reporte
        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, height - 50, "Reporte de Inventario")

        # Encabezados de tabla
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, height - 100, "Producto")
        p.drawString(250, height - 100, "Bodega")
        p.drawString(400, height - 100, "Stock")

        y = height - 120  # Posición inicial de las filas
        p.setFont("Helvetica", 10)

        # Recorrer los productos filtrados y añadirlos al PDF
        for item in inventarios:
            p.drawString(50, y, item.idproducto.descripcion)
            p.drawString(250, y, item.idbodega.nombre)
            p.drawString(400, y, str(item.stock))
            y -= 20  # Espaciado entre filas

            # Control de salto de página
            if y < 50:
                p.showPage()
                y = height - 50  

        p.showPage()
        p.save()

        return response
    














    
#Reporte de Productos

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors  # Asegúrate de importar la librería de colores
from django.http import HttpResponse

class ReporteProductoView(View):
    def get(self, request, *args, **kwargs):
        # Inicializar el formulario de filtros
        form = ReporteProductoForm(request.GET)

        # Filtrar productos si el formulario es válido
        if form.is_valid():
            nombre = form.cleaned_data.get('nombre')
            categoria = form.cleaned_data.get('categoria')
            fecha_inicio = form.cleaned_data.get('fecha_inicio')
            fecha_fin = form.cleaned_data.get('fecha_fin')
            precio_min = form.cleaned_data.get('precio_min')
            precio_max = form.cleaned_data.get('precio_max')

            productos = Producto.objects.all()
            if nombre:
                productos = productos.filter(descripcion__icontains=nombre)
            if categoria:
                productos = productos.filter(categoria__icontains=categoria)
            if fecha_inicio:
                productos = productos.filter(fecha_creacion__gte=fecha_inicio)
            if fecha_fin:
                productos = productos.filter(fecha_creacion__lte=fecha_fin)
            if precio_min:
                productos = productos.filter(precio_unitario__gte=precio_min)
            if precio_max:
                productos = productos.filter(precio_unitario__lte=precio_max)
        else:
            productos = Producto.objects.all()

        # Verificar si la solicitud es para generar el PDF
        if 'pdf' in request.GET:
            return self.generar_pdf(productos)

        # Renderizar la página con los productos filtrados y el formulario
        return render(request, 'inventario/reportes/productosReport.html', {'form': form, 'productos': productos})

    def generar_pdf(self, productos):
        # Crear la respuesta HTTP con el tipo de contenido para PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_productos.pdf"'

        # Crear el documento PDF usando SimpleDocTemplate
        doc = SimpleDocTemplate(response, pagesize=letter)

        # Crear estilo para el texto (para permitir ajuste de texto)
        styles = getSampleStyleSheet()
        style_normal = styles['Normal']
        style_normal.wordWrap = 'CJK'  # Permite el ajuste de texto

        # Datos de la tabla: encabezados y filas
        data = [
            ['Código', 'Descripción', 'Precio Unitario', 'Precio Cash', 'Proveedor', 'Marca']  # Encabezado
        ]

        # Agregar los productos como filas en la tabla
        for producto in productos:
            descripcion_paragraph = Paragraph(producto.descripcion, style_normal)  # Usar Paragraph para la descripción
            data.append([
                producto.codigo,
                descripcion_paragraph,  # Aquí agregamos el párrafo que manejará el ajuste de texto
                str(producto.precio_unitario),
                str(producto.precio_cash),
                str(producto.proveedor),
                str(producto.marca)
            ])

        # Crear la tabla con los datos
        table = Table(data, colWidths=[50, 150, 100, 100, 100, 100])  # Definir el ancho de cada columna

        # Establecer el estilo de la tabla (bordes, colores, alineación)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),  # Fondo negro para el encabezado
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Texto blanco en el encabezado
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alineación centrada para todo el contenido
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fuente negrita para el encabezado
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Relleno en el encabezado
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Fondo blanco para las filas
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Rejilla de bordes en la tabla
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Fuente normal para las filas
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),  # Alineación de texto a la izquierda para las filas
            ('TOPPADDING', (0, 0), (-1, -1), 6),  # Relleno en la parte superior de cada celda
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),  # Relleno en la parte inferior de cada celda
        ])

        # Aplicar el estilo a la tabla
        table.setStyle(style)

        # Construir el documento PDF con la tabla
        doc.build([table])

        return response
    
from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from .models import MovimientoProducto
from .forms import ReporteMovimientoFormulario
from django.template.loader import get_template
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from .models import MovimientoProducto
from .forms import ReporteMovimientoFormulario
from datetime import datetime

class ReporteMovimientoView(View):
    login_url = '/inventario/login'
    template_name = 'inventario/Reportes/reporteMovimiento.html'

    def get(self, request, *args, **kwargs):
        # Procesar formulario para filtrar datos
        form = ReporteMovimientoFormulario(request.GET)
        movimientos = MovimientoProducto.objects.all().order_by('-fecha_movimiento')

        # Obtener los filtros seleccionados
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')

        # Filtrar por fechas
        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            movimientos = movimientos.filter(fecha_movimiento__date__gte=fecha_inicio)

        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
            movimientos = movimientos.filter(fecha_movimiento__date__lte=fecha_fin)

        # Filtrar por empleado
        if form.is_valid():
            data = form.cleaned_data
            if data['empleado']:
                movimientos = movimientos.filter(empleado=data['empleado'])
            
            # Filtrar por tipo de movimiento
            if data['tipo_movimiento']:
                movimientos = movimientos.filter(tipo_movimiento=data['tipo_movimiento'])

        # Si el parámetro 'pdf' está en la URL, generamos el PDF
        if 'pdf' in request.GET:
            return self.generar_pdf(movimientos)

        # Si el parámetro 'excel' está en la URL, generamos el Excel
        if 'excel' in request.GET:
            return self.generar_excel(movimientos)

        context = {
            'form': form,
            'movimientos': movimientos
        }
        return render(request, self.template_name, context)

    def generar_pdf(self, movimientos):
        # Generar PDF con los movimientos de productos
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_movimientos.pdf"'

        # Crear documento PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Crear la tabla con los datos
        data = [
            ['Bodega', 'Producto', 'Tipo Movimiento', 'Cantidad', 'Empleado', 'Fecha']  # Encabezados
        ]

        for movimiento in movimientos:
            data.append([
                movimiento.bodega,
                movimiento.producto,
                movimiento.get_tipo_movimiento_display(),
                movimiento.cantidad,
                movimiento.empleado,
                movimiento.fecha_movimiento.strftime("%Y-%m-%d %H:%M:%S")
            ])

        # Crear tabla
        table = Table(data)

        # Establecer estilos de la tabla
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ])
        table.setStyle(style)

        # Build the document
        elements = [table]
        doc.build(elements)

        buffer.seek(0)
        response.write(buffer.getvalue())
        return response

    def generar_excel(self, movimientos):
        import openpyxl
        from django.http import HttpResponse

        # Crear archivo Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Reporte Movimientos'

        # Crear encabezados
        headers = ['Bodega', 'Producto', 'Tipo Movimiento', 'Cantidad', 'Empleado', 'Fecha']
        ws.append(headers)

        # Agregar los datos
        for movimiento in movimientos:
            ws.append([
                movimiento.bodega,
                movimiento.producto,
                movimiento.get_tipo_movimiento_display(),
                movimiento.cantidad,
                movimiento.empleado,
                movimiento.fecha_movimiento.strftime("%Y-%m-%d %H:%M:%S")
            ])

        # Crear la respuesta con el archivo Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="reporte_movimientos.xlsx"'

        wb.save(response)
        return response


from django.shortcuts import render
from .models import Producto
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

class BuscarProductoPorCodigo(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = "Inventario/listarProductos.html"
def buscar_producto(request):
    codigo = request.GET.get('codigo')
    if codigo:
        try:
            producto = Producto.objects.get(codigo=codigo)
            return JsonResponse({'id': producto.id, 'descripcion': producto.descripcion})
        except Producto.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado'})
    return JsonResponse({'error': 'Código no proporcionado'})



from django.http import JsonResponse
from .models import Producto
from django.views import View

class BuscarProductoPorId(View):

    def get(self, request):
        producto_id = request.GET.get('id')

        if producto_id:
            try:
                producto = Producto.objects.get(id=producto_id)
                return JsonResponse({
                    'id': producto.id,
                    'descripcion': producto.descripcion,
                    'codigo': producto.codigo
                })
            except Producto.DoesNotExist:
                return JsonResponse({'error': 'Producto no encontrado por ID'}, status=404)

        return JsonResponse({'error': 'ID no proporcionado'}, status=400)
from django.utils.numberformat import format as format_number
import calendar
from datetime import date

class ProductosMasVendidosPDF(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        # Vista para mostrar el formulario de selección de mes
        contexto = complementarContexto({}, request.user)
        return render(request, 'inventario/reportes/seleccionMes.html', contexto)

    def post(self, request):
        # Procesar la fecha seleccionada
        mes_seleccionado = request.POST.get('mes')
        año, mes = map(int, mes_seleccionado.split('-'))
        
        # Calcular rangos de fecha
        # Fecha de inicio
        fecha_inicio_naive = datetime(año, mes, 1)
        fecha_inicio = timezone.make_aware(fecha_inicio_naive)

        # Último día del mes
        ultimo_dia = calendar.monthrange(año, mes)[1]

        # Fecha de fin
        fecha_fin_naive = datetime(año, mes, ultimo_dia, 23, 59, 59)
        fecha_fin = timezone.make_aware(fecha_fin_naive)
        # Obtener datos
        productos = MovimientoProducto.objects.filter(
            tipo_movimiento='venta',
            estado_producto__nombre='Vendido',
            fecha_movimiento__range=[fecha_inicio, fecha_fin]
        ).values('producto__descripcion', 'producto__codigo').annotate(
            total_vendido=Sum('cantidad')
        ).order_by('-total_vendido')

        total_general = sum(item['total_vendido'] for item in productos)

        # Calcular la participación de cada producto y el ancho de la barra
        for producto in productos:
            participacion = (producto['total_vendido'] / total_general) * 100
            producto['participacion'] = participacion
            # Calcular el ancho de la barra (entero entre 0 y 100)
            producto['participacion_width'] = int(participacion)
            # Formatear la participación para mostrar solo dos decimales
            producto['participacion_display'] = format_number(participacion, decimal_sep='.', decimal_pos=2)

        # Calcular la participación del top 3 productos
        top_3_productos = productos[:3]
        participacion_top_3 = sum(producto['participacion'] for producto in top_3_productos)

        data = {
            'nombre_empresa': 'Comercial Hernandez',
            'direccion_empresa': 'Sonsonate, El Salvador',
            'productos': productos,
            'total_general': total_general,
            'mes': fecha_inicio.strftime("%B %Y"),
            'rango_fechas': f"{fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}",
            'fecha_reporte': date.today().strftime("%d/%m/%Y"),
            'usuario_generacion': request.user.get_full_name(),
            'participacion_top_3': participacion_top_3,
        }

        nombre_archivo = f"productos_mas_vendidos_{fecha_inicio.strftime('%Y_%m')}.pdf"

        pdf = render_to_pdf('inventario/Reportes/reporteProductosVendidos.html', data)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        return response
    

class GeneradorReportesPDF(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None
    
    reportes_config = {
        'ventas': {
            'nombre': 'Reporte de Ventas',
            'icono': 'fa-chart-line',
            'parametros': ['mes', 'bodega'],
            'template': 'inventario/Reportes/ventas.html',
            'handler': 'procesar_ventas'
        },
        'stock': {
            'nombre': 'Stock Actual',
            'icono': 'fa-boxes',
            'parametros': ['bodega', 'estado'],
            'template': 'inventario/Reportes/stock.html',
            'handler': 'procesar_stock'
        },
        'danados': {
            'nombre': 'Productos Dañados',
            'icono': 'fa-exclamation-triangle',
            'parametros': ['mes'],
            'template': 'inventario/Reportes/danados.html',
            'handler': 'procesar_danados'
        },
        'vendedor_mes': {
            'nombre': 'Vendedor del Mes',
            'icono': 'fa-trophy',
            'parametros': ['mes'],
            'template': 'inventario/Reportes/vendedor_mes.html',
            'handler': 'procesar_vendedor_mes'
        },
        'ganancias': {
            'nombre': 'Ganancias y Pérdidas',
            'icono': 'fa-coins',
            'parametros': ['mes'],
            'template': 'inventario/Reportes/ganancias.html',
            'handler': 'procesar_ganancias'
        },
        'entradas': {
        'nombre': 'Reporte de Entradas',
        'icono': 'fa-sign-in-alt',
        'parametros': ['mes', 'bodega'],
        'template': 'inventario/Reportes/entradas.html',
        'handler': 'procesar_entradas'
        },
        'salidas': {
            'nombre': 'Reporte de Salidas',
            'icono': 'fa-sign-out-alt',
            'parametros': ['mes', 'bodega'],
            'template': 'inventario/Reportes/salidas.html',
            'handler': 'procesar_salidas'
        }
    }

    def get(self, request, reporte_type='ventas'):
        config = self.reportes_config.get(reporte_type)
        contexto = self._preparar_contexto(request, config)
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/Reportes/base_generador.html', contexto)

    def post(self, request, reporte_type='ventas'):
        config = self.reportes_config.get(reporte_type)
        
        if config is None:
            return HttpResponse("Error: Tipo de reporte inválido", status=400)
        
        handler = getattr(self, config.get('handler', ''), None)

        if handler is None or not callable(handler):
            return HttpResponse("Error: Handler no encontrado para el reporte", status=500)
        
        return handler(request, config)
    
    def _preparar_contexto(self, request, config):
        return {
            'reportes_config': self.reportes_config,  # Agregar esta línea
            'reporte_type': config.get('nombre', ''),  # Para activar el elemento correcto
            'config': config,
            'bodegas': Bodega.objects.all(),
            'estados': EstadoProducto.objects.all(),
            'empleados': Empleado.objects.all()
        }

    # Handlers específicos para cada tipo de reporte
    def procesar_ventas(self, request, config):
        try:
            # Obtener parámetros
            params = {
                'mes': request.POST.get('mes'),
                'bodega_id': request.POST.get('bodega')
            }

            if not params['mes'] or not params['bodega_id']:
                raise ValueError("Parámetros incompletos")
            
            # Desglosar año y mes
            año, mes = map(int, params['mes'].split('-'))
            fecha_inicio = date(año, mes, 1)
            fecha_fin = date(año, mes, calendar.monthrange(año, mes)[1])
            
            # Obtener ventas
            ventas = MovimientoProducto.objects.filter(
                tipo_movimiento='venta',
                fecha_movimiento__range=[fecha_inicio, fecha_fin],
                bodega_id=params['bodega_id']
            ).annotate(
                total_vendido=Sum('cantidad')
            ).values('producto__descripcion', 'total_vendido')
            
            # Verificar si hay ventas
            if not ventas:
                return self._generar_pdf({
                    'mensaje': 'No hay datos de ventas para el periodo seleccionado.'
                }, config)
            
            # Calcular el total de ventas y la participación por producto
            total_ventas = sum(item['total_vendido'] for item in ventas)
            
            for venta in ventas:
                if total_ventas > 0:
                    venta['participacion'] = (venta['total_vendido'] / total_ventas) * 100
                else:
                    venta['participacion'] = 0

            # Obtener nombre de la bodega
            bodega = Bodega.objects.get(id=params['bodega_id']).nombre
            
            # Generar el reporte en PDF
            return self._generar_pdf({
                'data': ventas,
                'total_ventas': total_ventas,
                'rango_fechas': f"{fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}",
                'bodega': bodega
            }, config)

        except Exception as e:
            return self._generar_pdf({
                'mensaje': f"Error al generar el reporte: {str(e)}"
            }, config)

    def procesar_stock(self, request, config):
        bodega_id = request.POST.get('bodega')
        estado_id = EstadoProducto.objects.get(nombre= EstadoProducto.DISPONIBLE).id,
        
        stock = Inventario.objects.filter(
            idbodega_id=bodega_id,
            estado_id=estado_id
        ).annotate(
            valor_total=F('stock') * F('idproducto__precio_unitario')
        )
        
        return self._generar_pdf({
            'data': stock,
            'titulo': 'Stock Actual',
            'bodega': Bodega.objects.get(id=bodega_id).nombre
        }, config)

    def procesar_danados(self, request, config):
        mes = request.POST.get('mes')
        año, mes = map(int, mes.split('-'))
        
        danados = Devolucion.objects.filter(
            dañado=True,
            fecha_devolucion__year=año,
            fecha_devolucion__month=mes
        ).select_related('idproducto', 'idbodega')
        
        return self._generar_pdf({
            'data': danados,
            'titulo': 'Productos Dañados',
            'mes': f"{mes}/{año}"
        }, config)
    
    #Ganancias o perdidas en comparacion al mes anterior 
    def procesar_ganancias(self, request, config):
        mes = request.POST.get('mes')
        año, mes = map(int, mes.split('-'))
        
        fecha_inicio = datetime(año, mes, 1)
        fecha_fin = datetime(año, mes, calendar.monthrange(año, mes)[1], 23, 59, 59)
        
        # Obtener las ventas del mes actual
        ventas_mes_actual = MovimientoProducto.objects.filter(
            tipo_movimiento='venta',
            fecha_movimiento__range=[fecha_inicio, fecha_fin]
        ).aggregate(total=Sum('cantidad'))['total'] or 0
        
        # Obtener las ventas del mes anterior
        fecha_inicio_mes_anterior = fecha_inicio - timedelta(days=1)
        fecha_fin_mes_anterior = fecha_inicio - timedelta(days=1)
        
        ventas_mes_anterior = MovimientoProducto.objects.filter(
            tipo_movimiento='venta',
            fecha_movimiento__range=[fecha_inicio_mes_anterior, fecha_fin_mes_anterior]
        ).aggregate(total=Sum('cantidad'))['total'] or 0
        
        # Calcular la diferencia
        diferencia = ventas_mes_actual - ventas_mes_anterior
        
        return self._generar_pdf({
            'mes': fecha_inicio.strftime('%B %Y'),
            'ventas_mes_actual': ventas_mes_actual,
            'ventas_mes_anterior': ventas_mes_anterior,
            'diferencia': diferencia
        }, config)
    #procesar vendedor mes
    def procesar_vendedor_mes(self, request, config):
        try:
            mes = request.POST.get('mes')
            año, mes = map(int, mes.split('-'))
            
            # Crear las fechas con la zona horaria de Django
            fecha_inicio = timezone.make_aware(datetime(año, mes, 1), timezone.get_current_timezone())
            fecha_fin = timezone.make_aware(datetime(año, mes, calendar.monthrange(año, mes)[1], 23, 59, 59), timezone.get_current_timezone())
            
            # Obtener los vendedores con ventas en el rango de fechas
            vendedores = MovimientoProducto.objects.filter(
                tipo_movimiento='venta',
                fecha_movimiento__range=[fecha_inicio, fecha_fin]
            ).values('empleado__nombre', 'empleado__apellido').annotate(
                total_vendido=Sum('cantidad')
            ).order_by('-total_vendido')
            
            if vendedores.exists():
                # Calcular la participación de cada vendedor
                total_ventas = sum(v['total_vendido'] for v in vendedores)
                for vendedor in vendedores:
                    vendedor['participacion'] = (vendedor['total_vendido'] / total_ventas * 100) if total_ventas > 0 else 0
                
                return self._generar_pdf({
                    'mes': fecha_inicio.strftime('%B %Y'),
                    'vendedores': vendedores,
                    'total_ventas': total_ventas
                }, config)
            else:
                # Si no hay ventas, retornar un mensaje
                return self._generar_pdf({
                    'mes': fecha_inicio.strftime('%B %Y'),
                    'mensaje': 'No se encontraron ventas para este mes.'
                }, config)
        
        except Exception as e:
            return self._generar_pdf({
                'mensaje': f"Error al generar el reporte: {str(e)}"
            }, config)
    def procesar_entradas(self, request, config):
        try:
            params = {
                'mes': request.POST.get('mes'),
                'bodega_id': request.POST.get('bodega')
            }
            
            año, mes = map(int, params['mes'].split('-'))
            fecha_inicio = datetime(año, mes, 1)
            fecha_fin = datetime(año, mes, calendar.monthrange(año, mes)[1], 23, 59, 59)
            
            entradas = MovimientoProducto.objects.filter(
                tipo_movimiento__in=['entrada', 'recepcion', 'devolucion'],
                fecha_movimiento__range=[fecha_inicio, fecha_fin],
                bodega_id=params['bodega_id'],
                estado_producto__nombre='Disponible'
            ).select_related('producto', 'empleado')
            
            return self._generar_pdf({
                'data': entradas,
                'tipo': 'Entradas',
                'rango_fechas': f"{fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}",
                'bodega': Bodega.objects.get(id=params['bodega_id']).nombre
            }, config)
        
        except Exception as e:
            return self._generar_pdf({'mensaje': str(e)}, config)

    def procesar_salidas(self, request, config):
        try:
            params = {
                'mes': request.POST.get('mes'),
                'bodega_id': request.POST.get('bodega')
            }
            
            # Parsear año y mes
            año, mes = map(int, params['mes'].split('-'))
            fecha_inicio = datetime(año, mes, 1)
            fecha_fin = datetime(año, mes, calendar.monthrange(año, mes)[1], 23, 59, 59)

            # Filtrar los movimientos pendientes de productos disponibles
            movimientos_pendientes = MovimientoPendiente.objects.filter(
                fecha__range=[fecha_inicio, fecha_fin],
                bodega_id=params['bodega_id'],
                estado='Pendiente'  # Solo pendientes
            ).select_related('producto', 'empleado_recibio', 'empleado_entrego')  # Relacionar productos y empleados

            # Obtener los productos que ya han sido registrados en MovimientoProducto
            productos_en_movimiento = MovimientoProducto.objects.filter(
                tipo_movimiento__in=['salida', 'entrega', 'reparacion', 'dañado'],
                fecha_movimiento__range=[fecha_inicio, fecha_fin],
                bodega_id=params['bodega_id']
            ).values_list('producto', flat=True)

            # Filtrar solo los productos en pendiente que no estén en MovimientoProducto
            salidas = movimientos_pendientes.exclude(producto__in=productos_en_movimiento)

            # Generar reporte PDF
            return self._generar_pdf({
                'data': salidas,
                'tipo': 'Salidas',
                'rango_fechas': f"{fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}",
                'bodega': Bodega.objects.get(id=params['bodega_id']).nombre
            }, config)
        
        except Exception as e:
            return self._generar_pdf({'mensaje': str(e)}, config)



    def _generar_pdf(self, data, config):
        contexto = {
            **data,
            'usuario': self.request.user.get_full_name(),
            'fecha_generacion': date.today().strftime('%d/%m/%Y')
        }
        
        pdf = render_to_pdf(config['template'], contexto)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{config["nombre"]}.pdf"'
        return response