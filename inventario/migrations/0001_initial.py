# Generated by Django 5.0.7 on 2024-07-31 16:21

import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipoCedula', models.CharField(choices=[('C', 'Cédula de Identidad'), ('P', 'Pasaporte'), ('E', 'Cédula de Identidad para Extranjeros')], default='C', max_length=1)),
                ('cedula', models.CharField(max_length=10, unique=True)),
                ('nombre', models.CharField(max_length=40)),
                ('apellido', models.CharField(max_length=60)),
                ('ciudad', models.CharField(max_length=100, null=True)),
                ('direccion', models.CharField(max_length=200)),
                ('telefono', models.CharField(max_length=20)),
                ('telefono2', models.CharField(max_length=20, null=True)),
                ('correo', models.CharField(max_length=100)),
                ('correo2', models.CharField(max_length=100, null=True)),
                ('genero', models.CharField(choices=[('1', 'Masculino'), ('2', 'Femenino'), ('3', 'Otro')], default='1', max_length=20)),
                ('nacimiento', models.DateField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Opciones',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('moneda', models.CharField(max_length=20, null=True)),
                ('valor_iva', models.IntegerField(unique=True)),
                ('nombre_negocio', models.CharField(max_length=25, null=True)),
                ('mensaje_factura', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipoCedula', models.CharField(choices=[('C', 'Cédula de Identidad'), ('P', 'Pasaporte'), ('E', 'Cédula de Identidad para Extranjeros')], default='C', max_length=1)),
                ('cedula', models.CharField(max_length=10, unique=True)),
                ('nombre', models.CharField(max_length=40)),
                ('apellido', models.CharField(max_length=60)),
                ('ciudad', models.CharField(max_length=100, null=True)),
                ('direccion', models.CharField(max_length=200)),
                ('telefono', models.CharField(max_length=20)),
                ('telefono2', models.CharField(max_length=20, null=True)),
                ('correo', models.CharField(max_length=100)),
                ('correo2', models.CharField(max_length=100, null=True)),
                ('ruc', models.CharField(max_length=13, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=80, unique=True)),
                ('password', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('first_name', models.CharField(max_length=40)),
                ('last_name', models.CharField(max_length=60)),
                ('nivel', models.IntegerField(null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Factura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('sub_monto', models.DecimalField(decimal_places=2, max_digits=20)),
                ('monto_general', models.DecimalField(decimal_places=2, max_digits=20)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.cliente', to_field='cedula')),
                ('iva', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.opciones', to_field='valor_iva')),
            ],
        ),
        migrations.CreateModel(
            name='Notificaciones',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mensaje', models.TextField()),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('sub_monto', models.DecimalField(decimal_places=2, max_digits=20)),
                ('monto_general', models.DecimalField(decimal_places=2, max_digits=20)),
                ('presente', models.BooleanField(null=True)),
                ('iva', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.opciones', to_field='valor_iva')),
                ('proveedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.proveedor')),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=40)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=9)),
                ('disponible', models.IntegerField(null=True)),
                ('medida', models.CharField(choices=[('1', 'Unidad'), ('2', 'Kilo'), ('3', 'Litro'), ('4', 'Otros')], default='1', max_length=20)),
                ('tiene_iva', models.BooleanField(null=True)),
                ('stock_actual', models.IntegerField(default=0)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.categoria')),
            ],
        ),
        migrations.CreateModel(
            name='Kardex',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(auto_now_add=True)),
                ('tipo_movimiento', models.CharField(choices=[('ENTRADA', 'Entrada'), ('SALIDA', 'Salida')], max_length=10)),
                ('cantidad', models.IntegerField()),
                ('valor_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('valor_total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('saldo_cantidad', models.IntegerField()),
                ('saldo_valor_total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('detalle', models.CharField(max_length=200)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.producto')),
            ],
        ),
        migrations.CreateModel(
            name='DetallePedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('sub_total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('id_pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.pedido')),
                ('id_producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.producto')),
            ],
        ),
        migrations.CreateModel(
            name='DetalleFactura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('sub_total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('id_factura', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.factura')),
                ('id_producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.producto')),
            ],
        ),
    ]
