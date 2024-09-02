from django.db import models
from django.contrib.auth.models import AbstractUser


# MODELOS
class PersonaBase(models.Model):
    #id
    CEDULA_CHOICES =  [
        ('1', 'Cédula de Identidad'),
        ('2', 'Pasaporte'),
        ('3', 'Cédula de Identidad para Extranjeros'),
    ]
    tipoCedula = models.CharField(max_length=1, choices=CEDULA_CHOICES, default='1')
    cedula = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=60)
    ciudad = models.CharField(max_length=100, null=True)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    telefono2 = models.CharField(max_length=20, null=True)
    correo = models.CharField(max_length=100)
    correo2 = models.CharField(max_length=100, null=True)

    class Meta:
        abstract = True

    def get_tipo_cedula_texto(self):
        # Retorna el texto correspondiente al tipo de cedula
        return dict(self.CEDULA_CHOICES).get(self.tipoCedula, 'Desconocido')


#--------------------------------USUARIO------------------------------------------------
class Usuario(AbstractUser):
    #id
    username = models.CharField(max_length=80, unique=True)
    password = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=60)
    nivel = models.IntegerField(null=True)

    @classmethod
    def numeroRegistrados(self):
        return int(self.objects.all().count() )

    @classmethod
    def numeroUsuarios(self,tipo):
        if tipo == 'administrador':
            return int(self.objects.filter(is_superuser = True).count() )
        elif tipo == 'usuario':
            return int(self.objects.filter(is_superuser = False).count() )


class Opciones(models.Model):
    #id
    moneda = models.CharField(max_length=20, null=True)
    valor_iva = models.IntegerField(unique=True)
    nombre_negocio = models.CharField(max_length=25, null=True)
    mensaje_factura = models.TextField(null=True)

#---------------------------------------------------------------------------------------


#-------------------------------CATEGORIA------------------------------------------------
class Categoria(models.Model):
    #id
    nombre = models.CharField(max_length=50, unique=True)

    @classmethod
    def numeroRegistrados(self):
        return int(self.objects.all().count())

    def __str__(self):
        return self.nombre


#-------------------------------PRODUCTO------------------------------------------------
class Producto(models.Model):
    #id
    # ruc_proveedor = models.CharField(max_length=13, unique=True)
    decisiones =  [('1','sacos'),('2','kg'),('3','lb')]
    descripcion = models.CharField(max_length=40)
    precio = models.DecimalField(max_digits=9,decimal_places=2)
    disponible = models.IntegerField(null=True)
    medida = models.CharField(max_length=20, choices=decisiones, default='1')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    tiene_iva = models.BooleanField(null=True)

    @classmethod
    def numeroRegistrados(self):
        return int(self.objects.all().count() )

    @classmethod
    def numeroDisponibles(self):
        return int(self.objects.filter(disponible__gt=0).values().count() )


    @classmethod
    def productosRegistrados(self):
        objetos = self.objects.all().order_by('descripcion')
        return objetos


    @classmethod
    def preciosProductos(self):
        objetos = self.objects.all().order_by('id')
        arreglo = []
        etiqueta = True
        extra = 1

        for indice,objeto in enumerate(objetos):
            arreglo.append([])
            if etiqueta:
                arreglo[indice].append(0)
                arreglo[indice].append("------")
                etiqueta = False
                arreglo.append([])

            arreglo[indice + extra].append(objeto.id)
            precio_producto = objeto.precio
            arreglo[indice + extra].append("%d" % (precio_producto) )

        return arreglo

    @classmethod
    def productosDisponibles(self):
        objetos = self.objects.all().order_by('id')
        arreglo = []
        etiqueta = True
        extra = 1

        for indice,objeto in enumerate(objetos):
            arreglo.append([])
            if etiqueta:
                arreglo[indice].append(0)
                arreglo[indice].append("------")
                etiqueta = False
                arreglo.append([])

            arreglo[indice + extra].append(objeto.id)
            productos_disponibles = objeto.disponible
            arreglo[indice + extra].append("%d" % (productos_disponibles) )

        return arreglo

    def actualizar_stock(self, cantidad, es_entrada=True):
        if es_entrada:
            self.disponible += cantidad
        else:
            self.disponible -= cantidad
        self.save()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_stock = Producto.objects.filter(pk=self.pk).values_list('disponible', flat=True).first() if not is_new else 0
        super().save(*args, **kwargs)

        if is_new and self.disponible > old_stock:
            cantidad = self.disponible - old_stock if not is_new else self.disponible
            Kardex.registrar_movimiento(
                producto=self,
                tipo_movimiento='ENTRADA',
                cantidad=cantidad,
                valor_unitario=self.precio,
                detalle='Registro inicial' if is_new else 'Actualización de stock'
            )
#---------------------------------------------------------------------------------------


#------------------------------------------Kardex--------------------------------------

class Kardex(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    tipo_movimiento = models.CharField(max_length=10, choices=[('ENTRADA', 'Entrada'), ('SALIDA', 'Salida')])
    cantidad = models.IntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_cantidad = models.IntegerField()
    saldo_valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    detalle = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        if not self.pk:  # Si es un nuevo registro
            ultimo_kardex = Kardex.objects.filter(producto=self.producto).order_by('-fecha', '-id').first()

            if self.tipo_movimiento == 'ENTRADA':
                self.saldo_cantidad = (ultimo_kardex.saldo_cantidad if ultimo_kardex else 0) + self.cantidad
                self.saldo_valor_total = (ultimo_kardex.saldo_valor_total if ultimo_kardex else 0) + self.valor_total
            else:  # SALIDA
                self.saldo_cantidad = (ultimo_kardex.saldo_cantidad if ultimo_kardex else 0) - self.cantidad
                self.saldo_valor_total = (ultimo_kardex.saldo_valor_total if ultimo_kardex else 0) - self.valor_total

            # Actualizar el stock del producto
            self.producto.disponible = self.saldo_cantidad
            self.producto.save()

        super().save(*args, **kwargs)

    @classmethod
    def registrar_movimiento(cls, producto, tipo_movimiento, cantidad, valor_unitario, detalle):
        valor_total = cantidad * valor_unitario
        kardex = cls(
            producto=producto,
            tipo_movimiento=tipo_movimiento,
            cantidad=cantidad,
            valor_unitario=valor_unitario,
            valor_total=valor_total,
            detalle=detalle
        )
        kardex.save()
        return kardex

#---------------------------------------------------------------------------------------


#------------------------------------------CLIENTE--------------------------------------
class Cliente(PersonaBase):
    #id
    generoChoices =  [('1','Masculino'),('2','Femenino'),('3','Otro')]
    genero = models.CharField(max_length=20, choices=generoChoices, default='1')
    nacimiento = models.DateField(null=True)

    @classmethod
    def numeroRegistrados(self):
        return int(self.objects.all().count() )

    @classmethod
    def cedulasRegistradas(self):
        objetos = self.objects.all().order_by('nombre')
        arreglo = []
        for indice,objeto in enumerate(objetos):
            arreglo.append([])
            arreglo[indice].append(objeto.cedula)
            nombre_cliente = objeto.nombre + " " + objeto.apellido
            arreglo[indice].append("%s. C.I: %s" % (nombre_cliente,self.formatearCedula(objeto.cedula)) )

        return arreglo


    @staticmethod
    def formatearCedula(cedula):
        # return format(int(cedula), ',d')
        return cedula
#-----------------------------------------------------------------------------------------


#-------------------------------------DESCUENTOS---------------------------------------------
class Descuento(models.Model):
    #id
    nombre = models.CharField(max_length=100)
    valor = models.FloatField()
    # porcentaje = models.BooleanField()

    def __str__(self):
        return str(self.nombre) + " - " + str(self.valor) + "%"

    @classmethod
    def numeroRegistrados(self):
        return int(self.objects.all().count() )
#-----------------------------------------------------------------------------------------


#-------------------------------------FACTURA---------------------------------------------
class Factura(models.Model):
    #id
    cliente = models.ForeignKey(Cliente,to_field='cedula', on_delete=models.CASCADE)
    fecha = models.DateField()
    sub_monto = models.DecimalField(max_digits=20,decimal_places=2)
    descuento = models.ForeignKey(Descuento, on_delete=models.SET_NULL, null=True, blank=True)
    descuento_total = models.DecimalField(max_digits=20,decimal_places=2)
    monto_general = models.DecimalField(max_digits=20,decimal_places=2)
    iva = models.ForeignKey(Opciones,to_field='valor_iva', on_delete=models.CASCADE)

    @classmethod
    def numeroRegistrados(self):
        return int(self.objects.all().count() )

    @classmethod
    def ingresoTotal(self):
        facturas = self.objects.all()
        total = 0

        for factura in facturas:
            total += factura.monto_general

        return total
#-----------------------------------------------------------------------------------------


#-------------------------------------DETALLES DE FACTURA---------------------------------
class DetalleFactura(models.Model):
    #id
    id_factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    sub_total = models.DecimalField(max_digits=20,decimal_places=2)
    total = models.DecimalField(max_digits=20,decimal_places=2)

    @classmethod
    def productosVendidos(self):
        vendidos = self.objects.all()
        totalVendidos = 0
        for producto in vendidos:
            totalVendidos += producto.cantidad

        return totalVendidos

    @classmethod
    def ultimasVentas(self):
        objetos = self.objects.all().order_by('-id')[:10]

        return objetos
#---------------------------------------------------------------------------------------


#------------------------------------------PROVEEDOR-----------------------------------
class Proveedor(PersonaBase):
    #id
    ruc = models.CharField(max_length=13, unique=True)

    @classmethod
    def cedulasRegistradas(self):
        objetos = self.objects.all().order_by('nombre')
        arreglo = []
        for indice,objeto in enumerate(objetos):
            arreglo.append([])
            arreglo[indice].append(objeto.cedula)
            nombre_cliente = objeto.nombre + " " + objeto.apellido
            arreglo[indice].append("%s. C.I: %s" % (nombre_cliente,self.formatearCedula(objeto.cedula)) )
        return arreglo

    @staticmethod
    def formatearCedula(cedula):
        return format(int(cedula), ',d')
#---------------------------------------------------------------------------------------


#----------------------------------------PEDIDO-----------------------------------------
class Pedido(models.Model):
    #id
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha = models.DateField()
    sub_monto = models.DecimalField(max_digits=20,decimal_places=2)
    monto_general = models.DecimalField(max_digits=20,decimal_places=2)
    iva = models.ForeignKey(Opciones,to_field='valor_iva', on_delete=models.CASCADE)
    presente = models.BooleanField(null=True)

    @classmethod
    def recibido(self, pedido):
        return self.objects.get(id=pedido).presente

#---------------------------------------------------------------------------------------


#-------------------------------------DETALLES DE PEDIDO-------------------------------
class DetallePedido(models.Model):
    #id
    id_pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    sub_total = models.DecimalField(max_digits=20,decimal_places=2)
    total = models.DecimalField(max_digits=20,decimal_places=2)
#---------------------------------------------------------------------------------------


#------------------------------------NOTIFICACIONES------------------------------------
class Notificaciones(models.Model):
    #id
    autor = models.ForeignKey(Usuario,to_field='username', on_delete=models.CASCADE)
    mensaje = models.TextField()
#---------------------------------------------------------------------------------------