"""Genera hash bcrypt para las contraseñas de seeds"""
import bcrypt

password = b'password123'
hash_result = bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))
print("Hash para password123:")
print(hash_result.decode())
print("\nVerificación:", bcrypt.checkpw(password, hash_result))
