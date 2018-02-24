
class AiopgConnection:

    placeholder = 'percent'

    def __init__(self, pool):
        self.pool = pool

    async def execute(self, sql, params=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, params)
                return cur

    async def fetch(self, sql, params=None):
        cursor = await self.execute(sql, params)
        async for row in cursor:
            yield row

    async def fetchall(self, sql, params=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(sql, params)
                return await cursor.fetchall()

    async def fetchone(self, pool, sql, params=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(sql, params)
                return await cursor.fetchone()


class AsyncpgConnection:

    placeholder = 'number'

    def __init__(self, pool):
        self.pool = pool

    async def execute(self, query:str, params=None, timeout:float=None):
        async with self.pool.acquire() as conn:
            params = params or []
            return await conn.execute(query, *params, timeout)

    async def fetch(self, sql, params=None):
        params = params or []
        cur = await self.execute(sql, params)
        async for row in cur:
            yield row

    async def fetchall(self, query:str, params=None, timeout:float=None):
        async with self.pool.acquire() as conn:
            params = params or []
            return await conn.fetch(query, *params, timeout=timeout)

    async def fetchone(self, query:str, params=None, timeout:float=None):
        async with self.pool.acquire() as conn:
            params = params or []
            return await conn.fetchrow(query, *params, timeout=timeout)



