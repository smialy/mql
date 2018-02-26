from mql.common import errors, execution


class Source:
    def __init__(self, name, executor, schema):
        self._name = name
        self._executor = executor
        self._schema = schema

    @property
    def name(self):
        return self._name

    @property
    def schema(self):
        return self._schema

    def match(self, ast_document):
        return self._schema.match(ast_document)

    async def execute(self, context):
        try:
            return await self._executor.execute(context)
        except Exception as ex:
            return execution.ExecuteResult(errors=[ex])
