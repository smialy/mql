

class Source:
    def __init__(self, name, executor, schema):
        self.name = name
        self.executor = executor
        self.schema = schema

    def match(self, ast_node):
        return self.schema.match(ast_node)

    def describe(self):
        return self.schema.serialize()

    async def execute(self, context):
        return await self.executor.execute(context)
