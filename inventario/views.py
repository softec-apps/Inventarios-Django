from os import path, makedirs
#renderiza las vistas al usuario
from django.shortcuts import render
# para redirigir a otras paginas
from django.http import HttpResponseRedirect, HttpResponse,FileResponse
#el formulario de login
from .forms import *
# clase para crear vistas basadas en sub-clases
from django.views import View
#autentificacion de usuario e inicio de sesion
from django.contrib.auth import authenticate, login, logout
#verifica si el usuario esta logeado
from django.contrib.auth.mixins import LoginRequiredMixin

#modelos
from .models import *
#formularios dinamicos
from django.forms import formset_factory
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

#Para generar el Kardex
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Producto, Kardex
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .forms import KardexForm
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.db.models import F
from django.db import transaction

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
        contexto = {
            'usuario': request.user.username,
            'id_usuario':request.user.id,
            'nombre': request.user.first_name,
            'apellido': request.user.last_name,
            'correo': request.user.email,
            'fecha':  date.today(),
            'productosRegistrados' : Producto.numeroRegistrados(),
            'productosVendidos' :  DetalleFactura.productosVendidos(),
            'clientesRegistrados' : Cliente.numeroRegistrados(),
            'usuariosRegistrados' : Usuario.numeroRegistrados(),
            'facturasEmitidas' : Factura.numeroRegistrados(),
            'ingresoTotal' : Factura.ingresoTotal(),
            'ultimasVentas': DetalleFactura.ultimasVentas(),
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
            perf = Usuario.objects.get(id=p)
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
            perf = Usuario.objects.get(id=p)
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
            perf = Usuario.objects.get(id=p)
            contexto = { 'perfil':perf }
            contexto = complementarContexto(contexto,request.user)

            return render(request,'inventario/perfil/verPerfil.html', contexto)



    def post(self,request,modo,p):
        if modo ==  'editar':
            # Crea una instancia del formulario y la llena con los datos:
            form = UsuarioFormulario(request.POST)
            # Revisa si es valido:

            if form.is_valid():
                perf = Usuario.objects.get(id=p)
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

                usuario = Usuario.objects.get(id=p)

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


#Elimina usuarios, productos, clientes o proveedores----------------------------
class Eliminar(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, modo, p):

        if modo == 'producto':
            prod = Producto.objects.get(id=p)
            prod.delete()
            messages.success(request, 'Producto de ID %s borrado exitosamente.' % p)
            return HttpResponseRedirect("/inventario/listarProductos")

        if modo == 'categoria':
            categoria = Categoria.objects.get(id=p)
            categoria.delete()
            messages.success(request, 'Categoría de ID %s borrado exitosamente.' % p)
            return HttpResponseRedirect("/inventario/listarCategorias")

        elif modo == 'cliente':
            cliente = Cliente.objects.get(id=p)
            cliente.delete()
            messages.success(request, 'Cliente de ID %s borrado exitosamente.' % p)
            return HttpResponseRedirect("/inventario/listarClientes")


        elif modo == 'proveedor':
            proveedor = Proveedor.objects.get(id=p)
            proveedor.delete()
            messages.success(request, 'Proveedor de ID %s borrado exitosamente.' % p)
            return HttpResponseRedirect("/inventario/listarProveedores")

        elif modo == 'usuario':
            if request.user.is_superuser == False:
                messages.error(request, 'No tienes permisos suficientes para borrar usuarios')
                return HttpResponseRedirect('/inventario/listarUsuarios')

            elif p == 1:
                messages.error(request, 'No puedes eliminar al super-administrador.')
                return HttpResponseRedirect('/inventario/listarUsuarios')

            elif request.user.id == p:
                messages.error(request, 'No puedes eliminar tu propio usuario.')
                return HttpResponseRedirect('/inventario/listarUsuarios')

            else:
                usuario = Usuario.objects.get(id=p)
                usuario.delete()
                messages.success(request, 'Usuario de ID %s borrado exitosamente.' % p)
                return HttpResponseRedirect("/inventario/listarUsuarios")
#Fin de vista-------------------------------------------------------------------


#Crea una lista de las categorías, 10 por pagina----------------------------------------#
class ListarCategorias(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        #Saca una lista de todos los clientes de la BDD
        categorias = Categoria.objects.all()
        contexto = {'tabla': categorias}
        contexto = complementarContexto(contexto,request.user)

        return render(request, 'inventario/categoria/listarCategorias.html',contexto)
#Fin de vista--------------------------------------------------------------------------#



#Maneja y visualiza un formulario--------------------------------------------------#
class AgregarCategoria(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        # Crea una instancia del formulario y la llena con los datos:
        form = CategoriaFormulario(request.POST)
        # Revisa si es valido:
        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            nombre = form.cleaned_data['nombre']

            prod = Categoria(nombre=nombre)
            prod.save()

            form = CategoriaFormulario()
            messages.success(request, 'Ingresado exitosamente bajo la ID %s.' % prod.id)
            request.session['categoriaProcesado'] = 'agregado'
            return HttpResponseRedirect("/inventario/agregarCategoria")
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/categoria/agregarCategoria.html', {'form': form})

    # Si se llega por GET crearemos un formulario en blanco
    def get(self,request):
        form = CategoriaFormulario()
        #Envia al usuario el formulario para que lo llene
        contexto = {'form':form , 'modo':request.session.get('categoriaProcesado')}
        contexto = complementarContexto(contexto,request.user)
        return render(request, 'inventario/categoria/agregarCategoria.html', contexto)
#Fin de vista------------------------------------------------------------------------#



#Formulario simple que procesa un script para importar las categorías-----------------#
class ImportarCategorias(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request):
        form = ImportaCategoriasFormulario(request.POST)
        if form.is_valid():
            request.session['categoriasImportados'] = True
            return HttpResponseRedirect("/inventario/importarCategorias")

    def get(self,request):
        form = ImportarCategoriasFormulario()

        if request.session.get('categoriasImportados') == True:
            importado = request.session.get('categoriaImportados')
            contexto = { 'form':form,'categoriasImportados': importado  }
            request.session['categoriasImportados'] = False

        else:
            contexto = {'form':form}
            contexto = complementarContexto(contexto,request.user)
        return render(request, 'inventario/categoria/importarCategorias.html',contexto)

#Fin de vista-------------------------------------------------------------------------#



#Formulario simple que crea un archivo y respalda las categorías-----------------------#
class ExportarCategorias(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request):
        form = ExportarCategoriasFormulario(request.POST)
        if form.is_valid():
            request.session['categoriasExportados'] = True

            #Se obtienen las entradas de producto en formato JSON
            data = serializers.serialize("json", Categoria.objects.all())
            fs = FileSystemStorage('inventario/tmp/')

            #Se utiliza la variable fs para acceder a la carpeta con mas facilidad
            with fs.open("categorias.json", "w") as out:
                out.write(data)
                out.close()

            with fs.open("categorias.json", "r") as out:
                response = HttpResponse(out.read(), content_type="application/force-download")
                response['Content-Disposition'] = 'attachment; filename="categorias.json"'
                out.close()
            #------------------------------------------------------------
            return response

    def get(self,request):
        form = ExportarCategoriasFormulario()

        if request.session.get('categoriasExportados') == True:
            exportado = request.session.get('categoriaExportados')
            contexto = { 'form':form,'categoriasExportados': exportado  }
            request.session['categoriasExportados'] = False

        else:
            contexto = {'form':form}
            contexto = complementarContexto(contexto,request.user)
        return render(request, 'inventario/categoria/exportarCategoria.html',contexto)
#Fin de vista-------------------------------------------------------------------------#



#Muestra el formulario especifico para editarlo----------------------------------#
class EditarCategoria(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request,p):
        # Crea una instancia del formulario y la llena con los datos:
        form = CategoriaFormulario(request.POST)
        # Revisa si es valido:
        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            nombre = form.cleaned_data['nombre']

            categoria = Categoria.objects.get(id=p)
            categoria.nombre = nombre
            categoria.save()
            form = CategoriaFormulario(instance=categoria)
            messages.success(request, 'Actualizado exitosamente la categoría de ID %s.' % p)
            request.session['categoriaProcesado'] = 'editado'
            return HttpResponseRedirect("/inventario/editarCategoria/%s" % categoria.id)
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/categoria/agregarCategoria.html', {'form': form})

    def get(self, request,p):
        prod = Categoria.objects.get(id=p)
        form = CategoriaFormulario(instance=prod)
        #Envia al usuario el formulario para que lo llene
        contexto = {'form':form , 'modo':request.session.get('categoriaProcesado'),'editar':True}
        contexto = complementarContexto(contexto,request.user)
        return render(request, 'inventario/categoria/agregarCategoria.html', contexto)
#Fin de vista------------------------------------------------------------------------------------#



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



#Maneja y visualiza un formulario--------------------------------------------------#
class AgregarProducto(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        # Crea una instancia del formulario y la llena con los datos:
        form = ProductoFormulario(request.POST)
        # Revisa si es valido:
        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            descripcion = form.cleaned_data['descripcion']
            precio = form.cleaned_data['precio']
            categoria = form.cleaned_data['categoria']
            tiene_iva = form.cleaned_data['tiene_iva']
            disponible = form.cleaned_data['disponible']

            prod = Producto(descripcion=descripcion,precio=precio,categoria=categoria,tiene_iva=tiene_iva,disponible=disponible)
            prod.save()

            form = ProductoFormulario()
            messages.success(request, 'Ingresado exitosamente bajo la ID %s.' % prod.id)
            request.session['productoProcesado'] = 'agregado'
            return HttpResponseRedirect("/inventario/agregarProducto")
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/producto/agregarProducto.html', {'form': form})

    # Si se llega por GET crearemos un formulario en blanco
    def get(self,request):
        form = ProductoFormulario()
        #Envia al usuario el formulario para que lo llene
        contexto = {'form':form , 'modo':request.session.get('productoProcesado')}
        contexto = complementarContexto(contexto,request.user)
        return render(request, 'inventario/producto/agregarProducto.html', contexto)
#Fin de vista------------------------------------------------------------------------#



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

    def post(self, request, p):
        form = ProductoFormulario(request.POST)
        if form.is_valid():
            with transaction.atomic():
                descripcion = form.cleaned_data['descripcion']
                precio = form.cleaned_data['precio']
                categoria = form.cleaned_data['categoria']
                tiene_iva = form.cleaned_data['tiene_iva']
                disponible_nuevo = form.cleaned_data['disponible']

                prod = Producto.objects.select_for_update().get(id=p)
                stock_anterior = prod.disponible
                
                prod.descripcion = descripcion
                prod.precio = precio
                prod.categoria = categoria
                prod.tiene_iva = tiene_iva
                
                # Actualizar el campo 'disponible' sumando el nuevo valor al existente
                Producto.objects.filter(id=p).update(disponible=F('disponible') + disponible_nuevo)
                
                # Refrescar la instancia del producto después de la actualización
                prod.refresh_from_db()

                # Registrar el movimiento en el Kardex
                if disponible_nuevo != 0:
                    tipo_movimiento = 'ENTRADA' if disponible_nuevo > 0 else 'SALIDA'
                    Kardex.registrar_movimiento(
                        producto=prod,
                        tipo_movimiento=tipo_movimiento,
                        cantidad=abs(disponible_nuevo),
                        valor_unitario=prod.precio,
                        detalle='Actualización de stock'
                    )
            
            form = ProductoFormulario(instance=prod)
            messages.success(request, f'Actualizado exitosamente el producto de ID {p}. Stock anterior: {stock_anterior}, Nuevo stock: {prod.disponible}')
            request.session['productoProcesado'] = 'editado'
            return HttpResponseRedirect(f"/inventario/editarProducto/{prod.id}")
        else:
            return render(request, 'inventario/producto/agregarProducto.html', {'form': form})

    def get(self, request, p):
        prod = Producto.objects.get(id=p)
        form = ProductoFormulario(instance=prod)
        contexto = {'form': form, 'modo': request.session.get('productoProcesado'), 'editar': True}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/producto/agregarProducto.html', contexto)
#Fin de vista------------------------------------------------------------------------------------#


#Crea una lista de los clientes, 10 por pagina----------------------------------------#
class ListarClientes(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        from django.db import models
        #Saca una lista de todos los clientes de la BDD
        clientes = Cliente.objects.all()                
        contexto = {'tabla': clientes}
        contexto = complementarContexto(contexto,request.user)         

        return render(request, 'inventario/cliente/listarClientes.html',contexto) 
#Fin de vista--------------------------------------------------------------------------#




#Crea y procesa un formulario para agregar a un cliente---------------------------------#
class AgregarCliente(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        # Crea una instancia del formulario y la llena con los datos:
        form = ClienteFormulario(request.POST)
        # Revisa si es valido:

        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere

            cedula = form.cleaned_data['cedula']
            tipoCedula = form.cleaned_data['tipoCedula']
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            direccion = form.cleaned_data['direccion']
            nacimiento = form.cleaned_data['nacimiento']
            telefono = form.cleaned_data['telefono']
            correo = form.cleaned_data['correo']
            telefono2 = form.cleaned_data['telefono2']
            correo2 = form.cleaned_data['correo2']

            cliente = Cliente(cedula=cedula,tipoCedula=tipoCedula,nombre=nombre,apellido=apellido,
                direccion=direccion,nacimiento=nacimiento,telefono=telefono,
                correo=correo,telefono2=telefono2,correo2=correo2)
            cliente.save()
            form = ClienteFormulario()

            messages.success(request, 'Ingresado exitosamente bajo la ID %s.' % cliente.id)
            request.session['clienteProcesado'] = 'agregado'
            return HttpResponseRedirect("/inventario/agregarCliente")
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/cliente/agregarCliente.html', {'form': form})

    def get(self,request):
        form = ClienteFormulario()
        #Envia al usuario el formulario para que lo llene
        contexto = {'form':form , 'modo':request.session.get('clienteProcesado')}
        contexto = complementarContexto(contexto,request.user)
        return render(request, 'inventario/cliente/agregarCliente.html', contexto)
#Fin de vista-----------------------------------------------------------------------------#




#Formulario simple que procesa un script para importar los clientes-----------------#
class ImportarClientes(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request):
        form = ImportarClientesFormulario(request.POST)
        if form.is_valid():
            request.session['clientesImportados'] = True
            return HttpResponseRedirect("/inventario/importarClientes")

    def get(self,request):
        form = ImportarClientesFormulario()

        if request.session.get('clientesImportados') == True:
            importado = request.session.get('clientesImportados')
            contexto = { 'form':form,'clientesImportados': importado  }
            request.session['clientesImportados'] = False

        else:
            contexto = {'form':form}
            contexto = complementarContexto(contexto,request.user)             
        return render(request, 'inventario/cliente/importarClientes.html',contexto)
#Fin de vista-------------------------------------------------------------------------#




#Formulario simple que crea un archivo y respalda los clientes-----------------------#
class ExportarClientes(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request):
        form = ExportarClientesFormulario(request.POST)
        if form.is_valid():
            request.session['clientesExportados'] = True

            #Se obtienen las entradas de producto en formato JSON
            data = serializers.serialize("json", Cliente.objects.all())
            fs = FileSystemStorage('inventario/tmp/')

            #Se utiliza la variable fs para acceder a la carpeta con mas facilidad
            with fs.open("clientes.json", "w") as out:
                out.write(data)
                out.close()  

            with fs.open("clientes.json", "r") as out:                 
                response = HttpResponse(out.read(), content_type="application/force-download")
                response['Content-Disposition'] = 'attachment; filename="clientes.json"'
                out.close() 
            #------------------------------------------------------------
            return response

    def get(self,request):
        form = ExportarClientesFormulario()

        if request.session.get('clientesExportados') == True:
            exportado = request.session.get('clientesExportados')
            contexto = { 'form':form,'clientesExportados': exportado  }
            request.session['clientesExportados'] = False

        else:
            contexto = {'form':form}
            contexto = complementarContexto(contexto,request.user) 
        return render(request, 'inventario/cliente/exportarClientes.html',contexto)
#Fin de vista-------------------------------------------------------------------------#




#Muestra el mismo formulario del cliente pero con los datos a editar----------------------#
class EditarCliente(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request,p):
        # Crea una instancia del formulario y la llena con los datos:
        cliente = Cliente.objects.get(id=p)
        form = ClienteFormulario(request.POST, instance=cliente)
        # Revisa si es valido:

        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            tipoCedula = form.cleaned_data['tipoCedula']
            cedula = form.cleaned_data['cedula']
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            direccion = form.cleaned_data['direccion']
            nacimiento = form.cleaned_data['nacimiento']
            telefono = form.cleaned_data['telefono']
            correo = form.cleaned_data['correo']
            telefono2 = form.cleaned_data['telefono2']
            correo2 = form.cleaned_data['correo2']

            cliente.tipoCedula = tipoCedula
            cliente.cedula = cedula
            cliente.nombre = nombre
            cliente.apellido = apellido
            cliente.direccion = direccion
            cliente.nacimiento = nacimiento
            cliente.telefono = telefono
            cliente.correo = correo
            cliente.telefono2 = telefono2
            cliente.correo2 = correo2
            cliente.save()
            form = ClienteFormulario(instance=cliente)

            messages.success(request, 'Actualizado exitosamente el cliente de ID %s.' % p)
            request.session['clienteProcesado'] = 'editado'
            return HttpResponseRedirect("/inventario/editarCliente/%s" % cliente.id)
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/cliente/agregarCliente.html', {'form': form})

    def get(self, request,p):
        cliente = Cliente.objects.get(id=p)
        form = ClienteFormulario(instance=cliente)
        #Envia al usuario el formulario para que lo llene
        contexto = {'form':form , 'modo':request.session.get('clienteProcesado'),'editar':True}
        contexto = complementarContexto(contexto,request.user)
        return render(request, 'inventario/cliente/agregarCliente.html', contexto)
#Fin de vista--------------------------------------------------------------------------------#


#Emite la primera parte de la factura------------------------------#
class EmitirFactura(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        # Crea una instancia del formulario y la llena con los datos:
        cedulas = Cliente.cedulasRegistradas()
        form = EmitirFacturaFormulario(request.POST,cedulas=cedulas)
        # Revisa si es valido:
        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            request.session['form_details'] = form.cleaned_data['productos']
            request.session['id_client'] = form.cleaned_data['cliente']
            return HttpResponseRedirect("detallesDeFactura")
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/factura/emitirFactura.html', {'form': form})

    def get(self, request):
        cedulas = Cliente.cedulasRegistradas()
        missing = False
        if cedulas is None:
            missing = True
        else:
            missing = len(cedulas) == 0
        form = EmitirFacturaFormulario(cedulas=cedulas)
        contexto = {'form':form, 'missing':missing}
        contexto = complementarContexto(contexto,request.user)
        return render(request, 'inventario/factura/emitirFactura.html', contexto)
#Fin de vista---------------------------------------------------------------------------------#



#Muestra y procesa los detalles de cada producto de la factura--------------------------------#
class DetallesFactura(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        cedula = request.session.get('id_client')
        productos = request.session.get('form_details')
        FacturaFormulario = formset_factory(DetallesFacturaFormulario, extra=productos)
        formset = FacturaFormulario()
        contexto = {'formset':formset}
        contexto = complementarContexto(contexto,request.user) 

        return render(request, 'inventario/factura/detallesFactura.html', contexto)        

    def post(self, request):
        cedula = request.session.get('id_client')
        productos = request.session.get('form_details')

        FacturaFormulario = formset_factory(DetallesFacturaFormulario, extra=productos)

        inicial = {
        'descripcion':'',
        'cantidad': 0,
        'subtotal':0,
        }

        data = {
    'form-TOTAL_FORMS': productos,
    'form-INITIAL_FORMS':0,
    'form-MAX_NUM_FORMS': '',
                }

        formset = FacturaFormulario(request.POST,data)

        if formset.is_valid():

            id_producto = []
            cantidad = []
            subtotal = []
            total_general = []
            sub_monto = 0
            monto_general = 0

            for form in formset:
                desc = form.cleaned_data['descripcion'].descripcion
                cant = form.cleaned_data['cantidad']
                sub = form.cleaned_data['valor_subtotal']
                id_producto.append(obtenerIdProducto(desc))
                cantidad.append(cant)
                subtotal.append(sub)

            #Ingresa la factura
            #--Saca el sub-monto
            for index in subtotal:
                sub_monto += index

            #--Saca el monto general
            for index,element in enumerate(subtotal):
                if productoTieneIva(id_producto[index]):
                    nuevoPrecio = sacarIva(element)   
                    monto_general += nuevoPrecio
                    total_general.append(nuevoPrecio)                     
                else:                   
                    monto_general += element
                    total_general.append(element)        

            from datetime import date

            cliente = Cliente.objects.get(cedula=cedula)
            iva = ivaActual('objeto')
            factura = Factura(cliente=cliente,fecha=date.today(),sub_monto=sub_monto,monto_general=monto_general,iva=iva)

            factura.save()
            id_factura = factura

            for indice,elemento in enumerate(id_producto):
                objetoProducto = obtenerProducto(elemento)
                cantidadDetalle = cantidad[indice]
                subDetalle = subtotal[indice]
                totalDetalle = total_general[indice]

                detalleFactura = DetalleFactura(id_factura=id_factura,id_producto=objetoProducto,cantidad=cantidadDetalle
                    ,sub_total=subDetalle,total=totalDetalle)

                objetoProducto.disponible -= cantidadDetalle
                objetoProducto.save()

                detalleFactura.save()  

                # Registrar movimiento en Kardex (NUEVO)
                Kardex.registrar_movimiento(
                    producto=objetoProducto,
                    tipo_movimiento='SALIDA',
                    cantidad=cantidadDetalle,
                    valor_unitario=subDetalle / cantidadDetalle,
                    detalle=f'Venta - Factura #{id_factura.id}'
                )

            messages.success(request, 'Factura de ID %s insertada exitosamente.' % id_factura.id)
            return HttpResponseRedirect("/inventario/emitirFactura")    
        else:
            # Si el formset no es válido, se podría manejar el error aquí
            # Por ejemplo, redirigir de vuelta al formulario con un mensaje de error
            messages.error(request, 'Error al procesar la factura. Por favor, revise los datos.')
            return HttpResponseRedirect("/inventario/emitirFactura")
    
#Fin de vista-----------------------------------------------------------------------------------#


#Muestra y procesa los detalles de cada producto de la factura--------------------------------#
class ListarFacturas(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        #Lista de productos de la BDD
        facturas = Factura.objects.all()
        #Crea el paginador
                               
        contexto = {'tabla': facturas}
        contexto = complementarContexto(contexto,request.user) 

        return render(request, 'inventario/factura/listarFacturas.html', contexto)        

#Fin de vista---------------------------------------------------------------------------------------#     


#Muestra los detalles individuales de una factura------------------------------------------------#
class VerFactura(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, p):
        factura = Factura.objects.get(id=p)
        detalles = DetalleFactura.objects.filter(id_factura_id=p)
        contexto = {'factura':factura, 'detalles':detalles}
        contexto = complementarContexto(contexto,request.user)     
        return render(request, 'inventario/factura/verFactura.html', contexto)
#Fin de vista--------------------------------------------------------------------------------------#   


#Genera la factura en CSV--------------------------------------------------------------------------#
class GenerarFactura(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, p):
        import csv

        factura = Factura.objects.get(id=p)
        detalles = DetalleFactura.objects.filter(id_factura_id=p) 

        nombre_factura = "factura_%s.csv" % (factura.id)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % nombre_factura
        writer = csv.writer(response)

        writer.writerow(['Producto', 'Cantidad', 'Sub-total', 'Total',
         'Porcentaje IVA utilizado: %s' % (factura.iva.valor_iva)])

        for producto in detalles:            
            writer.writerow([producto.id_producto.descripcion,producto.cantidad,producto.sub_total,producto.total])

        writer.writerow(['Total general:','','', factura.monto_general])

        return response

        #Fin de vista--------------------------------------------------------------------------------------#


#Genera la factura en PDF--------------------------------------------------------------------------#
class GenerarFacturaPDF(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, p):
        import io
        from reportlab.pdfgen import canvas
        import datetime

        factura = Factura.objects.get(id=p)
        general = Opciones.objects.get(id=1)
        detalles = DetalleFactura.objects.filter(id_factura_id=p)          

        data = {
             'fecha': factura.fecha, 
             'monto_general': factura.monto_general,
            'nombre_cliente': factura.cliente.nombre + " " + factura.cliente.apellido,
            'cedula_cliente': factura.cliente.cedula,
            'id_reporte': factura.id,
            'iva': factura.iva.valor_iva,
            'detalles': detalles,
            'modo': 'factura',
            'general':general
        }

        nombre_factura = "factura_%s.pdf" % (factura.id)

        pdf = render_to_pdf('inventario/PDF/prueba.html', data)
        response = HttpResponse(pdf,content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % nombre_factura

        return response  

        #Fin de vista--------------------------------------------------------------------------------------#


#Crea una lista de los clientes, 10 por pagina----------------------------------------#
class ListarProveedores(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        #Saca una lista de todos los clientes de la BDD
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

            ruc = form.cleaned_data['ruc']
            tipoCedula = form.cleaned_data['tipoCedula']
            cedula = form.cleaned_data['cedula']
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            ciudad = form.cleaned_data['ciudad']
            direccion = form.cleaned_data['direccion']
            telefono = form.cleaned_data['telefono']
            correo = form.cleaned_data['correo']
            telefono2 = form.cleaned_data['telefono2']
            correo2 = form.cleaned_data['correo2']

            proveedor = Proveedor(
                ruc=ruc,cedula=cedula,tipoCedula=tipoCedula,nombre=nombre,apellido=apellido,
                ciudad=ciudad,direccion=direccion,telefono=telefono,
                correo=correo,telefono2=telefono2,correo2=correo2)
            proveedor.save()
            form = ProveedorFormulario()

            messages.success(request, 'Ingresado exitosamente bajo la ID %s.' % proveedor.id)
            request.session['proveedorProcesado'] = 'agregado'
            return HttpResponseRedirect("/inventario/agregarProveedor")
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/proveedor/agregarProveedor.html', {'form': form})

    def get(self,request):
        form = ProveedorFormulario()
        #Envia al usuario el formulario para que lo llene
        contexto = {'form':form , 'modo':request.session.get('proveedorProcesado')}
        contexto = complementarContexto(contexto,request.user)
        return render(request, 'inventario/proveedor/agregarProveedor.html', contexto)
#Fin de vista-----------------------------------------------------------------------------#

#Formulario simple que procesa un script para importar los proveedores-----------------#
class ImportarProveedores(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request):
        form = ImportarClientesFormulario(request.POST)
        if form.is_valid():
            request.session['clientesImportados'] = True
            return HttpResponseRedirect("/inventario/importarClientes")

    def get(self,request):
        form = ImportarClientesFormulario()

        if request.session.get('clientesImportados') == True:
            importado = request.session.get('clientesImportados')
            contexto = { 'form':form,'clientesImportados': importado  }
            request.session['clientesImportados'] = False

        else:
            contexto = {'form':form}
            contexto = complementarContexto(contexto,request.user)             
        return render(request, 'inventario/importarClientes.html',contexto)
#Fin de vista-------------------------------------------------------------------------#




#Formulario simple que crea un archivo y respalda los proveedores-----------------------#
class ExportarProveedores(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request):
        form = ExportarClientesFormulario(request.POST)
        if form.is_valid():
            request.session['clientesExportados'] = True


            #Se obtienen las entradas de producto en formato JSON
            data = serializers.serialize("json", Cliente.objects.all())
            fs = FileSystemStorage('inventario/tmp/')

            #Se utiliza la variable fs para acceder a la carpeta con mas facilidad
            with fs.open("clientes.json", "w") as out:
                out.write(data)
                out.close()  

            with fs.open("clientes.json", "r") as out:                 
                response = HttpResponse(out.read(), content_type="application/force-download")
                response['Content-Disposition'] = 'attachment; filename="clientes.json"'
                out.close() 
            #------------------------------------------------------------
            return response

    def get(self,request):
        form = ExportarClientesFormulario()

        if request.session.get('clientesExportados') == True:
            exportado = request.session.get('clientesExportados')
            contexto = { 'form':form,'clientesExportados': exportado  }
            request.session['clientesExportados'] = False

        else:
            contexto = {'form':form}
            contexto = complementarContexto(contexto,request.user) 
        return render(request, 'inventario/exportarClientes.html',contexto)
#Fin de vista-------------------------------------------------------------------------#




#Muestra el mismo formulario del cliente pero con los datos a editar----------------------#
class EditarProveedor(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self,request,p):
        # Crea una instancia del formulario y la llena con los datos:
        proveedor = Proveedor.objects.get(id=p)
        form = ProveedorFormulario(request.POST, instance=proveedor)
        # Revisa si es valido:

        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            ruc = form.cleaned_data['ruc']
            cedula = form.cleaned_data['cedula']
            tipoCedula = form.cleaned_data['tipoCedula']
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            direccion = form.cleaned_data['direccion']
            telefono = form.cleaned_data['telefono']
            correo = form.cleaned_data['correo']
            telefono2 = form.cleaned_data['telefono2']
            correo2 = form.cleaned_data['correo2']

            proveedor.ruc = ruc
            proveedor.cedula = cedula
            proveedor.tipoCedula = tipoCedula
            proveedor.nombre = nombre
            proveedor.apellido = apellido
            proveedor.direccion = direccion
            proveedor.telefono = telefono
            proveedor.correo = correo
            proveedor.telefono2 = telefono2
            proveedor.correo2 = correo2
            proveedor.save()
            form = ProveedorFormulario(instance=proveedor)

            messages.success(request, 'Actualizado exitosamente el proveedor de ID %s.' % p)
            request.session['proveedorProcesado'] = 'editado'
            return HttpResponseRedirect("/inventario/editarProveedor/%s" % proveedor.id)
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/proveedor/agregarProveedor.html', {'form': form})

    def get(self, request,p):
        proveedor = Proveedor.objects.get(id=p)
        form = ProveedorFormulario(instance=proveedor)
        #Envia al usuario el formulario para que lo llene
        contexto = {'form':form , 'modo':request.session.get('proveedorProcesado'),'editar':True}
        contexto = complementarContexto(contexto,request.user)
        return render(request, 'inventario/proveedor/agregarProveedor.html', contexto)
#Fin de vista--------------------------------------------------------------------------------#


#Agrega un pedido-----------------------------------------------------------------------------------#
class AgregarPedido(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        cedulas = Proveedor.cedulasRegistradas()
        missing = False
        if cedulas is None:
            missing = True
        else:
            missing = len(cedulas) == 0
        form = EmitirPedidoFormulario(cedulas=cedulas)
        contexto = {'form':form, 'missing':missing}
        contexto = complementarContexto(contexto,request.user)
        return render(request, 'inventario/pedido/emitirPedido.html', contexto)

    def post(self, request):
        # Crea una instancia del formulario y la llena con los datos:
        cedulas = Proveedor.cedulasRegistradas()
        form = EmitirPedidoFormulario(request.POST,cedulas=cedulas)
        # Revisa si es valido:
        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            request.session['form_details'] = form.cleaned_data['productos']
            request.session['id_proveedor'] = form.cleaned_data['proveedor']
            return HttpResponseRedirect("detallesPedido")
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/pedido/emitirPedido.html', {'form': form})

#--------------------------------------------------------------------------------------------------#



#Lista todos los pedidos---------------------------------------------------------------------------# 
class ListarPedidos(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        from django.db import models
        #Saca una lista de todos los clientes de la BDD
        pedidos = Pedido.objects.all()
        contexto = {'tabla': pedidos}
        contexto = complementarContexto(contexto,request.user)         

        return render(request, 'inventario/pedido/listarPedidos.html',contexto) 

#------------------------------------------------------------------------------------------------#


#Muestra y procesa los detalles de cada producto de la factura--------------------------------#
class DetallesPedido(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        cedula = request.session.get('id_proveedor')
        productos = request.session.get('form_details')
        PedidoFormulario = formset_factory(DetallesPedidoFormulario, extra=productos)
        formset = PedidoFormulario()
        contexto = {'formset':formset}
        contexto = complementarContexto(contexto,request.user)

        return render(request, 'inventario/pedido/detallesPedido.html', contexto)

    def post(self, request):
        cedula = request.session.get('id_proveedor')
        productos = request.session.get('form_details')

        PedidoFormulario = formset_factory(DetallesPedidoFormulario, extra=productos)

        inicial = {
        'descripcion':'',
        'cantidad': 0,
        'subtotal':0,
        }

        data = {
            'form-TOTAL_FORMS': productos,
            'form-INITIAL_FORMS':0,
            'form-MAX_NUM_FORMS': '',
        }

        formset = PedidoFormulario(request.POST,data)

        if formset.is_valid():

            id_producto = []
            cantidad = []
            subtotal = []
            total_general = []
            sub_monto = 0
            monto_general = 0

            for form in formset:
                desc = form.cleaned_data['descripcion'].descripcion
                cant = form.cleaned_data['cantidad']
                sub = form.cleaned_data['valor_subtotal']

                id_producto.append(obtenerIdProducto(desc)) #esta funcion, a estas alturas, es innecesaria porque ya tienes la id
                cantidad.append(cant)
                subtotal.append(sub)

            #Ingresa la factura
            #--Saca el sub-monto
            for index in subtotal:
                sub_monto += index

            #--Saca el monto general
            for index,element in enumerate(subtotal):
                if productoTieneIva(id_producto[index]):
                    nuevoPrecio = sacarIva(element)
                    monto_general += nuevoPrecio
                    total_general.append(nuevoPrecio)
                else:
                    monto_general += element
                    total_general.append(element)

            from datetime import date

            proveedor = Proveedor.objects.get(cedula=cedula)
            iva = ivaActual('objeto')
            presente = False
            pedido = Pedido(proveedor=proveedor,fecha=date.today(),sub_monto=sub_monto,monto_general=monto_general,iva=iva,
                presente=presente)

            pedido.save()
            id_pedido = pedido

            for indice,elemento in enumerate(id_producto):
                objetoProducto = obtenerProducto(elemento)
                cantidadDetalle = cantidad[indice]
                subDetalle = subtotal[indice]
                totalDetalle = total_general[indice]

                detallePedido = DetallePedido(id_pedido=id_pedido,id_producto=objetoProducto,cantidad=cantidadDetalle
                    ,sub_total=subDetalle,total=totalDetalle)
                detallePedido.save()


            messages.success(request, 'Pedido de ID %s insertado exitosamente.' % id_pedido.id)
            return HttpResponseRedirect("/inventario/agregarPedido")
#Fin de vista-----------------------------------------------------------------------------------#

#Muestra los detalles individuales de un pedido------------------------------------------------#
class VerPedido(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, p):
        pedido = Pedido.objects.get(id=p)
        detalles = DetallePedido.objects.filter(id_pedido_id=p)
        recibido = Pedido.recibido(p)
        contexto = {'pedido':pedido, 'detalles':detalles,'recibido': recibido}
        contexto = complementarContexto(contexto,request.user)     
        return render(request, 'inventario/pedido/verPedido.html', contexto)
#Fin de vista--------------------------------------------------------------------------------------#   

#Valida un pedido ya insertado------------------------------------------------#
class ValidarPedido(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, p):
        pedido = Pedido.objects.get(id=p)
        detalles = DetallePedido.objects.filter(id_pedido_id=p)

        #Agrega los productos del pedido
        for elemento in detalles:
            elemento.id_producto.disponible += elemento.cantidad
            elemento.id_producto.save()

        pedido.presente = True
        pedido.save()
        messages.success(request, 'Pedido de ID %s verificado exitosamente.' % pedido.id)     
        return HttpResponseRedirect("/inventario/verPedido/%s" % p) 
#Fin de vista--------------------------------------------------------------------------------------#   


#Genera el pedido en CSV--------------------------------------------------------------------------#
class GenerarPedido(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, p):
        import csv

        pedido = Pedido.objects.get(id=p)
        detalles = DetallePedido.objects.filter(id_pedido_id=p) 

        nombre_pedido = "pedido_%s.csv" % (pedido.id)

        response = HttpResponse(content_type='text/csv')

        response['Content-Disposition'] = 'attachment; filename="%s"' % nombre_pedido
        writer = csv.writer(response)

        writer.writerow(['Producto', 'Cantidad', 'Sub-total', 'Total',
         'Porcentaje IVA utilizado: %s' % (pedido.iva.valor_iva)])

        for producto in detalles:            
            writer.writerow([producto.id_producto.descripcion,producto.cantidad,producto.sub_total,producto.total])

        writer.writerow(['Total general:','','', pedido.monto_general])

        return response

        #Fin de vista--------------------------------------------------------------------------------------#




#Genera el pedido en PDF--------------------------------------------------------------------------#
class GenerarPedidoPDF(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, p):

        pedido = Pedido.objects.get(id=p)
        general = Opciones.objects.get(id=1)
        detalles = DetallePedido.objects.filter(id_pedido_id=p)


        data = {
             'fecha': pedido.fecha, 
             'monto_general': pedido.monto_general,
            'nombre_proveedor': pedido.proveedor.nombre + " " + pedido.proveedor.apellido,
            'cedula_proveedor': pedido.proveedor.cedula,
            'id_reporte': pedido.id,
            'iva': pedido.iva.valor_iva,
            'detalles': detalles,
            'modo' : 'pedido',
            'general': general
        }

        nombre_pedido = "pedido_%s.pdf" % (pedido.id)

        pdf = render_to_pdf('inventario/PDF/prueba.html', data)
        response = HttpResponse(pdf,content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % nombre_pedido

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
        # Se asegura de que el directorio exista
        if not path.exists('inventario/archivos/tmp/'):
            makedirs('inventario/archivos/tmp/')

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
                manejarArchivo(imagen,'inventario/static/inventario/assets/logo/logo2.png')

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

        if pagina == 'pedido':
            return render(request, 'inventario/manual/pedido.html') 

        if pagina == 'clientes':
            return render(request, 'inventario/manual/clientes.html') 

        if pagina == 'factura':
            return render(request, 'inventario/manual/factura.html') 

        if pagina == 'usuarios':
            return render(request, 'inventario/manual/usuarios.html')

        if pagina == 'opciones':
            return render(request, 'inventario/manual/opciones.html')



#Fin de vista--------------------------------------------------------------------------------

#Vistas para el Kardex------------------------------------------------------------------------

# Vistas para el Kardex------------------------------------------------------------------------

class ListaProductosView(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        productos = Producto.objects.all().order_by('descripcion')
        contexto = {
            'productos': productos,
            'usuario': request.user.username,
            'id_usuario': request.user.id
        }
        return render(request, 'inventario/kardex/lista_productos.html', contexto)

class DetalleKardexView(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, producto_id):
        producto = get_object_or_404(Producto, id=producto_id)
        movimientos = Kardex.objects.filter(producto=producto).order_by('-fecha')

        paginator = Paginator(movimientos, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        contexto = {
            'producto': producto,
            'page_obj': page_obj,
            'usuario': request.user.username,
            'id_usuario': request.user.id
        }
        return render(request, 'inventario/kardex/detalle_kardex.html', contexto)

class ResumenKardexView(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, producto_id):
        producto = get_object_or_404(Producto, id=producto_id)
        ultimo_movimiento = Kardex.objects.filter(producto=producto).order_by('-fecha').first()

        entradas = Kardex.objects.filter(producto=producto, tipo_movimiento='ENTRADA').aggregate(
            total_cantidad=Sum('cantidad'),
            total_valor=Sum('valor_total')
        )

        salidas = Kardex.objects.filter(producto=producto, tipo_movimiento='SALIDA').aggregate(
            total_cantidad=Sum('cantidad'),
            total_valor=Sum('valor_total')
        )

        contexto = {
            'producto': producto,
            'ultimo_movimiento': ultimo_movimiento,
            'entradas': entradas,
            'salidas': salidas,
            'usuario': request.user.username,
            'id_usuario': request.user.id
        }
        return render(request, 'inventario/kardex/resumen_kardex.html', contexto)

class RegistrarMovimientoView(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    @method_decorator(require_POST)
    def post(self, request, producto_id):
        producto = get_object_or_404(Producto, id=producto_id)
        form = KardexForm(request.POST)

        if form.is_valid():
            kardex = form.save(commit=False)
            kardex.producto = producto
            kardex.valor_total = kardex.cantidad * kardex.valor_unitario

            # Asignar valores a los campos saldo_cantidad y saldo_valor_total
            kardex.saldo_cantidad = kardex.cantidad  # Ajusta esto según tu lógica de negocio
            kardex.saldo_valor_total = kardex.valor_total  # Ajusta esto según tu lógica de negocio

            try:
                kardex.save()
                return redirect('inventario:detalle_kardex', producto_id=producto.id)
            except ValidationError as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Error al guardar el movimiento: {str(e)}'}, status=400)
        else:
            return JsonResponse({'status': 'error', 'message': 'Error en la validación del formulario', 'errors': form.errors}, status=400)

class NuevoMovimientoView(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, producto_id):
        producto = get_object_or_404(Producto, id=producto_id)
        form = KardexForm()
        contexto = {
            'form': form,
            'producto': producto,
            'usuario': request.user.username,
            'id_usuario': request.user.id
        }
        return render(request, 'inventario/kardex/nuevo_movimiento.html', contexto)

# Fin de vistas--------------------------------------------------------------------------------