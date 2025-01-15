# from django import forms
# from .models import Devolucion, Entrega, Estado, Categoria, Bodega, Inventario, MovimientoProducto, PedidoItem, Proveedor, Producto, EstadoProducto, Marca, Pedido, Recepcion, Reparacion
# from django.forms import ModelChoiceField

# class MisProductos(ModelChoiceField):
#     def label_from_instance(self, obj):
#         return "%s" % obj.descripcion

# class MisPrecios(ModelChoiceField):
#     def label_from_instance(self,obj):
#         return "%s" % obj.precio

# class MisDisponibles(ModelChoiceField):
#     def label_from_instance(self,obj):
#         return "%s" % obj.disponible


# class EstadoForm(forms.ModelForm):
#     class Meta:
#         model = Estado
#         fields = ['estado']
#         labels = {
#             'estado': 'Estado'
#         }
#         widgets = {
#             'estado': forms.TextInput(attrs={'placeholder': 'Estado', 'class': 'form-control'})
#         }

# class CategoriaForm(forms.ModelForm):
#     class Meta:
#         model = Categoria
#         fields = ['nombre']
#         labels = {
#             'nombre': 'Nombre'
#         }
#         widgets = {
#             'nombre': forms.TextInput(attrs={'placeholder': 'Nombre de la categoría', 'class': 'form-control'})
#         }

# class EstadoProductoForm(forms.ModelForm):
#     class Meta:
#         model = EstadoProducto
#         fields = ['nombre']
#         labels = {
#             'nombre': 'Nombre'
#         }
#         widgets = {
#             'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del estado', 'class': 'form-control'})
#         }

# class MarcaForm(forms.ModelForm):
#     class Meta:
#         model = Marca
#         fields = ['marca']
#         labels = {
#             'marca': 'Marca'
#         }
#         widgets = {
#             'marca': forms.TextInput(attrs={'placeholder': 'Nombre de la marca', 'class': 'form-control'})
#         }

# class BodegaForm(forms.ModelForm):
#     class Meta:
#         model = Bodega
#         fields = ['nombre', 'ubicacion', 'estado']
#         labels = {
#             'nombre': 'Nombre',
#             'ubicacion': 'Ubicación',
#             'estado': 'Estado'
#         }
#         widgets = {
#             'nombre': forms.TextInput(attrs={'placeholder': 'Nombre de la bodega', 'class': 'form-control'}),
#             'ubicacion': forms.TextInput(attrs={'placeholder': 'Ubicación de la bodega', 'class': 'form-control'}),
#             'estado': forms.Select(attrs={'class': 'form-control'})
#         }

# class ProveedorForm(forms.ModelForm):
#     class Meta:
#         model = Proveedor
#         fields = ['nombre', 'apellido', 'direccion', 'telefono', 'correo']
#         labels = {
#             'nombre': 'Nombre',
#             'apellido': 'Apellido',
#             'direccion': 'Dirección',
#             'telefono': 'Teléfono',
#             'correo': 'Correo'
#         }
#         widgets = {
#             'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del proveedor', 'class': 'form-control'}),
#             'apellido': forms.TextInput(attrs={'placeholder': 'Apellido del proveedor', 'class': 'form-control'}),
#             'direccion': forms.TextInput(attrs={'placeholder': 'Dirección del proveedor', 'class': 'form-control'}),
#             'telefono': forms.TextInput(attrs={'placeholder': 'Teléfono del proveedor', 'class': 'form-control'}),
#             'correo': forms.EmailInput(attrs={'placeholder': 'Correo del proveedor', 'class': 'form-control'})
#         }

# class ProductoForm(forms.ModelForm):
#     class Meta:
#         model = Producto
#         fields = ['descripcion', 'precio_unitario', 'precio_cash', 'codigo', 'disponible', 'imagen', 'categoria', 'proveedor', 'marca', 'estado']
#         labels = {
#             'descripcion': 'Descripción',
#             'precio_unitario': 'Precio Unitario',
#             'precio_cash': 'Precio Cash',
#             'codigo': 'Código',
#             'disponible': 'Disponible',
#             'imagen': 'Imagen',
#             'categoria': 'Categoría',
#             'proveedor': 'Proveedor',
#             'marca': 'Marca',
#             'estado': 'Estado'
#         }
#         widgets = {
#             'descripcion': forms.TextInput(attrs={'placeholder': 'Descripción del producto', 'class': 'form-control'}),
#             'precio_unitario': forms.NumberInput(attrs={'placeholder': 'Precio Unitario', 'class': 'form-control'}),
#             'precio_cash': forms.NumberInput(attrs={'placeholder': 'Precio Cash', 'class': 'form-control'}),
#             'codigo': forms.TextInput(attrs={'placeholder': 'Código del producto', 'class': 'form-control'}),
#             'disponible': forms.NumberInput(attrs={'placeholder': 'Cantidad disponible', 'class': 'form-control'}),
#             'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
#             'categoria': forms.Select(attrs={'class': 'form-control'}),
#             'proveedor': forms.Select(attrs={'class': 'form-control'}),
#             'marca': forms.Select(attrs={'class': 'form-control'}),
#             'estado': forms.Select(attrs={'class': 'form-control'})
#         }
# class ExportarProductosForm(forms.Form):
#     desde = forms.DateField(
#         label = 'Desde',
#         widget = forms.DateInput(format=('%d-%m-%Y'),
#         attrs={'id':'desde','class':'form-control','type':'date'}),
#         )   

#     hasta = forms.DateField(
#         label = 'Hasta',
#         widget = forms.DateInput(format=('%d-%m-%Y'),
#         attrs={'id':'hasta','class':'form-control','type':'date'}),
#         )   
# class ImportarProductosForm(forms.Form):
#     importar = forms.FileField(
#         max_length = 100000000000,
#         label = 'Escoger archivo',
#         widget = forms.ClearableFileInput(
#         attrs={'id':'importar','class':'form-control'}),
#         )


# class PedidoForm(forms.ModelForm):
#     class Meta:
#         model = Pedido
#         fields = ['proveedor', 'fecha', 'sub_monto', 'monto_general', 'presente']
#         labels = {
#             'proveedor': 'Proveedor',
#             'fecha': 'Fecha',
#             'sub_monto': 'Sub Monto',
#             'monto_general': 'Monto General',
#             'presente': 'Presente'
#         }
#         widgets = {
#             'proveedor': forms.Select(attrs={'class': 'form-control'}),
#             'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'sub_monto': forms.NumberInput(attrs={'placeholder': 'Sub Monto', 'class': 'form-control'}),
#             'monto_general': forms.NumberInput(attrs={'placeholder': 'Monto General', 'class': 'form-control'}),
#             'presente': forms.CheckboxInput(attrs={'class': 'form-check-input'})
#         }

# class PedidoItemForm(forms.ModelForm):
#     class Meta:
#         model = PedidoItem
#         fields = ['pedido', 'producto', 'bodega', 'cantidad']
#         labels = {
#             'pedido': 'Pedido',
#             'producto': 'Producto',
#             'bodega': 'Bodega',
#             'cantidad': 'Cantidad'
#         }
#         widgets = {
#             'pedido': forms.Select(attrs={'class': 'form-control'}),
#             'producto': forms.Select(attrs={'class': 'form-control'}),
#             'bodega': forms.Select(attrs={'class': 'form-control'}),
#             'cantidad': forms.NumberInput(attrs={'placeholder': 'Cantidad', 'class': 'form-control'})
#         }
# class EmitirPedidoForm(forms.Form):
#     def _init_(self, *args, **kwargs):
#         elecciones = kwargs.pop('cedulas')
#         super(EmitirPedidoForm, self)._init_(*args, **kwargs)

#         if(elecciones):
#             self.fields["proveedor"] = forms.CharField(label="Proveedor",max_length=50,
#             widget=forms.Select(choices=elecciones,attrs={'placeholder': 'La cedula del proveedor que vende el producto',
#             'id':'proveedor','class':'form-control'}))

#     productos = forms.IntegerField(label="Numero de productos",widget=forms.NumberInput(attrs={'placeholder': 'Numero de productos a comprar',
#         'id':'productos','class':'form-control'}))


# class DetallesPedidoFormulario(forms.Form):
#     productos = Producto.productosRegistrados()
#     precios = Producto.preciosProductos()

#     producto = MisProductos(queryset=productos, label="Producto",widget=forms.Select(attrs={'placeholder': 'Producto',
#         'id':'producto','class':'form-control'}))
    

# class InventarioForm(forms.ModelForm):
#     class Meta:
#         model = Inventario
#         fields = ['idbodega', 'idproducto', 'stock']
#         labels = {
#             'idbodega': 'Bodega',
#             'idproducto': 'Producto',
#             'stock': 'Stock'
#         }
#         widgets = {
#             'idbodega': forms.Select(attrs={'class': 'form-control'}),
#             'idproducto': forms.Select(attrs={'class': 'form-control'}),
#             'stock': forms.NumberInput(attrs={'placeholder': 'Stock', 'class': 'form-control'})
#         }

# class MovimientoProductoForm(forms.ModelForm):
#     class Meta:
#         model = MovimientoProducto
#         fields = ['bodega', 'producto', 'tipo_movimiento', 'cantidad', 'usuario', 'estado_producto']
#         labels = {
#             'bodega': 'Bodega',
#             'producto': 'Producto',
#             'tipo_movimiento': 'Tipo de Movimiento',
#             'cantidad': 'Cantidad',
#             'usuario': 'Usuario',
#             'estado_producto': 'Estado del Producto'
#         }
#         widgets = {
#             'bodega': forms.Select(attrs={'class': 'form-control'}),
#             'producto': forms.Select(attrs={'class': 'form-control'}),
#             'tipo_movimiento': forms.Select(attrs={'class': 'form-control'}),
#             'cantidad': forms.NumberInput(attrs={'placeholder': 'Cantidad', 'class': 'form-control'}),
#             'usuario': forms.Select(attrs={'class': 'form-control'}),
#             'estado_producto': forms.Select(attrs={'class': 'form-control'})
#         }

# class ReparacionForm(forms.ModelForm):
#     class Meta:
#         model = Reparacion
#         fields = ['idproducto', 'descripcion_problema', 'fecha_retorno', 'estado']
#         labels = {
#             'idproducto': 'Producto',
#             'descripcion_problema': 'Descripción del Problema',
#             'fecha_retorno': 'Fecha de Retorno',
#             'estado': 'Estado'
#         }
#         widgets = {
#             'idproducto': forms.Select(attrs={'class': 'form-control'}),
#             'descripcion_problema': forms.Textarea(attrs={'placeholder': 'Descripción del problema', 'class': 'form-control'}),
#             'fecha_retorno': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'estado': forms.Select(attrs={'class': 'form-control'})
#         }
# class DevolucionForm(forms.ModelForm):
#     class Meta:
#         model = Devolucion
#         fields = ['idproducto', 'idempleado', 'motivo']
#         labels = {
#             'idproducto': 'Producto',
#             'idempleado': 'Empleado',
#             'motivo': 'Motivo'
#         }
#         widgets = {
#             'idproducto': forms.Select(attrs={'class': 'form-control'}),
#             'idempleado': forms.Select(attrs={'class': 'form-control'}),
#             'motivo': forms.Textarea(attrs={'placeholder': 'Motivo de la devolución', 'class': 'form-control'})
#         }

# class EntregaForm(forms.ModelForm):
#     class Meta:
#         model = Entrega
#         fields = ['idproducto', 'idbodega', 'id_empleado_autorizo', 'id_empleado_recibio', 'cantidad']
#         labels = {
#             'idproducto': 'Producto',
#             'idbodega': 'Bodega',
#             'id_empleado_autorizo': 'Empleado que Autorizó',
#             'id_empleado_recibio': 'Empleado que Recibió',
#             'cantidad': 'Cantidad'
#         }
#         widgets = {
#             'idproducto': forms.Select(attrs={'class': 'form-control'}),
#             'idbodega': forms.Select(attrs={'class': 'form-control'}),
#             'id_empleado_autorizo': forms.Select(attrs={'class': 'form-control'}),
#             'id_empleado_recibio': forms.Select(attrs={'class': 'form-control'}),
#             'cantidad': forms.NumberInput(attrs={'placeholder': 'Cantidad', 'class': 'form-control'})
#         }

# class RecepcionForm(forms.ModelForm):
#     class Meta:
#         model = Recepcion
#         fields = ['idproducto', 'idbodega', 'id_empleado_autorizo', 'id_empleado_devolvio', 'cantidad', 'tipo_recepcion']
#         labels = {
#             'idproducto': 'Producto',
#             'idbodega': 'Bodega',
#             'id_empleado_autorizo': 'Empleado que Autorizó',
#             'id_empleado_devolvio': 'Empleado que Devolvió',
#             'cantidad': 'Cantidad',
#             'tipo_recepcion': 'Tipo de Recepción'
#         }
#         widgets = {
#             'idproducto': forms.Select(attrs={'class': 'form-control'}),
#             'idbodega': forms.Select(attrs={'class': 'form-control'}),
#             'id_empleado_autorizo': forms.Select(attrs={'class': 'form-control'}),
#             'id_empleado_devolvio': forms.Select(attrs={'class': 'form-control'}),
#             'cantidad': forms.NumberInput(attrs={'placeholder': 'Cantidad', 'class': 'form-control'}),
#             'tipo_recepcion': forms.Select(attrs={'class': 'form-control'})
#         }

