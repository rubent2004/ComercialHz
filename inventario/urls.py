from django.urls import path
from . import views

app_name = "inventario"

urlpatterns = [
path('login', views.Login.as_view(), name='login'),
path('panel', views.Panel.as_view(), name='panel'),
path('salir', views.Salir.as_view(), name='salir'),
path('perfil/<str:modo>/<int:p>', views.Perfil.as_view(), name='perfil'),
path('eliminar/<str:modo>/<int:p>', views.Eliminar.as_view(), name='eliminar'),


path('listarClientes', views.ListarClientes.as_view(), name='listarClientes'),
path('agregarCliente', views.AgregarCliente.as_view(), name='agregarCliente'),
path('importarClientes', views.ImportarClientes.as_view(), name='importarClientes'),
path('exportarClientes', views.ExportarClientes.as_view(), name='exportarClientes'),
path('editarCliente/<int:p>', views.EditarCliente.as_view(), name='editarCliente'),

path('emitirFactura', views.EmitirFactura.as_view(), name='emitirFactura'),
path('detallesDeFactura', views.DetallesFactura.as_view(), name='detallesDeFactura'),
path('listarFacturas',views.ListarFacturas.as_view(), name='listarFacturas'),
path('verFactura/<int:p>',views.VerFactura.as_view(), name='verFactura'),
path('generarFactura/<int:p>',views.GenerarFactura.as_view(), name='generarFactura'),
path('generarFacturaPDF/<int:p>',views.GenerarFacturaPDF.as_view(), name='generarFacturaPDF'),

path('crearUsuario',views.CrearUsuario.as_view(), name='crearUsuario'),
path('listarUsuarios', views.ListarUsuarios.as_view(), name='listarUsuarios'),

path('importarBDD',views.ImportarBDD.as_view(), name='importarBDD'),
path('descargarBDD', views.DescargarBDD.as_view(), name='descargarBDD'),
path('configuracionGeneral', views.ConfiguracionGeneral.as_view(), name='configuracionGeneral'),

path('verManualDeUsuario/<str:pagina>/',views.VerManualDeUsuario.as_view(), name='verManualDeUsuario')
]

