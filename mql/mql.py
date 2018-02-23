import sys
import traceback

from mql.parser.parser import parse, expression
from mql.validation import validate
from mql.common.traverse import NodeTransformer, NodeVisitor
from mql.common import ast, errors
from mql.common.schema import Schema


class Mql:
    def __init__(self, databases=None, sources=None, default_database='default'):
        self._schema = Schema()
        self._sources = sources or []
        self._transformers = [
            DatabaseTransformer(default_database)
        ]
        if databases:
            for db in databases:
                self.add_database(db)

    def add_source(self, source):
        self._sources.append(source)

    def add_database(self, database):
        self._schema.add_database(database)

    def add_transformer(self, transformer):
        self._transformers.append(transformer)

    async def execute(self, query, params=None):
        try:
            ast_node = parse(query)
            for transformer in self._transformers:
                ast_node = transformer.visit(ast_node)

            context = ExecutionContext(
                self._sources,
                self._schema,
                ast_node,
                params,
                query
            )
            executor = get_executor(context.ast_node)
            return ExecuteResult(await executor.execute(context))
        except Exception as ex:
            # print(ex)
            # exc_type, exc_value, exc_traceback = sys.exc_info()
            # print(exc_type, exc_value)
            # traceback.print_tb(exc_traceback)
            return ExecuteResult(errors=[ex])

def get_executor(ast_node):
    Excecutor = ExcecutorFinder().visit(ast_node)
    return Excecutor()


class ExecutionContext:
    def __init__(self, sources, schema, ast_node, params, query):
        self.errors = []
        self.sources = sources
        self.schema = schema
        self.ast_node = ast_node
        self.params = params
        self.query = query

    def report_error(self, error):
        self.errors.append(error)


class IExcecutor:
    def execute(self, context):
        pass


class SourceExcecutor(IExcecutor):
    async def execute(self, context):
        source = self._find_source(context)
        return await source.execute(
            context.ast_node, context.params
        )

    def _find_source(self, context):
        database_name = context.ast_node.table.database
        for source in context.sources:
            if source.match(database_name):
                return source
        raise errors.MqlError('Not found database: {}'.format(database_name))


class DatabasesExcecutor(IExcecutor):
    async def execute(self, context):
        databases = context.schema.databases
        return [db.name for db in databases]


class DescribeExcecutor(IExcecutor):
    async def execute(self, context):
        database = self._find_database(context)
        return database.serialize()

    def _find_database(self, context):
        database_name = context.ast_node.database.name
        databases = context.schema.databases
        for database in databases:
            if database.name == database_name:
                return database
        raise errors.MqlError('Not found database: {}'.format(database_name))


class ExecuteResult:
    def __init__(self, data=None, errors=None):
        self.data = data
        self.errors = errors
        self.encoded = isinstance(data, str)

    def has_errors():
        return bool(self.errors)


class ExcecutorFinder(NodeVisitor):

    def visit_SelectStatement(self, node):
        return SourceExcecutor

    def visit_ShowDatabasesStatement(self, node):
        return DatabasesExcecutor

    def visit_ShowTablesStatement(self, node):
        return DescribeExcecutor


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
