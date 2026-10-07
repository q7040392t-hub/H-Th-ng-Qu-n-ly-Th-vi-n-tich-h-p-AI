from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parent/'.env')
import database as db
ok,msg=db.test_connection()
print('Database:',db.connection_info())
print(msg)
raise SystemExit(0 if ok else 1)
