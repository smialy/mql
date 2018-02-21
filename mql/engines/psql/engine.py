import sys
import re
import traceback

from mql.common.errors import MqlEnginError
from .generator import SqlGenerator
from .schema import load_schema

NOT_EXSITS_ERROR = re.compile(
    r'^(column|relation) "([a-z0-9_.]+)" does not exist$', re.IGNORECASE)

SYNTAX_ERROR = re.compile(
    r'^syntax error at or near "([a-z0-9_.]+)"$', re.IGNORECASE)

class PgsqlEngine:
    def __init__(self, connection):
        self.connection = connection
        self._transformers = []

    async def load_schema(self):
        return await load_schema(self.connection)

    async def execute(self, ast_tree, params):
        sql = self.build_sql(ast_tree)
        try:
            print(sql, params)
            data = await self.connection.fetchall(sql, params)
            return data[0][0]
        except Exception as ex:
            raise MqlEnginError(*extract_error(ex))

    def build_sql(self, ast_node):
        generator = SqlGenerator()
        generator.visit(ast_node)
        return generator.to_sql()


def extract_error(exeption):
    line = str(exeption).split('\n')[0].strip()
    result = NOT_EXSITS_ERROR.match(line)
    if result:
        kind, name = result.groups()
        kind = kind[0].upper() + kind[1:]
        return '{} "{}" does not exist'.format(kind, name), True
    result = SYNTAX_ERROR.match(line)
    print(line, result)
    if result:
        identifier = result.group(1)
        return 'Syntax error at or near "{}"'.format(identifier), True
    return str(exeption), False

