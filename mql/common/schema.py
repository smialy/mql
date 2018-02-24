
class _Named:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def serialize(self, **extra_data):
        data = dict(
            name=self.name
        )
        data.update(**extra_data)
        return data

class Source(_Named):
    def __init__(self, name):
        super().__init__(name)
        self._tables = []

    def add_table(self, table):
        self._tables.append(table)

    def match(self, ast_node):
        return self.name == ast_node.table.source

    @property
    def tables(self):
        return self._tables[:]

    def serialize(self):
        return super().serialize(
            tables=[table.serialize() for table in self._tables]
        )


class Table(_Named):
    def __init__(self, name, kind, editable=True):
        super().__init__(name)
        self._kind = kind
        self._editable = editable
        self._columns = []
        self._constraints = []

    @property
    def kind(self):
        return self._kind

    @property
    def editable(self):
        return self._editable

    @property
    def columns(self):
        return list(elf._columns)

    @property
    def constraints(self):
        return list(self._constraints)

    def add_column(self, column):
        self._columns.append(column)

    def add_constraint(self, constraint):
        self._constraints.append(constraint)

    def serialize(self):
        return super().serialize(
            constraints=[constraint.serialize() for constraints in self._constraints],
            columns=[column.serialize() for column in self._columns]
        )


class Column(_Named):
    def __init__(self, name, type, default_value=None, not_null=False, is_primary=False, length=-1):
        super().__init__(name)
        self.type = type
        self.default_value = default_value
        self.not_null = not_null
        self.length = length
        self.is_primary = is_primary
        self.enum = []

    def add_enum(self, value):
        self.enum.append(value)

    def serialize(self):
        return super().serialize(
            type=self.type,
            not_null=self.not_null,
            default_value=self.default_value,
            length=self.length,
            enum=self.enum[:],
            is_primary=self.is_primary
        )

