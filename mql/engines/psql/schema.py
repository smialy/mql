import os
from pathlib import Path

from mql.common.schema import Schema


_sql_file = Path(__file__).parent / 'schema.sql'
with _sql_file.open() as f:
    SQL = f.read()


async def load_schema(connection):
    print('load_schema')
    schema = Schema()
    rows = await connection.fetchall(SQL)
    for row in rows:
        pass
        # if row['type'] == 'namespace':
            # schema.Database(dict())
    return schema