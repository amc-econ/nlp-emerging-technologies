import tempfile
import pandas as pd

def read_sql_tmpfile(query, db_engine):
        
    """
    Snippet to speed up large SQL queries by loading them in a temporary file
    Taken from: https://gist.github.com/thcrock/b9ac0e2fb822d5ac5b506af13c755134
    """
        
    with tempfile.TemporaryFile() as tmpfile:
        copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(query=query, head="HEADER")
        conn = db_engine.raw_connection()
        cur = conn.cursor()
        cur.copy_expert(copy_sql, tmpfile)
        tmpfile.seek(0)
        df = pd.read_csv(tmpfile, low_memory=False)
        return df