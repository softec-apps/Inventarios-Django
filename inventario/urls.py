from django.urls import path, include
from . import views
from .funciones import *
app_name = "inventario"

urlpatterns = [
    path('tinymce/', include('tinymce.urls')),

    path('login', views.Login.as_view(), name='login'),
    path('panel', views.Panel.as_view(), name='panel'),
    path('salir', views.Salir.as_view(), name='salir'),
    path('perfil/<str:modo>/<int:p>', views.Perfil.as_view(), name='perfil'),
    path('eliminar/<str:modo>/<int:p>', views.Eliminar.as_view(), name='eliminar'),

    path('listarCategorias', views.ListarCategorias.as_view(), name='listarCategorias'),
    path('agregarCategoria', views.AgregarCategoria.as_view(), name='agregarCategoria'),
    path('importarCategorias', views.ImportarCategorias.as_view(), name='importarCategorias'),
    path('exportarCategorias', views.ExportarCategorias.as_view(), name='exportarCategorias'),
    path('editarCategoria/<int:p>', views.EditarCategoria.as_view(), name='editarCategoria'),

    path('listarProductos', views.ListarProductos.as_view(), name='listarProductos'),
    path('agregarProducto', views.AgregarProducto.as_view(), name='agregarProducto'),
    path('importarProductos', views.ImportarProductos.as_view(), name='importarProductos'),
    path('exportarProductos', views.ExportarProductos.as_view(), name='exportarProductos'),
    path('editarProducto/<int:p>', views.EditarProducto.as_view(), name='editarProducto'),

    path('listarProveedores', views.ListarProveedores.as_view(), name='listarProveedores'),
    path('agregarProveedor', views.AgregarProveedor.as_view(), name='agregarProveedor'),
    path('importarProveedores', views.ImportarProveedores.as_view(), name='importarProveedores'),
    path('exportarProveedores', views.ExportarProveedores.as_view(), name='exportarProveedores'),
    path('editarProveedor/<int:p>', views.EditarProveedor.as_view(), name='editarProveedor'),

    path('agregarPedido', views.AgregarPedido.as_view(), name='agregarPedido'),
    path('listarPedidos', views.ListarPedidos.as_view(), name='listarPedidos'),
    path('detallesPedido', views.DetallesPedido.as_view(), name='detallesPedido'),
    path('verPedido/<int:p>',views.VerPedido.as_view(), name='verPedido'),
    path('validarPedido/<int:p>',views.ValidarPedido.as_view(), name='validarPedido'),
    path('generarPedido/<int:p>',views.GenerarPedido.as_view(), name='generarPedido'),
    path('generarPedidoPDF/<int:p>',views.GenerarPedidoPDF.as_view(), name='generarPedidoPDF'),

    path('listarClientes', views.ListarClientes.as_view(), name='listarClientes'),
    path('agregarCliente', views.AgregarCliente.as_view(), name='agregarCliente'),
    path('importarClientes', views.ImportarClientes.as_view(), name='importarClientes'),
    path('exportarClientes', views.ExportarClientes.as_view(), name='exportarClientes'),
    path('editarCliente/<int:p>', views.EditarCliente.as_view(), name='editarCliente'),

    path('listarDescuentos', views.ListarDescuentos.as_view(), name='listarDescuentos'),
    path('agregarDescuento', views.AgregarDescuento.as_view(), name='agregarDescuento'),
    path('editarDescuento/<int:p>', views.EditarDescuento.as_view(), name='editarDescuento'),

    path('emitirVenta', views.EmitirFactura.as_view(), name='emitirVenta'),
    path('detallesDeVenta', views.DetallesFactura.as_view(), name='detallesDeVenta'),
    path('listarVentas',views.ListarFacturas.as_view(), name='listarVentas'),
    path('verVenta/<int:p>',views.VerFactura.as_view(), name='verVenta'),
    path('generarVenta/<int:p>',views.GenerarFactura.as_view(), name='generarVenta'),
    path('generarVentaPDF/<int:p>',views.GenerarFacturaPDF.as_view(), name='generarVentaPDF'),

    path('crearUsuario',views.CrearUsuario.as_view(), name='crearUsuario'),
    path('listarUsuarios', views.ListarUsuarios.as_view(), name='listarUsuarios'),

    # path('importarBDD',views.ImportarBDD.as_view(), name='importarBDD'),
    # path('descargarBDD', views.DescargarBDD.as_view(), name='descargarBDD'),
    path('configuracionGeneral', views.ConfiguracionGeneral.as_view(), name='configuracionGeneral'),

    # path('verManualDeUsuario/<str:pagina>/',views.VerManualDeUsuario.as_view(), name='verManualDeUsuario'),

    #rutas para el manejo del Kardex
    path('lista_productos/', views.ListaProductosView.as_view(), name='lista_productos'),
    path('detalle_kardex/<int:producto_id>/', views.DetalleKardexView.as_view(), name='detalle_kardex'),
    path('resumen_kardex/<int:producto_id>/', views.ResumenKardexView.as_view(), name='resumen_kardex'),
    path('nuevo_movimiento/<int:producto_id>/', views.NuevoMovimientoView.as_view(), name='nuevo_movimiento'),
    path('registrar_movimiento/<int:producto_id>/', views.RegistrarMovimientoView.as_view(), name='registrar_movimiento'),

    #rutas exportacion de datos
    path('exportar/productos/csv/', exportar_productos_csv, name='exportar_productos_csv'),
    path('exportar/productos/excel/', exportar_productos_excel, name='exportar_productos_excel'),
    path('exportar/kardex/csv/', exportar_kardex_csv, name='exportar_kardex_csv'),
    path('exportar/kardex/excel/', exportar_kardex_excel, name='exportar_kardex_excel'),
    path('exportar/kardex/producto/<int:producto_id>/csv/', exportar_kardex_producto_csv, name='exportar_kardex_producto_csv'),
    path('exportar/kardex/producto/<int:producto_id>/excel/', exportar_kardex_producto_excel, name='exportar_kardex_producto_excel'),
    path('exportar/proveedores/csv/', exportar_proveedores_csv, name='exportar_proveedores_csv'),
    path('exportar/proveedores/excel/', exportar_proveedores_excel, name='exportar_proveedores_excel'),
    path('exportar/pedidos/csv/', exportar_pedidos_csv, name='exportar_pedidos_csv'),
    path('exportar/pedidos/excel/', exportar_pedidos_excel, name='exportar_pedidos_excel'),
    path('exportar/categorias/csv/', exportar_categorias_csv, name='exportar_categorias_csv'),
    path('exportar/categorias/excel/', exportar_categorias_excel, name='exportar_categorias_excel'),
    path('exportar/clientes/csv/', exportar_clientes_csv, name='exportar_clientes_csv'),
    path('exportar/clientes/excel/', exportar_clientes_excel, name='exportar_clientes_excel'),
    path('exportar/descuentos/csv/', exportar_descuentos_csv, name='exportar_descuentos_csv'),
    path('exportar/descuentos/excel/', exportar_descuentos_excel, name='exportar_descuentos_excel'),
    path('exportar/facturas/csv/', exportar_facturas_csv, name='exportar_facturas_csv'),
    path('exportar/facturas/excel/', exportar_facturas_excel, name='exportar_facturas_excel'),
    path('exportar/usuarios/csv/', exportar_usuarios_csv, name='exportar_usuarios_csv'),
    path('exportar/usuarios/excel/', exportar_usuarios_excel, name='exportar_usuarios_excel'),
]
