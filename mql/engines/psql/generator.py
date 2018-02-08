from mql.common.traverse import NodeVisitor


class Buffer:
    def __init__(self):
        self._buff = []
        self._queue = []

    def append(self, text):
        self._flush()
        self._buff.append(text)

    def last(self):
        return self._buff[:-1]

    def to_sql(self):
        self._flush()
        return ''.join(self._buff)

    def _flush(self):
        while len(self._queue):
            self._buff.append(self._queue.pop());


class Printer(NodeVisitor):
    def __init__(self):
        self._buff = []

    def token(self, item):
        self.append(item)
        self.space()

    def append(self, item):
        self._buff.append(item)

    def visitList(self, items, separator=','):
        for i, item in enumerate(items):
            self.visit(item)
            if i < len(items) - 1:
                self._buff.append(separator)
                self.space()
        self.space()

    def space(self):
        if self._buff[:-1] != ' ':
            self._buff.append(' ')

    def get_value(self):
        return ''.join(self._buff)

class SqlGenerator(Printer):
    def to_sql(self):
        return self.get_value()

    def visit_SelectStatement(self, node):
        self.append('SELECT array_to_json(array_agg(row_to_json(data)))::text FROM (SELECT ')
        self.visitList(node.results)
        self.visit(node.table)
        self.visit(node.where)
        self.visit(node.order)
        self.visit(node.limit)
        self.visit(node.offset)
        self.append(') as data')

    def visit_SelectIdentifier(self, node):
        name = node.name if not node.alias else node.name + ' as ' + node.alias
        self.append(name)

    def visit_SelectTable(self, node):
        self.token('FROM')
        self.append(node.name)
        self.space()

    def visit_SelectWhere(self, node):
        self.token('WHERE')
        self.visit(node.condition)
        self.space()

    def visit_BinaryExpression(self, node):
        self.append('(')
        self.visit(node.left)
        self.append(node.operator)
        self.visit(node.right)
        self.append(')')

    def visit_LogicalExpression(self, node):
        self.visit(node.left)
        self.append(node.operator)
        self.visit(node.right)

    def visit_Identifier(self, node):
        self.append(node.name)

    def visit_IntNumber(self, node):
        self.append(str(node.value))

    def visit_String(self, node):
        self.append("'{}'".format(node.value))

    def visit_Placeholder(self, node):
        self.token('%s')

    def visit_SelectOrder(self, node):
        self.token('ORDER BY')
        self.visitList(node.items)

    def visit_SelectOrderItem(self, node):
        self.token(node.name)
        self.append(node.direction)

    def visit_SelectLimit(self, node):
        self.token('LIMIT')
        self.token(str(node.value))

    def visit_SelectOffset(self, node):
        self.token('OFFSET')
        self.token(str(node.value))
