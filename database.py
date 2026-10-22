import sqlite3
from pathlib import Path

DB_PATH=Path(__file__).parent/"sample_data.db"

def build_database():
    """Create deterministic synthetic data; no personal/customer data is used."""
    with sqlite3.connect(DB_PATH) as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS customers(customer_id INTEGER PRIMARY KEY, customer_name TEXT, city TEXT, signup_date TEXT);
        CREATE TABLE IF NOT EXISTS products(product_id INTEGER PRIMARY KEY, product_name TEXT, category TEXT, unit_price REAL, stock_quantity INTEGER);
        CREATE TABLE IF NOT EXISTS orders(order_id INTEGER PRIMARY KEY, customer_id INTEGER, order_date TEXT, status TEXT);
        CREATE TABLE IF NOT EXISTS order_items(order_item_id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity INTEGER, unit_price REAL);
        """)
        if con.execute("SELECT COUNT(*) FROM customers").fetchone()[0]==0:
            con.executemany("INSERT INTO customers VALUES(?,?,?,?)",[
                (1,"Aarav Sharma","Delhi","2024-02-11"),(2,"Meera Kapoor","Mumbai","2024-03-19"),(3,"Kabir Verma","Jaipur","2024-06-05"),
                (4,"Ananya Singh","Bengaluru","2024-08-22"),(5,"Rohan Mehta","Pune","2024-10-02"),(6,"Ishita Rao","Hyderabad","2025-01-14"),
                (7,"Dev Malhotra","Delhi","2025-03-09"),(8,"Sana Khan","Lucknow","2025-04-21"),(9,"Arjun Das","Kolkata","2025-06-12"),(10,"Tara Joshi","Chandigarh","2025-08-03")])
            con.executemany("INSERT INTO products VALUES(?,?,?,?,?)",[
                (1,"Wireless Mouse","Accessories",799,52),(2,"Mechanical Keyboard","Accessories",2499,18),(3,"USB-C Hub","Accessories",1799,24),
                (4,"Laptop Stand","Office",1299,13),(5,"Desk Lamp","Office",999,31),(6,"Notebook Set","Stationery",299,80),
                (7,"Gel Pen Pack","Stationery",149,120),(8,"Webcam HD","Electronics",3299,9),(9,"Bluetooth Speaker","Electronics",2199,16),(10,"Monitor 24-inch","Electronics",10999,7)])
            orders=[]
            dates=["2025-01-08","2025-01-20","2025-02-11","2025-02-28","2025-03-07","2025-03-19","2025-04-02","2025-04-18","2025-05-13","2025-05-26","2025-06-04","2025-06-22","2025-07-09","2025-07-25","2025-08-03","2025-08-19","2025-09-12","2025-09-28","2025-10-05","2025-10-23","2025-11-07","2025-11-21","2025-12-04","2025-12-16","2026-01-11","2026-02-08","2026-03-15","2026-04-01","2026-05-14","2026-06-02"]
            orders=[(i+1,(i%10)+1,d,"processing" if i==25 else "delivered") for i,d in enumerate(dates)]
            con.executemany("INSERT INTO orders VALUES(?,?,?,?)",orders)
            items=[]
            for i in range(30):
                order_id=i+1; product_id=(i%10)+1
                items.append((i+1,order_id,product_id,(i%4)+1,[799,2499,1799,1299,999,299,149,3299,2199,10999][product_id-1]))
            con.executemany("INSERT INTO order_items VALUES(?,?,?,?,?)",items)
        con.commit()
    return str(DB_PATH)

def get_schema(db_path=None):
    db_path=db_path or DB_PATH; result={}
    with sqlite3.connect(db_path) as con:
        tables=con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
        for (table,) in tables:
            result[table]=[(r[1],r[2] or "TEXT") for r in con.execute(f"PRAGMA table_info('{table}')").fetchall()]
    return result

def _authorizer(action,arg1,arg2,dbname,source):
    allowed={sqlite3.SQLITE_SELECT,sqlite3.SQLITE_READ,sqlite3.SQLITE_FUNCTION,sqlite3.SQLITE_RECURSIVE,sqlite3.SQLITE_TRANSACTION}
    return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY

def run_read_only_query(db_path,sql):
    cleaned=(sql or "").strip().rstrip(";").strip()
    if not cleaned: return {"ok":False,"error":"No SQL was generated.","columns":[],"rows":[]}
    if cleaned.split(None,1)[0].upper() not in {"SELECT","WITH"}:
        return {"ok":False,"error":"Read-only policy: only SELECT or WITH queries are allowed.","columns":[],"rows":[]}
    uri=Path(db_path).resolve().as_uri()+"?mode=ro"
    try:
        with sqlite3.connect(uri,uri=True,timeout=5) as con:
            con.set_authorizer(_authorizer)
            cur=con.execute(cleaned); rows=cur.fetchmany(501)
            if len(rows)>500: return {"ok":False,"error":"Result exceeded the 500-row safety limit. Add LIMIT.","columns":[],"rows":[]}
            return {"ok":True,"error":"","columns":[c[0] for c in (cur.description or [])],"rows":[tuple(r) for r in rows]}
    except Exception as e:
        return {"ok":False,"error":f"{type(e).__name__}: {e}","columns":[],"rows":[]}
