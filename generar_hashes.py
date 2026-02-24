import bcrypt

# Diccionario con usuarios y sus contraseñas
credenciales = {
    'admin': 'adminSistema',
    'gerente': 'gerenteSistema',
    'recepcionista1': 'recepcionista1Sistema'
}

print("\n" + "="*70)
print("HASHES GENERADOS CON BCRYPT (rounds=12)")
print("="*70 + "\n")

for usuario, password in credenciales.items():
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
    
    print(f"-- Usuario: {usuario.upper()} | Contraseña: {password}")
    print(f"UPDATE usuarios SET password_hash = '{hashed.decode()}' WHERE username = '{usuario}';")
    print()

print("="*70)
print("✅ Copia los UPDATE y ejecútalos en tu base de datos PostgreSQL")
print("="*70 + "\n")