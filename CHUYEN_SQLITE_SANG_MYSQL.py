import os, sqlite3
from pathlib import Path
from dotenv import load_dotenv
BASE=Path(__file__).resolve().parent
load_dotenv(BASE/'.env')
if os.getenv('DB_ENGINE','mysql').lower()!='mysql': raise SystemExit('DB_ENGINE phải là mysql')
import database as db
old=BASE/'library.db'
if not old.exists(): raise SystemExit('Không tìm thấy library.db')
db.init_db()
src=sqlite3.connect(old); src.row_factory=sqlite3.Row
tables=['users','books','loans','reservations','notifications','settings','fines','activity_logs','favorites','support_tickets']
with db.get_conn() as dst:
    dst.execute('SET FOREIGN_KEY_CHECKS=0')
    try:
        for table in tables:
            rows=src.execute(f'SELECT * FROM {table}').fetchall()
            if not rows: print(table,0); continue
            cols=list(rows[0].keys()); names=','.join(f'`{c}`' for c in cols); marks=','.join('?' for _ in cols)
            updates=','.join(f'`{c}`=VALUES(`{c}`)' for c in cols if c!='id')
            for row in rows:
                sql=f'INSERT INTO `{table}` ({names}) VALUES ({marks})'
                sql += (' ON DUPLICATE KEY UPDATE '+updates) if updates else ''
                dst.execute(sql,[row[c] for c in cols])
            print(table,len(rows))
    finally:
        dst.execute('SET FOREIGN_KEY_CHECKS=1')
src.close(); print('Hoàn tất chuyển SQLite -> MySQL')
