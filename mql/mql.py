from mql.parser.parser import parse, expression
from mql.validation import validate
from mql.common.traverse import NodeTransformer
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
            errors = validate(self._sources, ast_node)
            if errors:
                return ExecuteResult(errors=errors)
            else:
                source = self.find_source(ast_node)
                return ExecuteResult(await source.execute(ast_node, params))
        except Exception as ex:
            return ExecuteResult(errors=[ex])

    def find_source(self, ast_node):
        database_name = ast_node.table.database
        for source in self._sources:
            if source.match(database_name):
                return source
        raise errors.MqlError('Not found database: {}'.format(database_name))


class ExecuteResult:
    def __init__(self, data=None, errors=None):
        self.data = data
        self.errors = errors

    def has_errors():
        return bool(self.errors)


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