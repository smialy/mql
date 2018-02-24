import sys
import traceback

from mql.common.traverse import NodeTransformer, NodeVisitor
from mql.common import ast, errors
from mql.parser.parser import parse

class Mql:
    def __init__(self, sources=None, default_source='default'):
        self._transformers = [
            SourceTransformer(default_source)
        ]
        self._sources = [
            SourceListExcecutor(),
            SourceTableExcecutor()
        ]
        if sources:
            self.add_sources(sources)

    def add_sources(self, sources):
        for source in sources:
            self.add_source(source)

    def add_source(self, source):
        self._sources.append(source)

    def add_transformer(self, transformer):
        self._transformers.append(transformer)

    async def execute(self, query, params=None):
        try:
            ast_node = parse(query)
            for transformer in self._transformers:
                ast_node = transformer.visit(ast_node)

            source = self._find_source(ast_node)
            context = ExecutionContext(
                self._sources,
                ast_node,
                params,
                query
            )
            return ExecuteResult(await source.execute(context))
        except Exception as ex:
            print(ex)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(exc_type, exc_value)
            traceback.print_tb(exc_traceback)
            return ExecuteResult(errors=[ex])

    def _find_source(self, ast_node):
        for source in self._sources:
            if source.match(ast_node):
                return source
        raise errors.MqlError('Not found source')


class ExecutionContext:
    def __init__(self, sources, ast_node, params, query):
        self.errors = []
        self.sources = sources
        self.ast_node = ast_node
        self.params = params
        self.query = query

    def report_error(self, error):
        self.errors.append(error)


class SourceListExcecutor:
    def match(self, ast_node):
        return isinstance(ast_node, ast.ShowSourcesStatement)

    async def execute(self, context):
        sources = context.sources
        return [source.name for source in sources if not is_describe_source(source)]


def is_describe_source(source):
    return isinstance(source, (SourceListExcecutor, SourceTableExcecutor))


class SourceTableExcecutor:
    def match(self, ast_node):
        return isinstance(ast_node, ast.ShowTablesStatement)

    async def execute(self, context):
        source = self._find_source(context)
        return source.describe()

    def _find_source(self, context):
        source_name = context.ast_node.source.name
        for source in context.sources:
            if not is_describe_source(source) and source.name == source_name:
                return source
        raise errors.MqlError('Not found source')


class ExecuteResult:
    def __init__(self, data=None, errors=None):
        self.data = data
        self.errors = errors
        self.encoded = isinstance(data, str)

    def has_errors():
        return bool(self.errors)


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
