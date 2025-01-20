#renderiza las vistas al usuario
import datetime
from time import timezone
from urllib import request
from django.shortcuts import get_object_or_404, redirect, render
# para redirigir a otras paginas
from django.http import HttpResponseRedirect, HttpResponse,FileResponse
#el formulario de login
from .forms import *
# clase para crear vistas basadas en sub-clases
from django.views import View
from django.urls import reverse

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




#Panel de inicio y vista principal------------------------------------------------#
class Panel(LoginRequiredMixin, View):
    #De no estar logeado, el usuario sera redirigido a la pagina de Login
    #Las dos variables son la pagina a redirigir y el campo adicional, respectivamente
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        from datetime import date
        #Recupera los datos del usuario despues del login
        contexto = {'usuario': request.user.username,
                    'id_usuario':request.user.id,
                   'nombre': request.user.first_name,
                   'apellido': request.user.last_name,
                   'correo': request.user.email,
                   'fecha':  date.today(),
                   'productosRegistrados' : Producto.numeroRegistrados(),
                   #'productosVendidos' :  DetalleFactura.productosVendidos(),
                   'empleadosRegistrados' : Empleado.numeroRegistrados(),
                   'usuariosRegistrados' : Usuario.numeroRegistrados(),
                   #'facturasEmitidas' : Factura.numeroRegistrados(),
                   #'ingresoTotal' : Factura.ingresoTotal(),
                   #'ultimasVentas': DetalleFactura.ultimasVentas(),
                   'administradores': Usuario.numeroUsuarios('administrador'),
                   'usuarios': Usuario.numeroUsuarios('usuario')

        }


        return render(request, 'inventario/panel.html',contexto)
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


#Muestra el perfil del usuario logeado actualmente---------------------------------#
class Perfil(LoginRequiredMixin, View):
    login_url = 'inventario/login'
    redirect_field_name = None

    #se accede al modo adecuado y se valida al usuario actual para ver si puede modificar al otro usuario-
    #-el cual es obtenido por la variable 'p'
    def get(self, request, modo, p):
        if modo == 'editar':
            perf = Usuario.objects.get(id=pk)
            editandoSuperAdmin = False

            if p == 1:
                if request.user.nivel != 2:
                    messages.error(request, 'No puede editar el perfil del administrador por no tener los permisos suficientes')
                    return HttpResponseRedirect('/inventario/perfil/ver/%s' % p)
                editandoSuperAdmin = True
            else:
                if request.user.is_superuser != True: 
                    messages.error(request, 'No puede cambiar el perfil por no tener los permisos suficientes')
                    return HttpResponseRedirect('/inventario/perfil/ver/%s' % p) 

                else:
                    if perf.is_superuser == True:
                        if request.user.nivel == 2:
                            pass

                        elif perf.id != request.user.id:
                            messages.error(request, 'No puedes cambiar el perfil de un usuario de tu mismo nivel')

                            return HttpResponseRedirect('/inventario/perfil/ver/%s' % p) 

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
            if p == 1:
                if request.user.nivel != 2:
                   
                    messages.error(request, 'No puede cambiar la clave del administrador por no tener los permisos suficientes')
                    return HttpResponseRedirect('/inventario/perfil/ver/%s' % p)  
            else:
                if request.user.is_superuser != True: 
                    messages.error(request, 'No puede cambiar la clave de este perfil por no tener los permisos suficientes')
                    return HttpResponseRedirect('/inventario/perfil/ver/%s' % p) 

                else:
                    if perf.is_superuser == True:
                        if request.user.nivel == 2:
                            pass

                        elif perf.id != request.user.id:
                            messages.error(request, 'No puedes cambiar la clave de un usuario de tu mismo nivel')
                            return HttpResponseRedirect('/inventario/perfil/ver/%s' % p) 


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



    def post(self,request,modo,p):
        if modo ==  'editar':
            # Crea una instancia del formulario y la llena con los datos:
            form = UsuarioFormulario(request.POST)
            # Revisa si es valido:
            
            if form.is_valid():
                perf = Usuario.objects.get(id=pk)
                # Procesa y asigna los datos con form.cleaned_data como se requiere
                if p != 1:
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
                messages.success(request, 'Actualizado exitosamente el perfil de ID %s.' % p)
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
                    return HttpResponseRedirect("/inventario/perfil/clave/%s" % p)
    



  
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
            precio = form.cleaned_data['precio']
            categoria = form.cleaned_data['categoria']
            tiene_iva = form.cleaned_data['tiene_iva']

            prod = Producto.objects.get(id=pk)
            prod.descripcion = descripcion
            prod.precio = precio
            prod.categoria = categoria
            prod.tiene_iva = tiene_iva
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
        contexto = complementarContexto(contexto,request.user)         
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


# #Emite la primera parte de la factura------------------------------#
# class EmitirFactura(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self, request):
#         # Crea una instancia del formulario y la llena con los datos:
#         duis = Empleado.duisRegistradas()
#         form = EmitirFacturaFormulario(request.POST,duis=duis)
#         # Revisa si es valido:
#         if form.is_valid():
#             # Procesa y asigna los datos con form.cleaned_data como se requiere
#             request.session['form_details'] = form.cleaned_data['productos']
#             request.session['id_client'] = form.cleaned_data['empleado']
#             return HttpResponseRedirect("detallesDeFactura")
#         else:
#             #De lo contrario lanzara el mismo formulario
#             return render(request, 'inventario/factura/emitirFactura.html', {'form': form})

#     def get(self, request):
#         duis = Empleado.duisRegistradas()   
#         form = EmitirFacturaFormulario(duis=duis)
#         contexto = {'form':form}
#         contexto = complementarContexto(contexto,request.user) 
#         return render(request, 'inventario/factura/emitirFactura.html', contexto)
# #Fin de vista---------------------------------------------------------------------------------#



# #Muestra y procesa los detalles de cada producto de la factura--------------------------------#
# class DetallesFactura(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def get(self, request):
#         dui = request.session.get('id_client')
#         productos = request.session.get('form_details')
#         FacturaFormulario = formset_factory(DetallesFacturaFormulario, extra=productos)
#         formset = FacturaFormulario()
#         contexto = {'formset':formset}
#         contexto = complementarContexto(contexto,request.user) 

#         return render(request, 'inventario/factura/detallesFactura.html', contexto)        

#     def post(self, request):
#         dui = request.session.get('id_client')
#         productos = request.session.get('form_details')

#         FacturaFormulario = formset_factory(DetallesFacturaFormulario, extra=productos)

#         inicial = {
#         'descripcion':'',
#         'cantidad': 0,
#         'subtotal':0,
#         }

#         data = {
#     'form-TOTAL_FORMS': productos,
#     'form-INITIAL_FORMS':0,
#     'form-MAX_NUM_FORMS': '',
#                 }

#         formset = FacturaFormulario(request.POST,data)


#         if formset.is_valid():

#             id_producto = []
#             cantidad = []
#             subtotal = []
#             total_general = []
#             sub_monto = 0
#             monto_general = 0

#             for form in formset:
#                 desc = form.cleaned_data['descripcion'].descripcion
#                 cant = form.cleaned_data['cantidad']
#                 sub = form.cleaned_data['valor_subtotal']
#                 id_producto.append(obtenerIdProducto(desc)) #esta funcion, a estas alturas, es innecesaria porque ya tienes la id
#                 cantidad.append(cant)
#                 subtotal.append(sub)

#             #Ingresa la factura
#             #--Saca el sub-monto
#             for index in subtotal:
#                 sub_monto += index

#             #--Saca el monto general
#             for index,element in enumerate(subtotal):
#                 if productoTieneIva(id_producto[index]):
#                     nuevoPrecio = sacarIva(element)   
#                     monto_general += nuevoPrecio
#                     total_general.append(nuevoPrecio)                     
#                 else:                   
#                     monto_general += element
#                     total_general.append(element)        

#             from datetime import date

#             empleado = Empleado.objects.get(dui=dui)
#             iva = ivaActual('objeto')
#             factura = Factura(empleado=empleado,fecha=date.today(),sub_monto=sub_monto,monto_general=monto_general,iva=iva)

#             factura.save()
#             id_factura = factura

#             for indice,elemento in enumerate(id_producto):
#                 objetoProducto = obtenerProducto(elemento)
#                 cantidadDetalle = cantidad[indice]
#                 subDetalle = subtotal[indice]
#                 totalDetalle = total_general[indice]

#                 detalleFactura = DetalleFactura(id_factura=id_factura,id_producto=objetoProducto,cantidad=cantidadDetalle
#                     ,sub_total=subDetalle,total=totalDetalle)

#                 objetoProducto.disponible -= cantidadDetalle
#                 objetoProducto.save()

#                 detalleFactura.save()  

#             messages.success(request, 'Factura de ID %s insertada exitosamente.' % id_factura.id)
#             return HttpResponseRedirect("/inventario/emitirFactura")    
    
# #Fin de vista-----------------------------------------------------------------------------------#


# #Muestra y procesa los detalles de cada producto de la factura--------------------------------#
# class ListarFacturas(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def get(self, request):
#         #Lista de productos de la BDD
#         facturas = Factura.objects.all()
#         #Crea el paginador
                               
#         contexto = {'tabla': facturas}
#         contexto = complementarContexto(contexto,request.user) 

#         return render(request, 'inventario/factura/listarFacturas.html', contexto)        

# #Fin de vista---------------------------------------------------------------------------------------#     


# #Muestra los detalles individuales de una factura------------------------------------------------#
# class VerFactura(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def get(self, request, p):
#         factura = Factura.objects.get(id=pk)
#         detalles = DetalleFactura.objects.filter(id_factura_id=pk)
#         contexto = {'factura':factura, 'detalles':detalles}
#         contexto = complementarContexto(contexto,request.user)     
#         return render(request, 'inventario/factura/verFactura.html', contexto)
# #Fin de vista--------------------------------------------------------------------------------------#   


# #Genera la factura en CSV--------------------------------------------------------------------------#
# class GenerarFactura(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def get(self, request, p):
#         import csv

#         factura = Factura.objects.get(id=pk)
#         detalles = DetalleFactura.objects.filter(id_factura_id=pk) 

#         nombre_factura = "factura_%s.csv" % (factura.id)

#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="%s"' % nombre_factura
#         writer = csv.writer(response)

#         writer.writerow(['Producto', 'Cantidad', 'Sub-total', 'Total',
#          'Porcentaje IVA utilizado: %s' % (factura.iva.valor_iva)])

#         for producto in detalles:            
#             writer.writerow([producto.id_producto.descripcion,producto.cantidad,producto.sub_total,producto.total])

#         writer.writerow(['Total general:','','', factura.monto_general])

#         return response

#         #Fin de vista--------------------------------------------------------------------------------------#


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




# #Formulario simple que crea un archivo y respalda los proveedores-----------------------#
# class ExportarProveedores(LoginRequiredMixin, View):
#     login_url = '/inventario/login'
#     redirect_field_name = None

#     def post(self,request):
#         form = ExportarEmpleadosFormulario(request.POST)
#         if form.is_valid():
#             request.session['empleadosExportados'] = True


#             #Se obtienen las entradas de producto en formato JSON
#             data = serializers.serialize("json", Empleado.objects.all())
#             fs = FileSystemStorage('inventario/tmp/')

#             #Se utiliza la variable fs para acceder a la carpeta con mas facilidad
#             with fs.open("empleados.json", "w") as out:
#                 out.write(data)
#                 out.close()  

#             with fs.open("empleados.json", "r") as out:                 
#                 response = HttpResponse(out.read(), content_type="application/force-download")
#                 response['Content-Disposition'] = 'attachment; filename="empleados.json"'
#                 out.close() 
#             #------------------------------------------------------------
#             return response

#     def get(self,request):
#         form = ExportarEmpleadosFormulario()

#         if request.session.get('empleadosExportados') == True:
#             exportado = request.session.get('empleadosExportados')
#             contexto = { 'form':form,'empleadosExportados': exportado  }
#             request.session['empleadosExportados'] = False

#         else:
#             contexto = {'form':form}
#             contexto = complementarContexto(contexto,request.user) 
#         return render(request, 'inventario/exportarEmpleados.html',contexto)
# #Fin de vista-------------------------------------------------------------------------#




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


#Agrega un compra-----------------------------------------------------------------------------------#      
class AgregarCompra(View):
    def get(self, request):
        compra_form = CompraFormulario()
        CompraItemFormSet = modelformset_factory(CompraItem, form=CompraItemFormulario, extra=1)
        formset = CompraItemFormSet(queryset=CompraItem.objects.none())
        return render(request, 'inventario/compra/agregarCompra.html', {'compra_form': compra_form, 'formset': formset})

    def post(self, request):
        compra_form = CompraFormulario(request.POST)
        CompraItemFormSet = modelformset_factory(CompraItem, form=CompraItemFormulario, extra=1)
        formset = CompraItemFormSet(request.POST)
        
        if compra_form.is_valid() and formset.is_valid():
            compra = compra_form.save()
            for form in formset:
                compra_item = form.save(commit=False)
                compra_item.compra = compra
                compra_item.save()
            compra.procesar_compra()  # Procesar la compra para actualizar el inventario y el estado del producto
            messages.success(request, 'Compra agregada exitosamente.')
            return redirect('listar_compras')  # Redirige a la vista de listar compras
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
        
        return render(request, 'inventario/compra/agregarCompra.html', {'compra_form': compra_form, 'formset': formset})

#Lista todos los compras---------------------------------------------------------------------------# 
class ListarCompras(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        #Lista de productos de la BDD
        compras = Compra.objects.all()
        #Crea el paginador
                               
        contexto = {'tabla': compras}
        contexto = complementarContexto(contexto,request.user) 

        return render(request, 'inventario/compra/listarCompras.html', contexto)
#------------------------------------------------------------------------------------------------#

#Genera el compra en CSV--------------------------------------------------------------------------
class GenerarCompra(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, p):
        import csv

        compra = Compra.objects.get(id=pk)
        detalles = DetalleCompra.objects.filter(id_compra_id=pk) 

        nombre_compra = "compra_%s.csv" % (compra.id)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % nombre_compra
        writer = csv.writer(response)

        writer.writerow(['Producto', 'Cantidad', 'Sub-total', 'Total'])

        for producto in detalles:            
            writer.writerow([producto.id_producto.descripcion,producto.cantidad,producto.sub_total,producto.total])

        writer.writerow(['Total general:','', compra.monto_general])

        return response

        #Fin de vista--------------------------------------------------------------------------------------#



#Genera el compra en PDF--------------------------------------------------------------------------#
class GenerarCompraPDF(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, p):

        compra = Compra.objects.get(id=pk)
        general = Opciones.objects.get(id=1)
        detalles = DetalleCompra.objects.filter(id_compra_id=pk)


        data = {
             'fecha': compra.fecha, 
             'monto_general': compra.monto_general,
            'nombre_proveedor': compra.proveedor.nombre + " " + compra.proveedor.apellido,
            'dui_proveedor': compra.proveedor.dui,
            'id_reporte': compra.id,
            'detalles': detalles,
            'modo' : 'compra',
            'general': general
        }

        nombre_compra = "compra_%s.pdf" % (compra.id)

        pdf = render_to_pdf('inventario/PDF/prueba.html', data)
        response = HttpResponse(pdf,content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % nombre_compra

        return response 
        #Fin de vista--------------------------------------------------------------------------------------#


#Crea un nuevo usuario--------------------------------------------------------------#
class CrearUsuario(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None    

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
class MovimientoProducto(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        return render(request, 'inventario/movimientoProducto.html')
#listar movimientoProducto
class ListarMovimientoProducto(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        movimientoProductos = MovimientoProducto.objects.all()
        contexto = {'tabla': movimientoProductos}
        contexto = complementarContexto(contexto,request.user) 
        return render(request, 'inventario/movimientoProducto/listarMovimientoProducto.html', contexto)

#Reparacion
class Reparacion(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        return render(request, 'inventario/reparacion.html')
#listar Rep
class ListarRep(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        reparaciones = Reparacion.objects.all()
        contexto = {'tabla': reparaciones}
        contexto = complementarContexto(contexto,request.user) 
        return render(request, 'inventario/reparacion/listarRep.html', contexto)
#Agregar Rep
class AgregarRep(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        form = ReparacionFormulario(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            descripcion = form.cleaned_data['descripcion']
            rep = Reparacion(nombre=nombre,descripcion=descripcion)
            rep.save()
            form = ReparacionFormulario()
            messages.success(request, 'Ingresado exitosamente bajo la ID %s.' % rep.id)
            request.session['repProcesado'] = 'agregado'
            return HttpResponseRedirect("/inventario/agregarRep")
        else:
            return render(request, 'inventario/reparacion/agregarRep.html', {'form': form})        

    def get(self,request):
        form = ReparacionFormulario()
        contexto = {'form':form , 'modo':request.session.get('repProcesado')} 
        contexto = complementarContexto(contexto,request.user)         
        return render(request, 'inventario/reparacion/agregarRep.html', contexto)

#editar Rep
class EditarRep(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request,pk):
        rep = Reparacion.objects.get(id=pk)
        form = ReparacionFormulario(request.POST, instance=rep)
        if form.is_valid():           
            nombre = form.cleaned_data['nombre']
            descripcion = form.cleaned_data['descripcion']
            rep.nombre = nombre
            rep.descripcion = descripcion
            rep.save()
            form = ReparacionFormulario(instance=rep)
            messages.success(request, 'Actualizado exitosamente la reparacion de ID %s.' % p)
            request.session['repProcesado'] = 'editado'            
            return HttpResponseRedirect("/inventario/editarRep/%s" % rep.id)
        else:
            return render(request, 'inventario/reparacion/agregarRep.html', {'form': form})
    def get(self, request,pk): 
        rep = Reparacion.objects.get(id=pk)
        form = ReparacionFormulario(instance=rep)
        contexto = {'form':form , 'modo':request.session.get('repProcesado'),'editar':True} 
        contexto = complementarContexto(contexto,request.user)     
        return render(request, 'inventario/reparacion/agregarRep.html', contexto)
    
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
            if form.cleaned_data['estado']:
                inventarios = inventarios.filter(estado__nombre=form.cleaned_data['estado'])

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
            registro = form.save(commit=False)
            inventario, _ = Inventario.objects.get_or_create(
                idbodega=registro.bodega,
                idproducto=registro.producto,
                defaults={'stock': 0, 'estado': EstadoProducto.objects.get(nombre='Disponible')}
            )
            inventario.aumentar_stock(registro.cantidad)
            inventario.save()
            registro.estado = EstadoProducto.objects.get(nombre='Disponible')
            registro.ajustar_stock(registro.cantidad)
            messages.success(request, 'Registro de inventario agregado exitosamente y stock actualizado.')
            return HttpResponseRedirect("/inventario/agregarInventario")
        else:
            return render(request, 'inventario/inventario/agregarInventario.html', {'form': form})

    def get(self, request):
        form = RegistroInventarioFormulario()
        contexto = {'form': form}
        return render(request, 'inventario/inventario/agregarInventario.html', contexto)
    

# VIEWS MAS PERRONAS AQUI XD# MovimientoProducto
class ListarMovimientoProducto(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        form = MovimientoProductoFormulario(request.GET)
        movimientos = MovimientoProducto.objects.all()

        if form.is_valid():
            if form.cleaned_data['bodega']:
                movimientos = movimientos.filter(bodega=form.cleaned_data['bodega'])
            if form.cleaned_data['producto']:
                movimientos = movimientos.filter(producto=form.cleaned_data['producto'])
            if form.cleaned_data['tipo_movimiento']:
                movimientos = movimientos.filter(tipo_movimiento=form.cleaned_data['tipo_movimiento'])

        contexto = {'tabla': movimientos, 'form': form}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/movimientoProducto/listarMovimientoProducto.html', contexto)

class AgregarEntrega(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        form = EntregaFormulario(request.POST)
        if form.is_valid():
            idbodega = form.cleaned_data['idbodega']
            idproducto = form.cleaned_data['idproducto']
            cantidad = form.cleaned_data['cantidad']
            id_empleado_recibio = form.cleaned_data['id_empleado_recibio']
            
            try:
                inventario = Inventario.objects.get(idbodega=idbodega, idproducto=idproducto)

                if inventario.stock < cantidad:
                    messages.error(request, 'No hay suficiente stock para realizar la entrega.')
                    return render(request, 'inventario/entrega/agregarEntrega.html', {'form': form})

                entrega = form.save(commit=False)
                entrega.id_empleado_autorizo = request.user  # Usuario autenticado
                entrega.save()

                inventario.reducir_stock(cantidad)
                inventario.save()

                messages.success(request, 'Entrega registrada y stock actualizado exitosamente.')
                request.session['entregaProcesada'] = 'registrada'
                return HttpResponseRedirect("/inventario/agregarEntrega")

            except Inventario.DoesNotExist:
                messages.error(request, 'El producto no está disponible en la bodega seleccionada.')
                return render(request, 'inventario/entrega/agregarEntrega.html', {'form': form})

        else:
            return render(request, 'inventario/entrega/agregarEntrega.html', {'form': form})


    def get(self, request):
        form = EntregaFormulario()
        contexto = {'form': form, 'modo': request.session.get('entregaProcesada')}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/entrega/agregarEntrega.html', contexto)

class AgregarRecepcion(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        form = RecepcionFormulario(request.POST)
        if form.is_valid():
            recepcion = form.save(commit=False)
            
            # Asignar automáticamente el usuario autenticado como el que realiza la recepción
            recepcion.id_empleado_autorizo = request.user

            # Guardar la recepción y actualizar el inventario
            recepcion.save()
            inventario = Inventario.objects.get(idbodega=recepcion.idbodega, idproducto=recepcion.idproducto)
            inventario.aumentar_stock(recepcion.cantidad)
            inventario.save()

            messages.success(request, 'Recepción registrada y stock actualizado exitosamente.')
            return HttpResponseRedirect("/inventario/agregarRecepcion")
        else:
            return render(request, 'inventario/recepcion/agregarRecepcion.html', {'form': form})

    def get(self, request):
        form = RecepcionFormulario()
        contexto = {'form': form}
        return render(request, 'inventario/recepcion/agregarRecepcion.html', contexto)