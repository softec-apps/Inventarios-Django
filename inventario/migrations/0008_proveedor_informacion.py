# Generated by Django 5.0.7 on 2024-09-20 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0007_producto_marcas_producto_tipos'),
    ]

    operations = [
        migrations.AddField(
            model_name='proveedor',
            name='informacion',
            field=models.TextField(blank=True, null=True),
        ),
    ]
