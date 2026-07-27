import psycopg
from db.config import DB_CONFIG

conn = psycopg.connect(**DB_CONFIG)
cursor = conn.cursor()
print("Database connected successfully!")
