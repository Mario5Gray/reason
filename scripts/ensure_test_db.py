import psycopg

conn = psycopg.connect("postgresql://reason:reason@db:5432/reason")
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute("SELECT 1 FROM pg_database WHERE datname='reason_test'")
    exists = cur.fetchone()
    if not exists:
        cur.execute("CREATE DATABASE reason_test")
conn.close()
