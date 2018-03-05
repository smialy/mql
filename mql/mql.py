import sys
import traceback

from mql.common.traverse import NodeTransformer
from mql.common import ast, errors, execution
from mql.parser.parser import parse
from mql.validation import validate


class Mql:
    def __init__(self, sources, default_source='default', *, transformers=None):
        self._transformers = [
            SourceTransformer(default_source)
        ]
        self._sources = [
            SourceListExcecutor(),
            SourceTableExcecutor(),
            *sources
        ]
        if transformers:
            for transformer in transformers:
                self.add_transformer(transformer)

    def add_source(self, source):
        self._sources.append(source)

    def add_transformer(self, transformer):
        self._transformers.append(transformer)

    async def execute(self, query, params=None):
        try:
            ast_document = parse(query)
            for transformer in self._transformers:
                ast_document = transformer.visit(ast_document)

            source = self._find_source(ast_document)
            errors = validate(source.schema, ast_document, params)
            if errors:
                return execution.ExecuteResult(errors=errors)

            context = execution.ExecutionContext(
                self._sources,
                ast_document,
                params,
                query
            )
            return await source.execute(context)
        except Exception as ex:
            print(ex)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(exc_type, exc_value)
            traceback.print_tb(exc_traceback)
            return execution.ExecuteResult(errors=[ex])

    def _find_source(self, ast_document):
        for source in self._sources:
            if source.match(ast_document):
                return source
        raise errors.MqlError('Not found source')


def is_describe_source(source):
    return isinstance(source, (SourceListExcecutor, SourceTableExcecutor))


class SourceListExcecutor:
    @property
    def schema(self):
        return None

    def match(self, ast_document):
        return isinstance(ast_document, ast.ShowSourcesStatement)

    async def execute(self, context):
        sources = context.sources
        info = [source.name for source in sources if not is_describe_source(source)]
        return execution.ExecuteResult(info)


class SourceTableExcecutor:
    @property
    def schema(self):
        return None

    def match(self, ast_document):
        return isinstance(ast_document, ast.ShowSourceStatement)

    async def execute(self, context):
        source = self._find_source(context)
        return execution.ExecuteResult(source.schema.serialize())

    def _find_source(self, context):
        source_name = context.ast_document.source.name
        for source in context.sources:
            if not is_describe_source(source) and source.name == source_name:
                return source
        raise errors.MqlError('Not found source')


class SourceTransformer(NodeTransformer):

    def __init__(self, default_name):
        self.default_name = default_name

    def visit_SelectStatement(self, node):
        return self.fix_table_name(node)

    def visit_InsertStatement(self, node):
        return self.fix_table_name(node)

    def visit_UpdateStatement(self, node):
        return self.fix_table_name(node)

    def visit_DeleteStatement(self, node):
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
