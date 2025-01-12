import concurrent.futures
import subprocess

scripts = [
    'app_permisos.py',
    'app_pantallas.py',
    'app_roles.py',
    'app_distribucion',
]

def run_script(script):
    subprocess.call(['python', script])

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(run_script, scripts)