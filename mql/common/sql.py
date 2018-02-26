
import abc


class IConnection(abc.ABC):

    @abc.abstractmethod
    async def execute(self, query:str, args=None, timeout:float=None):
        pass

    @abc.abstractmethod
    async def execute_many(self, command:str, args=None, *, timeout:float=None):
        '''>>> await con.executemany("""
            ...     INSERT INTO mytab (a) VALUES ($1, $2, $3);
            ... """, [(1, 2, 3), (4, 5, 6)])
        '''

    @abc.abstractmethod
    async def fetch(self, query, args=None, timeout:float=None):
        pass

    @abc.abstractmethod
    async def fetch_one(self, query, args=None, timeout=None):
        pass

    @abc.abstractmethod
    async def fetch_col(self, query, args=None, column=0, timeout=None):
        pass

    @abc.abstractmethod
    async def findone(self, table, filters, fields=None):
        pass

    @abc.abstractmethod
    async def find(self, table, filters=None, fields=None):
        pass

    @abc.abstractmethod
    async def insert(self, table, data, returning='id'):
        pass

    @abc.abstractmethod
    async def delete(self, table, filters):
        pass

    @abc.abstractmethod
    async def update(self, table, filters, data):
        pass


class IConnection:
    async def _execute(self, sql, params=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, params)
                return cur

    async def fetch(self, sql, params=None):
        cur = await self._execute(sql, params)
        async for row in cur:
            yield row

    async def fetch_all(self, sql, params=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, params)
                return await cur.fetchall()

    async def fetch_one(self, pool, sql, params=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, params)
                return await cur.fetchone()

    async def findone(self, table, filters, fields=None):
        query, values = sql.findone_sql(table, filters, fields)
        return await self.engine.fetchone(query, values)

    async def find(self, table, filters=None, fields=None):
        query, values = sql.find_sql(table, filters, fields)
        return await self.engine.fetch(query, values)

    async def insert(self, table, data, returning='id'):
        query, values = sql.insert_sql(table, data, returning)
        return await conn.fetchval(query, values)

    async def delete(self, table, filters):
        query, values = sql.delete_sql(table, filters)
        return await self.engine.execute(query, values)

    async def update(self, table, filters, data):
        query, values = sql.update_sql(table, filters, data)
        return await self.engine.execute(query, values)



