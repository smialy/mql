import re

from mql.common import errors, execution

from .generator import SqlGenerator
from .schema import load_schema

NOT_EXSITS_ERROR = re.compile(
    r'^(column|relation) "([a-z0-9_.]+)" does not exist$',
    re.IGNORECASE
)

SYNTAX_ERROR = re.compile(
    r'^syntax error at or near "([a-z0-9_.]+)"$',
    re.IGNORECASE
)

NOT_EXSITS_ERROR_2 = re.compile(
    r'^column "([a-z0-9_.]+)" of relation "([a-z0-9_.]+)" does not exist$',
    re.IGNORECASE
)


class PgsqlEngine:
    def __init__(self, connection):
        self.connection = connection
        self._transformers = []

    async def load_schema(self, name):
        return await load_schema(self.connection, name)

    async def execute(self, context):
        sql = self.build_sql(context.ast_document)
        try:
            print(sql, context.params)
            data = await self.connection.fetchall(sql, context.params)
            return execution.ExecuteResult(data[0][0], encoded=True)
        except Exception as ex:
            raise errors.MqlEngineError(*extract_error(ex)) from ex

    def build_sql(self, ast_document):
        generator = SqlGenerator(self.connection.placeholder)
        generator.visit(ast_document)
        return generator.to_sql()


def extract_error(exception):
    print(exception)
    line = str(exception).split('\n')[0].strip()
    result = NOT_EXSITS_ERROR.match(line)
    if result:
        kind, name = result.groups()
        kind = kind[0].upper() + kind[1:]
        return '{} "{}" does not exist'.format(kind, name), True
    result = NOT_EXSITS_ERROR_2.match(line)
    if result:
        name, ref = result.groups()
        return 'Column "{}" of relation "{}" does not exist'.format(name, ref), True
    result = SYNTAX_ERROR.match(line)
    if result:
        identifier = result.group(1)
        return 'Syntax error at or near "{}"'.format(identifier), True

    return str(exception), False
