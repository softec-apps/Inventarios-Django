# Inventario Django
Sistema de inventario y facturación hecho con Django/ Stock and bill system made with Django

El sistema permite realizar operaciones básicas de inventario y facturación:

-Productos, clientes, proveedores, pedidos

-Reportes de facturas en PDF Y CSV

-Ingreso de usuarios en varios niveles

-Cambio de IVA y otras opciones generales

Se puede correr en local fácilmente usando el comando ```python manage.py runserver``` dentro de la carpeta raíz

Username: admin
Contraseña: admin


# Creación del entorno virtual
Ejecutar el siguiente comando para crear un entorno virtual para la instalación de dependencias
```python
python3 -m venv .venv
```
> Importante: Tener la versión 3 de Python instalada y el modulo de virtualenvironment


# Dependencias (con sus versiones):
Todas las dependencias con sus versiones se encuentran en el archivo ***requirements.txt***.
Con el entorno virtual activado ejecutar el comando:
```bash
pip install -r requirements.txt
```


# Preparación del proyecto
1. Comentar la linea de importación de bidi en la ruta .venv/lib/python3.[YOURVERS]/site-packages/xhtml2pdf/util.py
```python
#from bidi.algorithm import get_display
```
2. Configurar SECRET_KEY en el archivo ***.env***:
Copie el archivo de ejemplo y cambie los valores correspondientes.
> Puede generar una clave secreta desde el terminal de python accediendo a el desde la terminal con el comando ***python3***
```python
# Puede generar una clave secreta desde el terminal de python
import secrets
print(secrets.token_urlsafe())
```
3. Preparar las migraciones
```python
python manage.py makemigrations
```
4. Migrar la DB (por default SQLITE3)
```python
python manage.py migrate
```