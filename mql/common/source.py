from mql.common import errors, execution


class Source:
    def __init__(self, name, executor, schema):
        self.name = name
        self._executor = executor
        self._schema = schema

    def match(self, ast_document):
        return self._schema.match(ast_document)

    def describe(self):
        return self._schema.serialize()

    async def execute(self, context):
        try:
            return await self._executor.execute(context)
        except errors.MqlError as ex:
            return execution.ExecuteResult(errors=[ex])
        except Exception as ex:
            return execution.ExecuteResult(errors=[ex])

