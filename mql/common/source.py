

class Source:
    def __init__(self, name, engine):
        self.name = name
        self.engine = engine

    def match(self, database_name):
        return self.name == database_name

    async def execute(self, ast_stmt, params):
        return await self.engine.execute(ast_stmt, params)
