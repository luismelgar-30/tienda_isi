import bcrypt

# Contraseña ingresada (la que se usa para hacer login)
password = "12345678"  # La contraseña que intentas verificar
stored_hash = "$2b$12$TjOcHtQJgsmn4ievPmZPFOzubW/rY9Pf6pTWglGpIjD..."  # El hash que tienes en la base de datos

# Verificación de la contraseña con el hash almacenado
if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
    print("Contraseña correcta.")
else:
    print("Contraseña incorrecta.")