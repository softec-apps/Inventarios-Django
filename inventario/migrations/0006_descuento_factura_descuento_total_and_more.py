# Generated by Django 5.0.7 on 2024-08-20 22:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0005_alter_producto_categoria'),
    ]

    operations = [
        migrations.CreateModel(
            name='Descuento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('valor', models.FloatField()),
            ],
        ),
        migrations.AddField(
            model_name='factura',
            name='descuento_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='producto',
            name='medida',
            field=models.CharField(choices=[('1', 'sacos'), ('2', 'kg'), ('3', 'lb')], default='1', max_length=20),
        ),
        migrations.AddField(
            model_name='factura',
            name='descuento',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventario.descuento'),
        ),
    ]
