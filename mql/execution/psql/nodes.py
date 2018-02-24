from mql.common.traverse import NodeVisitor

class Buffer:
    def __init__(self):
        self._buf = []
        self._queue = []

    def get_value(self):
        pass


class SqlNode(object):
    def __init__(self, sql=''):
        self._children = [sql]

    def add_node(self, node):
        node.parent = self
        self._children.append(node)

    def write(self, *sql):
        self._children.extend(sql)

    def to_sql(self):
        sql = []
        for child in self._children:
            s = child.to_sql() if isinstance(child, SqlNode) else child
            if s:
                sql.append(s)
        return ' '.join(sql)


class SqlLogic(SqlNode):
    pass


class SqlSelect(SqlNode):
    def __init__(self):
        super().__init__('SELECT')

    def to_sql(self):
        sql = super().to_sql()
        return 'SELECT array_to_json(array_agg(row_to_json(data)))::text FROM ({}) as data'.format(sql)

def get_indentifier_name(node):
    return node.name if not node.alias else node.name + ' ' + node.alias

def get_indentifier_names(nodes):
    return [get_indentifier_names(identifer)
        for identifer in nodes]


class SqlGenerator(NodeVisitor):
    def __init__(self):
        self.root = self.head = SqlNode()

    def visit_SelectStatement(self, node):
        self.root = SqlSelect()
        names = get_indentifier_names(node.results)
        self.root.write(', '.join(names))
        self.visit(node.table)
        if node.where:
            self.head = SqlNode('WHERE')
            self.root.add_node(self.head)
            self.visit(node.where)
        self.visit(node.order)
        self.visit(node.limit)
        self.visit(node.offset)

    def visit_SelectIdentifier(self, node):
        name = node.name if not node.alias else node.name + ' ' + node.alias
        self.root.write(name)

    def visit_SelectTable(self, node):
        self.root.write('FROM', node.name)

    def visit_BinaryExpression(self, node):
        head = self.head
        self.head = SqlLogic()
        head.add_node(self.head)
        self.head.write('(')
        self.visit(node.left)
        self.head.write(node.operator)
        self.visit(node.right)
        self.head = head
        self.head.write(')')

    def visit_BinaryExpression(self, node):
        head = self.head
        self.head = SqlNode()
        head.add_node(self.head)
        self.visit(node.left)
        self.head.write(node.operator)
        self.visit(node.right)
        self.head = head

    def visit_Identifier(self, node):
        self.head.write(node.name)

    def visit_IntNumber(self, node):
        self.head.write(str(node.value))

    def visit_SelectOrder(self, node):
        self.root.write('ORDER BY')
        for item in node.items:
            self.visit(item)

    def visit_SelectOrderItem(self, node):
        self.root.write(node.name, node.direction)

    def visit_SelectLimit(self, node):
        self.root.write('LIMIT', str(node.value))

    def visit_SelectOffset(self, node):
        self.root.write('OFFSET', str(node.value))
