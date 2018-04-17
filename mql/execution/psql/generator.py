from mql.common.traverse import NodeVisitor


class NumberPlaceholder:
    def __init__(self):
        self.placeholder = 1

    def __call__(self):
        num = self.placeholder
        self.placeholder += 1
        return '${}'.format(num)


def percent_placeholder():
    return '%s'


PLACEHOLDERS = {
    'number': lambda: NumberPlaceholder(),
    'percent': lambda: percent_placeholder
}


class SqlGenerator(NodeVisitor):
    def __init__(self, placeholder='percent'):
        self.placeholder = PLACEHOLDERS[placeholder]()
        self._buff = []

    def to_sql(self):
        return self.get_value()

    def token(self, item):
        self.append(item)
        self.space()

    def append(self, item):
        self._buff.append(item)

    def space(self):
        if self._buff[:-1] != ' ':
            self._buff.append(' ')

    def get_value(self):
        return ''.join(self._buff)

    def visitList(self, items, separator=','):
        for i, item in enumerate(items):
            self.visit(item)
            if i < len(items) - 1:
                self._buff.append(separator)
                self.space()
        self.space()

    def visit_SelectStatement(self, node):
        self.append('SELECT ')
        self.append('array_to_json(array_agg(row_to_json(data)))::text ')
        self.append('FROM (SELECT ')
        self.visitList(node.results)
        self.visit(node.table)
        self.visit(node.where)
        self.visit(node.order)
        self.visit(node.limit)
        self.visit(node.offset)
        self.append(') as data')

    def visit_UpdateStatement(self, node):
        self.append('UPDATE ')
        self.visit(node.table)
        self.append('SET')
        self.space()
        self.visitList(node.columns)
        self.space()
        self.token('WHERE')
        self.visit(node.where)

    def visit_InsertStatement(self, node):
        self.append('INSERT INTO')
        self.space()
        self.visit(node.table)
        self.space()
        self.append('(')
        self.visitList(node.results)
        self.append(') VALUES (')
        self.visitList(node.values)
        self.append(')')

    def visit_DeleteStatement(self, node):
        self.append('DELETE FROM')
        self.space()
        self.visit(node.table)
        self.space()
        self.token('WHERE')
        self.visit(node.where)

    def visit_SelectIdentifier(self, node):
        name = node.name if not node.alias else node.name + ' as ' + node.alias
        self.append(name)

    def visit_SelectTable(self, node):
        self.token('FROM')
        self.append(node.name)
        self.space()

    def visit_UpdateTable(self, node):
        self.append(node.name)
        self.space()

    def visit_InsertTable(self, node):
        self.append(node.name)

    def visit_DeleteTable(self, node):
        self.append(node.name)

    def visit_UpdateColumn(self, node):
        self.append(node.name)
        self.append('=')
        self.visit(node.value)

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
        self.token(self.placeholder())

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
