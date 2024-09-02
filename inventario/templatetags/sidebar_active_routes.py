from django import template

register = template.Library()


sections={
    'panel': ['panel'],
    'categorias':['listarCategorias', 'agregarCategoria', 'editarCategoria'],
    'productos': ['listarProductos', 'agregarProducto', 'editarProducto'],
    'kardex': ['lista_productos','detalle_kardex','resumen_kardex','nuevo_movimiento','registrar_movimiento'],
    'proveedores': ['listarProveedores', 'agregarProveedor', 'editarProveedor'],
    'pedidos': ['listarPedidos', 'agregarPedido', 'detallesPedido', 'verPedido'],
    'clientes': ['listarClientes', 'agregarCliente', 'editarCliente'],
    'descuentos': ['listarDescuentos', 'agregarDescuento', 'editarDescuento'],
    'ventas': ['emitirVenta', 'detallesDeVenta', 'listarVentas', 'verVenta'],
    'usuarios': ['crearUsuario', 'listarUsuarios'],
    'opciones': ['configuracionGeneral']
}

@register.filter(name='in_list')
def in_list(section_name, request):
    url_name = request.resolver_match.url_name
    return True if url_name in sections.get(section_name, []) else False