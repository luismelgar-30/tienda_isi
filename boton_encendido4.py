import concurrent.futures
import subprocess

scripts = [

    'boton_encendido5.py',
    'app_mantenimiento.py',
    'app_proveedores.py',
    'app_devolucion_ventas.py',
    'app_sar.py',
    'app_factu.py',
    'app_login.py',
    'app_usuarios.py',

]

def run_script(script):
    subprocess.call(['python', script])

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(run_script, scripts)