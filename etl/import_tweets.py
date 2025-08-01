# etl/import_tweets.py
import csv, os, glob
import psycopg2
from psycopg2.extras import execute_values

DSN = "dbname=liardb user=liar password=liarpass host=localhost port=5432"

def ingest_csv(path):
    conn = psycopg2.connect(DSN)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS tweets(
        id BIGINT PRIMARY KEY,
        created_at TIMESTAMP,
        text TEXT,
        favorite_count INT,
        retweet_count INT,
        source_file TEXT
    )""")
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [
            (int(r['id']), r['created_at'], r['text'],
             int(r.get('favorite_count',0)), int(r.get('retweet_count',0)), os.path.basename(path))
            for r in reader
        ]
    execute_values(
        cur,
        "INSERT INTO tweets VALUES %s ON CONFLICT (id) DO NOTHING",
        rows
    )
    conn.commit()
    conn.close()
    print(f"✓ {path} → {len(rows)} lignes")

if __name__ == "__main__":
    for file in glob.glob("datasets/*.csv"):
        ingest_csv(file)
