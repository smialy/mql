import sys
import traceback

from mql.parser.parser import parse, expression
from mql.validation import validate
from mql.common.traverse import NodeTransformer, NodeVisitor
from mql.common import ast, errors
from mql.common.schema import Schema


class Mql:
    def __init__(self, executors=None, sources=None, default_source='default'):
        self._schema = Schema()
        self._executors = executors or []
        self._transformers = [
            SourceTransformer(default_source)
        ]
        if sources:
            for db in sources:
                self.add_source(db)

    def add_executor(self, source):
        self._executors.append(source)

    def add_source(self, source):
        self._schema.add_source(source)

    def add_transformer(self, transformer):
        self._transformers.append(transformer)

    async def execute(self, query, params=None):
        try:
            ast_node = parse(query)
            for transformer in self._transformers:
                ast_node = transformer.visit(ast_node)

            context = ExecutionContext(
                self._executors,
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
    def __init__(self, executors, schema, ast_node, params, query):
        self.errors = []
        self.executors = executors
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
        executor = self._find_executor(context)
        return await executor.execute(
            context.ast_node, context.params
        )

    def _find_executor(self, context):
        source_name = context.ast_node.table.source
        for executor in context.executors:
            if executor.match(source_name):
                return executor
        raise errors.MqlError('Not found source: {}'.format(source_name))


class SourcesExcecutor(IExcecutor):
    async def execute(self, context):
        sources = context.schema.sources
        return [db.name for db in sources]


class DescribeExcecutor(IExcecutor):
    async def execute(self, context):
        source = self._find_source(context)
        return source.serialize()

    def _find_source(self, context):
        source_name = context.ast_node.source.name
        sources = context.schema.sources
        for source in sources:
            if source.name == source_name:
                return source
        raise errors.MqlError('Not found source: {}'.format(source_name))


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

    def visit_ShowSourcesStatement(self, node):
        return SourcesExcecutor

    def visit_ShowTablesStatement(self, node):
        return DescribeExcecutor


class SourceTransformer(NodeTransformer):
    def __init__(self, default_name):
        self.default_name = default_name

    def visit_SelectStatement(self, node):
        return self.fix_table_name(node)

    def fix_table_name(self, node):
        if not node.table.source:
            name = node.table.name
            parts = name.split('.')
            if len(parts) == 3:
                node.table.source = parts.pop(0)
                node.table.name = '.'.join(parts)
            else:
                node.table.source = self.default_name
        return node
