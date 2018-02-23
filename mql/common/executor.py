

class Executor:
    def __init__(self, name, engine):
        self.name = name
        self.engine = engine

    def match(self, name):
        return self.name == name

    async def execute(self, ast_stmt, params):
        return await self.engine.execute(ast_stmt, params)
