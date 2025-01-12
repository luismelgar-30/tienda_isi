import concurrent.futures
import subprocess

scripts = [
    
    'app_almacenes.py', 
    'boton_encendido2.py',
    'app_capacitacion.py',
    'app_categorias.py',
    'app_cliente.py',
    'app_detalle_p.py',
    'app_detalle.py',
    'app_devolucion_compra.py',
    
]

def run_script(script):
    subprocess.call(['python', script])

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(run_script, scripts)
