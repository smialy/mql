class Node:
    __slots__ = ()


class Expresion(Node):
    pass


class Identifier(Node):
    __slots__ = ('name', )

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Identifier name="{}">'.format(self.name)


class Placeholder(Node):

    def __repr__(self):
        return '<Placeholder>'


class BinaryExpression(Expresion):  # ==, >=, <=, !=
    __slots__ = ('operator', 'left', 'right')

    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def __repr__(self):
        return '<BinaryExpression {}{}{}">'.format(
            repr(self.left), self.operator, repr(self.right)
        )


class LogicalExpression(Expresion):  # AND, OR
    __slots__ = ('operator', 'left', 'right')

    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def __repr__(self):
        return '<LogicalExpression {}{}{}">'.format(
            repr(self.left), self.operator, repr(self.right)
        )


class UnaryExpression(Expresion):  # not
    __slots__ = ('operator', 'argument')

    def __init__(self, argument):
        self.operator = 'NOT'
        self.argument = argument

    def __repr__(self):
        return '<UnaryExpression {}{}">'.format(
            self.operator, repr(self.argument)
        )


class InExpression(Expresion):  # and, or
    __slots__ = ('items')

    def __init__(self, items):
        self.items = items

    def __repr__(self):
        return '<InExpression {}">'.format(repr(self.items))


class _Value(Node):
    __slots__ = ('value', )

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '<{} value={}">'.format(self.__class__.__name__, self.value)


class Number(_Value):
    pass

class String(_Value):
    pass

class IntNumber(Number):
    def __init__(self, value):
        super().__init__(int(value))


class FloatNumber(Number):
    def __init__(self, value):
        super().__init__(float(value))


class Statements(Node):
    __slots__ = ('statements', )

    def __init__(self):
        self.statements = []

    def add(self, stmt):
        self.statements.append(stmt)

    def __repr__(self):
        return '<Statements statements={}>'.format(repr(self.statements))


class Statement(Node):
    __slots__ = ()

    def __repr__(self):
        return '<Statement>'


class SelectStatement(Statement):
    __slots__ = ('results', 'table', 'where', 'order', 'limit', 'offset')

    def __init__(self,
        results=None,
        table=None,
        where=None,
        order=None,
        limit=None,
        offset=None
    ):
        self.results = results if results is not None else []
        self.table = table
        self.where = where
        self.order = order
        self.limit = limit
        self.offset = offset

    def __repr__(self):
        return '<SelectStatement identifier={} \
                table={} where={} order={} limit={} offset={}>'.format(
            repr(self.results),
            self.table,
            repr(self.where),
            repr(self.order),
            repr(self.limit),
            repr(self.offset)

        )


class SelectIdentifier(Node):
    __slots__ = ('name', 'alias')

    def __init__(self, name, alias=''):
        self.name = name
        self.alias = alias

    def is_wildcard(self):
        return self.name == '*'

    def __repr__(self):
        return '<SelectIdentifier name={} alias={}>'.format(
            self.name, self.alias
        )


class Table(Node):
    __slots__ = ('name', 'database')

    def __init__(self, name, database=''):
        self.name = name
        self.database = database

    def __repr__(self):
        return '<Table name={}>'.format(self.name)


class SelectTable(Table):
    def __repr__(self):
        return '<SelectTable database={} name={}>'.format(
            self.database,
            self.name
        )


class SelectWhere(Expresion):
    __slots__ = ('condition', )

    def __init__(self, condition):
        self.condition = condition

    def __repr__(self):
        return '<SelectWhere condition={}>'.format(self.condition)


class SelectOrder(Node):
    __slots__ = ('items', )

    def __init__(self, items=None):
        self.items = items if items is not None else []

    def add(self, item):
        self.items.append(item)

    def __repr__(self):
        return '<SelectOrder items={}>'.format(repr(self.items))


class SelectOrderItem(Node):
    __slots__ = ('name', 'direction')

    def __init__(self, name, direction='ASC'):
        self.name = name
        direction = direction.upper() if direction else 'ASC'
        self.direction = 'DESC' if direction == 'DESC' else 'ASC'

    def __repr__(self):
        return '<SelectOrderItem name={} direction={}>'.format(
            self.name, self.direction
        )


class SelectLimit(Node):
    __slots__ = ('value', )

    def __init__(self, value):
        self.value = int(value)

    def __repr__(self):
        return '<SelectLimit value={}>'.format(self.value)


class SelectOffset(Node):
    __slots__ = ('value', )

    def __init__(self, value):
        self.value = int(value)

    def __repr__(self):
        return '<SelectOffset value={}>'.format(self.value)


class InsertStatement(Statement):
    __slots__ = ('table', 'results', 'values')

    def __init__(self, table, indentifiers, values):
        self.table = table
        self.results = indentifiers
        self.values = values

    def __repr__(self):
        return '<InsertStatement table={} results={} values={}">'.format(
            repr(self.table), repr(self.results), repr(self.values)
        )


class UpdateStatement(Statement):
    __slots__ = ('table', 'columns', 'where')

    def __init__(self, table, columns, where):
        self.table = table
        self.columns = columns
        self.where = where

    def __repr__(self):
        return '<UpdateStatement table={} columns={} where={}">'\
        .format(
            repr(self.table),
            repr(self.columns),
            repr(self.where)
        )


class UpdateTable(Table):
    def __repr__(self):
        return '<UpdateTable database={} name={}>'.format(
            self.database,
            self.name
        )


class UpdateColumn(Node):
    __slots__ = ('name', 'value')

    def __init__(self, name, value):
        self.name = name
        self.value = value


class DeleteStatement(Statement):
    __slots__ = ('table', 'where')

    def __init__(self, table, where):
        self.table = table
        self.where = where

    def __repr__(self):
        return '<UpdateStatement table={} where={}">'.format(
            repr(self.table), repr(self.where)
        )


class DeleteTable(Table):
    def __repr__(self):
        return '<DeleteTable database={} name={}>'.format(
            self.database,
            self.name
        )


class _ShowStatement(Statement):
    pass


class ShowDatabasesStatement(_ShowStatement):
    __slots__ = []

    def __repr__(self):
        return '<ShowDatabases>'


class ShowTablesStatement(_ShowStatement):
    __slots__ = ('database', )

    def __init__(self, database):
        self.database = database

    def __repr__(self):
        return '<ShowTableStatement database={}>'.format(
            repr(self.database)
        )


class Database(Node):
    __slots__ = ('name', )

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Database name={}>'.format(self.name)


class ShowTableStatement(_ShowStatement):
    __slots__ = ('table', )

    def __init__(self, table):
        self.table = table

    def __repr__(self):
        return '<DescribeTableStatement table={}>'.format(repr(self.table))


class ShowTable(Table):
    def __repr__(self):
        return '<ShowTable name={}>'.format(self.name)


def is_statement(node):
    return isinstance(node, Statement)


def is_show_statement(node):
    return isinstance(node, _ShowStatement)


def is_show_database_statement(node):
    return isinstance(node, ShowDatabasesStatement)