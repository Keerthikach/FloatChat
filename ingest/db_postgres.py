import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_pg_connection():
    """
    Returns a psycopg2 connection, converting SQLAlchemy URL if needed.
    """
    if DATABASE_URL.startswith("postgresql+psycopg2://"):
        url = DATABASE_URL.replace("postgresql+psycopg2://", "")
        user_pass, host_db = url.split("@")
        user, password = user_pass.split(":")
        host_port, dbname = host_db.split("/")
        host, port = host_port.split(":")
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
    else:
        conn = psycopg2.connect(DATABASE_URL)
    return conn

def save_to_postgres_batch(records):
    """
    Inserts a batch of ARGO metadata records into argo_profiles.
    Each record should be a tuple:
    (entry_id, float_id, profile_time, lat, lon, variables, depth_range, source_file)
    Records with missing profile_time are skipped to respect NOT NULL constraint.
    """
    if not records:
        print("No records to insert.")
        return

    # Skip records with missing or invalid profile_time
    cleaned_records = []
    for rec in records:
        rec = list(rec)
        profile_time = rec[2]
        if profile_time is None or str(profile_time) == "NaT":
            continue  # skip invalid timestamps
        cleaned_records.append(tuple(rec))

    if not cleaned_records:
        print("No valid records to insert after filtering missing profile_time.")
        return

    query = """
    INSERT INTO argo_profiles (entry_id, float_id, profile_time, lat, lon, variables, depth_range, source_file)
    VALUES %s
    ON CONFLICT (entry_id) DO NOTHING;
    """

    try:
        conn = get_pg_connection()
        cur = conn.cursor()
        execute_values(cur, query, cleaned_records)
        conn.commit()
        cur.close()
        conn.close()
        print(f"Inserted {len(cleaned_records)} records successfully.")
    except Exception as e:
        print(f"❌ Error inserting records: {e}")
