import sys
import traceback

from mql.parser.parser import parse, expression
from mql.validation import validate
from mql.common.traverse import NodeTransformer, NodeVisitor
from mql.common import ast, errors


class Mql:
    def __init__(self, default_database='default'):
        self._sources = []
        self._transformers = [
            DatabaseTransformer(default_database)
        ]

    def add_source(self, source):
        self._sources.append(source)

    def add_transformer(self, transformer):
        self._transformers.append(transformer)

    async def execute(self, query, params=None):
        try:
            ast_node = parse(query)
            for transformer in self._transformers:
                ast_node = transformer.visit(ast_node)
            executor = self._get_executor(ast_node, params)
            return ExecuteResult(await executor.execute())
        except Exception as ex:
            print(ex)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(exc_type, exc_value)
            traceback.print_tb(exc_traceback)

            return ExecuteResult(errors=[ex])

    def _get_executor(self, ast_node, params):
        Excecutor = ExcecutorFinder().visit(ast_node)
        return Excecutor(self._sources, ast_node, params)


class IExcecutor:
    def __init__(self, sources, ast_node, params):
        self.sources = sources
        self.ast_node = ast_node
        self.params = params

    def execute(self):
        pass

class SourceExcecutor(IExcecutor):
    async def execute(self):
        source = self._find_source()
        return await source.execute(
            self.ast_node, self.params
        )

    def _find_source(self):
        database_name = self.ast_node.table.database
        for source in self.sources:
            if source.match(database_name):
                return source
        raise errors.MqlError('Not found database: {}'.format(database_name))


class DatabasesExcecutor(IExcecutor):
    async def execute(self):
        buff = []
        for source in self.sources:
            buff.append(await source.describe())
        return buff

class DescribeExcecutor(IExcecutor):

    async def execute(self):
        source = self._find_source()
        return await source.describe()

    def _find_source(self):
        database_name = self.ast_node.database.name
        for source in self.sources:
            if source.match(database_name):
                return source
        raise errors.MqlError('Not found database: {}'.format(database_name))


class ExecuteResult:
    def __init__(self, data=None, errors=None):
        self.data = data
        self.errors = errors

    def has_errors():
        return bool(self.errors)


class ExcecutorFinder(NodeVisitor):

    def visit_SelectStatement(self):
        return SourceExcecutor

    def visit_ShowDatabasesStatement(self, node):
        return DatabasesExcecutor

    def visit_ShowTablesStatement(self, node):
        return  DescribeExcecutor


class DatabaseTransformer(NodeTransformer):
    def __init__(self, default_name):
        self.default_name = default_name

    def visit_SelectStatement(self, node):
        return self.fix_table_name(node)

    def fix_table_name(self, node):
        if not node.table.database:
            name = node.table.name
            parts = name.split('.')
            if len(parts) == 3:
                node.table.database = parts.pop(0)
                node.table.name = '.'.join(parts)
            else:
                node.table.database = self.default_name
        return node
