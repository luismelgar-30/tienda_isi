import concurrent.futures
import subprocess

scripts = [
    
    'boton_encendido3.py',
    'app_impuesto.py', 
    'app_inventario_almacenes.py',
    'app_inventario.py',
    'app_pedido.py',
    'app_pedidos_compra_p.py',
    'app_producto.py',
    
    
]

def run_script(script):
    subprocess.call(['python', script])

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(run_script, scripts)