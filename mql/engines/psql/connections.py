
class AiopgConnection:
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
    def __init__(self, pool):
        self.pool = pool

    async def execute(self, query:str, args=None, timeout:float=None):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args, timeout)

    async def fetch(self, sql, params=None):
        cur = await self.execute(sql, params)
        async for row in cur:
            yield row

    async def fetchall(self, query:str, args=None, timeout:float=None):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args, timeout=timeout)

    async def fetchone(self, query:str, args=None, timeout:float=None):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args, timeout=timeout)



