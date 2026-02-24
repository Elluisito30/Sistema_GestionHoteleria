# test_neon.py
import psycopg2

print("🔍 Probando conexión a Neon con nueva contraseña...")

try:
    conn = psycopg2.connect(
        host="ep-mute-pond-aic2jswt-pooler.c-4.us-east-1.aws.neon.tech",
        port="5432",
        database="neondb",
        user="neondb_owner",
        password="npg_bqMBQag6xsR0",
        sslmode='require'
    )
    print("✅ CONEXIÓN EXITOSA A NEON!")
    
    # Verificar tablas
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    tables = cur.fetchall()
    
    if tables:
        print("📋 Tablas encontradas:")
        for table in tables:
            print(f"   - {table[0]}")
    else:
        print("⚠️ No hay tablas. Debes ejecutar schema.sql")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ ERROR: {e}")