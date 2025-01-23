from django import forms
from .models import Bodega, Entrega, Estado, EstadoProducto, Inventario, Marca, MovimientoProducto, Producto, Empleado, Proveedor, RegistroInventario, Reparacion, Usuario

from django.forms import ModelChoiceField

class MisProductos(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.descripcion

class MisPrecios(ModelChoiceField):
    def label_from_instance(self,obj):
        return "%s" % obj.precio

class MisDisponibles(ModelChoiceField):
    def label_from_instance(self,obj):
        return "%s" % obj.disponible


class LoginFormulario(forms.Form):
    username = forms.CharField(label="Tu nombre de usuario",widget=forms.TextInput(attrs={'placeholder': 'Tu nombre de usuario',
        'class': 'form-control underlined', 'type':'text','id':'user'}))

    password = forms.CharField(label="Contraseña",widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña',
        'class': 'form-control underlined', 'type':'password','id':'password'}))

class ProductoFormulario(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['descripcion', 'precio_unitario', 'precio_cash', 'proveedor', 'marca']
        labels = {
            #'codigo': 'Código',
            'descripcion': 'Descripción',
            'precio_unitario': 'Precio Unitario',
            'precio_cash': 'Precio Cash',
            'proveedor': 'Proveedor',
            'marca': 'Marca'
        }
        widgets = {
            #'codigo': forms.TextInput(attrs={'placeholder': 'Código del producto', 'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'placeholder': 'Descripción del producto', 'class': 'form-control'}),
            'precio_unitario': forms.NumberInput(attrs={'placeholder': 'Precio Unitario', 'class': 'form-control'}),
            'precio_cash': forms.NumberInput(attrs={'placeholder': 'Precio Cash', 'class': 'form-control'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'marca': forms.Select(attrs={'class': 'form-control'})
        }


class ImportarProductosFormulario(forms.Form):
    importar = forms.FileField(
        max_length = 100000000000,
        label = 'Escoger archivo',
        widget = forms.ClearableFileInput(
        attrs={'id':'importar','class':'form-control'}),
        )

class ImportarEmpleadosFormulario(forms.Form):
    importar = forms.FileField(
        max_length = 100000000000,
        label = 'Escoger archivo',
        widget = forms.ClearableFileInput(
        attrs={'id':'importar','class':'form-control'}),
        )   

class ExportarProductosFormulario(forms.Form):
    desde = forms.DateField(
        label = 'Desde',
        widget = forms.DateInput(format=('%d-%m-%Y'),
        attrs={'id':'desde','class':'form-control','type':'date'}),
        )   

    hasta = forms.DateField(
        label = 'Hasta',
        widget = forms.DateInput(format=('%d-%m-%Y'),
        attrs={'id':'hasta','class':'form-control','type':'date'}),
        )   

class ExportarEmpleadoFormulario(forms.Form):
    desde = forms.DateField(
        label = 'Desde',
        widget = forms.DateInput(format=('%d-%m-%Y'),
        attrs={'id':'desde','class':'form-control','type':'date'}),
        )   

    hasta = forms.DateField(
        label = 'Hasta',
        widget = forms.DateInput(format=('%d-%m-%Y'),
        attrs={'id':'hasta','class':'form-control','type':'date'}),
        )   


class EmpleadoFormulario(forms.ModelForm):
    tipoC =  [ ('1','DUI'),('2','NIT') ]

    tipoDui = forms.CharField(
        label="Tipo de DUI",
        max_length=2,
        widget=forms.Select(choices=tipoC,attrs={'placeholder': 'Tipo de DUI',
        'id':'tipoDui','class':'form-control'}
        )
        )


    class Meta:
        model = Empleado
        fields = ['tipoDui','dui','nombre','apellido','nacimiento','telefono','correo']
        labels = {
        'DUI': 'Dui del empleado',
        'nombre': 'Nombre del empleado',
        'apellido': 'Apellido del empleado',
        'nacimiento': 'Fecha de nacimiento del empleado',
        'telefono': 'Numero telefonico del empleado',
        'correo': 'Correo electronico del empleado'
        }
        widgets = {
        'DUI': forms.TextInput(attrs={'placeholder': 'Inserte DUI de identidad del empleado',
        'id':'dui','class':'form-control'} ),
        'nombre': forms.TextInput(attrs={'placeholder': 'Inserte el primer o primeros nombres del empleado',
        'id':'nombre','class':'form-control'}),
        'apellido': forms.TextInput(attrs={'class':'form-control','id':'apellido','placeholder':'El apellido del empleado'}),
        'nacimiento':forms.DateInput(format=('%d-%m-%Y'),attrs={'id':'hasta','class':'form-control','type':'date'} ),
        'telefono':forms.TextInput(attrs={'id':'telefono','class':'form-control',
        'placeholder':'El telefono del empleado'} ),
        'correo':forms.TextInput(attrs={'placeholder': 'Correo del empleado',
        'id':'correo','class':'form-control'} )
        }


class EmitirFacturaFormulario(forms.Form):
    def _init_(self, *args, **kwargs):
       elecciones = kwargs.pop('duis')
       super(EmitirFacturaFormulario, self)._init_(*args, **kwargs)

       if(elecciones):
            self.fields["empleado"] = forms.CharField(label="empleado a facturar",max_length=50,
            widget=forms.Select(choices=elecciones,
            attrs={'placeholder': 'el dui del empleado a facturar',
            'id':'empleado','class':'form-control'}))
    
    productos = forms.IntegerField(label="Numero de productos",widget=forms.NumberInput(attrs={'placeholder': 'Numero de productos a facturar',
        'id':'productos','class':'form-control'}))

class DetallesFacturaFormulario(forms.Form):
    productos = Producto.productosRegistrados()

    descripcion = MisProductos(queryset=productos,widget=forms.Select(attrs={'placeholder': 'El producto a debitar','class':'form-control select-group','onchange':'establecerOperaciones(this)'}))

    vista_precio = MisPrecios(required=False,queryset=productos,label="Precio del producto",widget=forms.Select(attrs={'placeholder': 'El precio del producto','class':'form-control','disabled':'true'}))

    cantidad = forms.IntegerField(label="Cantidad a facturar",min_value=0,widget=forms.NumberInput(attrs={'placeholder': 'Introduzca la cantidad del producto','class':'form-control','value':'0','onchange':'calculoPrecio(this);calculoDisponible(this)', 'max':'0'}))

    cantidad_disponibles = forms.IntegerField(required=False,label="Stock disponible",min_value=0,widget=forms.NumberInput(attrs={'placeholder': 'Introduzca la cantidad del producto','class':'form-control','value':'0', 'max':'0', 'disabled':'true'}))

    selec_disponibles = MisDisponibles(queryset=productos,required=False,widget=forms.Select(attrs={'placeholder': 'El producto a debitar','class':'form-control','disabled':'true','hidden':'true'}))

    subtotal = forms.DecimalField(required=False,label="Sub-total",min_value=0,widget=forms.NumberInput(attrs={'placeholder': 'Monto sub-total','class':'form-control','disabled':'true','value':'0'}))

    valor_subtotal = forms.DecimalField(min_value=0,widget=forms.NumberInput(attrs={'placeholder': 'Monto sub-total','class':'form-control','hidden':'true','value':'0'}))      

class EmitirFacturaFormulario(forms.Form):
    def __init__(self, *args, **kwargs):
        elecciones = kwargs.pop('duis')
        super(EmitirFacturaFormulario, self).__init__(*args, **kwargs)

        if elecciones:
            self.fields["empleado"] = forms.CharField(label="Empleado a facturar", max_length=50, widget=forms.Select(choices=elecciones, attrs={'placeholder': 'El DUI del empleado a facturar', 'id': 'empleado', 'class': 'form-control'}))

    productos = forms.IntegerField(label="Número de productos", widget=forms.NumberInput(attrs={'placeholder': 'Número de productos a facturar', 'id': 'productos', 'class': 'form-control'}))

class DetallesFacturaFormulario(forms.Form):
    productos = Producto.productosRegistrados()

    descripcion = MisProductos(queryset=productos, widget=forms.Select(attrs={'placeholder': 'El producto a debitar', 'class': 'form-control select-group', 'onchange': 'establecerOperaciones(this)'}))
    vista_precio = MisPrecios(required=False, queryset=productos, label="Precio del producto", widget=forms.Select(attrs={'placeholder': 'El precio del producto', 'class': 'form-control', 'disabled': 'true'}))
    cantidad = forms.IntegerField(label="Cantidad a facturar", min_value=0, widget=forms.NumberInput(attrs={'placeholder': 'Introduzca la cantidad del producto', 'class': 'form-control', 'value': '0', 'onchange': 'calculoPrecio(this);calculoDisponible(this)', 'max': '0'}))
    cantidad_disponibles = forms.IntegerField(required=False, label="Stock disponible", min_value=0, widget=forms.NumberInput(attrs={'placeholder': 'Introduzca la cantidad del producto', 'class': 'form-control', 'value': '0', 'max': '0', 'disabled': 'true'}))
    selec_disponibles = MisDisponibles(queryset=productos, required=False, widget=forms.Select(attrs={'placeholder': 'El producto a debitar', 'class': 'form-control', 'disabled': 'true', 'hidden': 'true'}))
    subtotal = forms.DecimalField(required=False, label="Sub-total", min_value=0, widget=forms.NumberInput(attrs={'placeholder': 'Monto sub-total', 'class': 'form-control', 'disabled': 'true', 'value': '0'}))
    valor_subtotal = forms.DecimalField(min_value=0, widget=forms.NumberInput(attrs={'placeholder': 'Monto sub-total', 'class': 'form-control', 'hidden': 'true', 'value': '0'}))

class ProveedorFormulario(forms.ModelForm):
    tipoC =  [ ('1','DUI'),('2','NIT') ]

    tipoDui = forms.CharField(
        label="Tipo de dui",
        max_length=2,
        widget=forms.Select(choices=tipoC,attrs={'placeholder': 'Tipo de dui',
        'id':'tipoDui','class':'form-control'}
        )
        )

    class Meta:
        model = Proveedor
        fields = ['tipoDui','dui','nombre','apellido','direccion','telefono','correo']
        labels = {
        'dui': 'DUI del proveedor',
        'nombre': 'Nombre del proveedor',
        'apellido': 'Apellido del proveedor',
        'direccion': 'Direccion del proveedor',
        'telefono': 'Numero telefonico del proveedor',
        'correo': 'Correo electronico del proveedor'
        }
        widgets = {
        'dui': forms.TextInput(attrs={'placeholder': 'Inserte la dui de identidad del proveedor',
        'id':'dui','class':'form-control'} ),
        'nombre': forms.TextInput(attrs={'placeholder': 'Inserte el primer o primeros nombres del proveedor',
        'id':'nombre','class':'form-control'}),
        'apellido': forms.TextInput(attrs={'class':'form-control','id':'apellido','placeholder':'El apellido del proveedor'}),
        'direccion': forms.TextInput(attrs={'class':'form-control','id':'direccion','placeholder':'Direccion del proveedor'}), 
        'telefono':forms.TextInput(attrs={'id':'telefono','class':'form-control',
        'placeholder':'El telefono del proveedor'} ),
        'correo':forms.TextInput(attrs={'placeholder': 'Correo del proveedor',
        'id':'correo','class':'form-control'} )
        } 


class UsuarioFormulario(forms.Form):
    niveles =  [ ('1','Administrador'),('0','Usuario'),('2','Empleado') ]

    username = forms.CharField(
        label = "Nombre de usuario",
        max_length=50,
        widget = forms.TextInput(attrs={'placeholder': 'Inserte un nombre de usuario',
        'id':'username','class':'form-control','value':''} ),
        )

    first_name = forms.CharField(
        label = 'Nombre',
        max_length =100,
        widget = forms.TextInput(attrs={'placeholder': 'Inserte un nombre',
        'id':'first_name','class':'form-control','value':''}),            
        )

    last_name = forms.CharField(
        label = 'Apellido',
        max_length = 100,
        widget = forms.TextInput(attrs={'class':'form-control','id':'last_name','placeholder':'Inserte un apellido','value':''}), 
        )

    email = forms.CharField(
        label = 'Correo electronico',
        max_length=100,
        widget = forms.TextInput(attrs={'placeholder': 'Inserte un correo valido',
        'id':'email','class':'form-control','type':'email','value':''} )
        )

    level =  forms.CharField(
        required=False,
        label="Nivel de acceso",
        max_length=2,
        widget=forms.Select(choices=niveles,attrs={'placeholder': 'El nivel de acceso',
        'id':'level','class':'form-control','value':''}
        )
        )

class NuevoUsuarioFormulario(forms.Form):
    niveles =  [ ('1','Administrador'),('0','Usuario'),('2','Empleado') ]

    username = forms.CharField(
        label = "Nombre de usuario",
        max_length=50,
        widget = forms.TextInput(attrs={'placeholder': 'Inserte un nombre de usuario',
        'id':'username','class':'form-control','value':''} ),
        )

    first_name = forms.CharField(
        label = 'Nombre',
        max_length =100,
        widget = forms.TextInput(attrs={'placeholder': 'Inserte un nombre',
        'id':'first_name','class':'form-control','value':''}),            
        )

    last_name = forms.CharField(
        label = 'Apellido',
        max_length = 100,
        widget = forms.TextInput(attrs={'class':'form-control','id':'last_name','placeholder':'Inserte un apellido','value':''}), 
        )

    email = forms.CharField(
        label = 'Correo electronico',
        max_length=100,
        widget = forms.TextInput(attrs={'placeholder': 'Inserte un correo valido',
        'id':'email','class':'form-control','type':'email','value':''} )
        )    

    password = forms.CharField(
        label = 'Clave',
        max_length=100,
        widget = forms.TextInput(attrs={'placeholder': 'Inserte una clave',
        'id':'password','class':'form-control','type':'password','value':''} )
        )  

    rep_password = forms.CharField(
        label = 'Repetir clave',
        max_length=100,
        widget = forms.TextInput(attrs={'placeholder': 'Repita la clave de arriba',
        'id':'rep_password','class':'form-control','type':'password','value':''} )
        )  

    level =  forms.CharField(
        label="Nivel de acceso",
        max_length=2,
        widget=forms.Select(choices=niveles,attrs={'placeholder': 'El nivel de acceso',
        'id':'level','class':'form-control','value':''}
        )
        )


class ClaveFormulario(forms.Form):
    clave = forms.CharField(
        label = 'Ingrese su clave actual',
        max_length=50,
        widget = forms.TextInput(
        attrs={'placeholder': 'Inserte la clave actual para verificar su identidad',
        'id':'clave','class':'form-control', 'type': 'password'}),
        )

    clave_nueva = forms.CharField(
        label = 'Ingrese la clave nueva',
        max_length=50,
        widget = forms.TextInput(
        attrs={'placeholder': 'Inserte la clave nueva de acceso',
        'id':'clave_nueva','class':'form-control', 'type': 'password'}),
        )

    repetir_clave = forms.CharField(
        label="Repita la clave nueva",
        max_length=50,
        widget = forms.TextInput(
        attrs={'placeholder': 'Vuelva a insertar la clave nueva',
        'id':'repetir_clave','class':'form-control', 'type': 'password'}),
        )


class ImportarBDDFormulario(forms.Form):
    archivo = forms.FileField(
        widget=forms.FileInput(
            attrs={'placeholder': 'Archivo de la base de datos',
            'id':'customFile','class':'custom-file-input'})
        )

class OpcionesFormulario(forms.Form):
    moneda = forms.CharField(
        label = 'Moneda a emplear en el sistema',
        max_length=20,
        widget = forms.TextInput(
        attrs={'placeholder': 'Inserte la abreviatura de la moneda que quiere usar (Ejemplo: $)',
        'id':'moneda','class':'form-control'}),
        )

    mensaje_factura = forms.CharField(
        label = 'Mensaje personal que va en las facturas',
        max_length=50,
        widget = forms.TextInput(
        attrs={'placeholder': 'Inserte el mensaje personal que ira en el pie de la factura',
        'id':'mensaje_factura','class':'form-control'}),
        )

    nombre_negocio = forms.CharField(
        label = 'Nombre actual del negocio',
        max_length=50,
        widget = forms.TextInput(
        attrs={'class':'form-control','id':'nombre_negocio',
            'placeholder':'Coloque el nombre actual del negocio'}),
        )

    imagen = forms.FileField(required=False,widget = forms.FileInput(
        attrs={'class':'custom-file-input','id':'customFile'}))

#Formulario Estado
class EstadoFormulario(forms.ModelForm):
    class Meta:
        model = Estado
        fields = ['nombre']
        labels = {
            'nombre': 'Nombre del estado del producto',
        }
        widgets = {
           'nombre': forms.TextInput(attrs={'placeholder': 'Estado del producto', 'class': 'form-control'}),
        }

#Estado Producto Formulario
class EstadoProductoFormulario(forms.ModelForm):
    class Meta:
        model = EstadoProducto
        fields = ['nombre']
        labels = {
            'nombre': 'Nombre del estado del producto',
        }
        widgets = {
           'nombre': forms.TextInput(attrs={'placeholder': 'Estado del producto', 'class': 'form-control'}),
        }

#Formulario Bodega
class BodegaFormulario(forms.ModelForm):
   class Meta:
        model = Bodega
        fields = ['nombre', 'ubicacion','estado']
        labels = {
            'nombre': 'Nombre de la bodega',
            'ubicacion':'Ubicación de la bodega',
            'estado':'Estado de la bodega',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre de la bodega', 'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'placeholder': 'Ubicación de la bodega', 'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'})
        }


#Formulario Marca
class MarcaFormulario(forms.ModelForm):
   class Meta:
        model = Marca
        fields = ['nombre']
        labels = {
            'nombre': 'Nombre de la marca',
        }
        widgets = {
           'nombre': forms.TextInput(attrs={'placeholder': 'Nombre de la marca', 'class': 'form-control'}),
        }


class BuscarInventarioFormulario(forms.Form):
    bodega = forms.ModelChoiceField(queryset=Bodega.objects.all(), required=False, label='Bodega', widget=forms.Select(attrs={'class': 'form-control'}))
    producto = forms.ModelChoiceField(queryset=Producto.objects.all(), required=False, label='Producto', widget=forms.Select(attrs={'class': 'form-control'}))
    estado = forms.ChoiceField(choices=[('Disponible', 'Disponible'), ('Dañado', 'Dañado'), ('En reparación', 'En reparación'), ('Vendido', 'Vendido'), ('Pendiente', 'Pendiente')], required=False, label='Estado', widget=forms.Select(attrs={'class': 'form-control'}))


# Formulario Registro Inventario

class RegistroInventarioFormulario(forms.ModelForm):
    class Meta:
        model = RegistroInventario
        fields = ['producto', 'bodega', 'cantidad']
        labels = {
            'producto': 'Producto',
            'bodega': 'Bodega',
            'cantidad': 'Cantidad',
        }
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'bodega': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad'}),
        }
# Formulario Reparaciónclass ReparacionFormulario(forms.ModelForm):
class ReparacionFormulario(forms.ModelForm):
    class Meta:
        model = Reparacion
        fields = ['idproducto', 'descripcion_problema', 'fecha_retorno', 'estado']
        labels = {
            'idproducto': 'Producto',
            'descripcion_problema': 'Descripción del problema',
            'fecha_retorno': 'Fecha de retorno',
            'estado': 'Estado',
        }
        widgets = {
            'idproducto': forms.Select(attrs={'class': 'form-control'}),
            'descripcion_problema': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción del problema'}),
            'fecha_retorno': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }
# Formulario Entrega
class EntregaFormulario(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ['idproducto', 'idbodega', 'id_empleado_recibio', 'cantidad']
        labels = {
            'idproducto': 'Producto',
            'idbodega': 'Bodega',
            'id_empleado_recibio': 'Empleado que Recibe',
            'cantidad': 'Cantidad',
        }
        widgets = {
            'idproducto': forms.Select(attrs={'class': 'form-control'}),
            'idbodega': forms.Select(attrs={'class': 'form-control'}),
            'id_empleado_recibio': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad'}),
        }

# Formulario Movimiento Producto
class MovimientoProductoFormulario(forms.Form):
    bodega = forms.ModelChoiceField(queryset=Bodega.objects.all(), required=False, label='Bodega', widget=forms.Select(attrs={'class': 'form-control'}))
    producto = forms.ModelChoiceField(queryset=Producto.objects.all(), required=False, label='Producto', widget=forms.Select(attrs={'class': 'form-control'}))
    empleado = forms.ModelChoiceField(queryset=Empleado.objects.all(), required=False, label='Empleado', widget=forms.Select(attrs={'class': 'form-control'}))
    estado_producto = forms.ModelChoiceField(queryset=EstadoProducto.objects.all(), required=False, label='Estado del Producto', widget=forms.Select(attrs={'class': 'form-control'}))

class RecepcionFormulario(forms.Form):
    empleado = forms.ModelChoiceField(queryset=Empleado.objects.all(), widget=forms.HiddenInput())
    producto = forms.ModelChoiceField(queryset=Producto.objects.all(), widget=forms.HiddenInput())
    bodega = forms.ModelChoiceField(queryset=Bodega.objects.all(), widget=forms.HiddenInput())
    cantidad_vendida = forms.IntegerField(min_value=0)
    cantidad_devuelta = forms.IntegerField(min_value=0)
    bodega_devuelta = forms.ModelChoiceField(queryset=Bodega.objects.all(), required=False)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'productos_pendientes' in kwargs:
            for producto in kwargs.pop('productos_pendientes'):
                self.fields[f'cantidad_vendida_{producto.id}'] = forms.IntegerField(min_value=0, max_value=producto.cantidad)
                self.fields[f'cantidad_devuelta_{producto.id}'] = forms.IntegerField(min_value=0, max_value=producto.cantidad)