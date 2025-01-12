import concurrent.futures
import subprocess

scripts = [
    
    'boton_encendido4.py',
    'app_empleados.py',
    'app_equipo.py',
    'app_factura.py',
    'app_promocion.py',
    'app_puesto_de_trabajo.py',
    'app_sucursales.py',
    'app_transportistas.py',
    'app_distribucion.py',
    
]

def run_script(script):
    subprocess.call(['python', script])

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(run_script, scripts)