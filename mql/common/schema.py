
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


class Schema:
    def __init__(self):
        self._databases = []

    def find_database(self, name):
        for database in self._databases:
            if database.name == name:
                return database
        return None

    @property
    def databases(self):
        return self._databases[:]


    def match(self, ast_node):
        for database in self.databases:
            if database.match(ast_node):
                return database

    def serialize(self):
        return super().serialize(
            databases=[database.serialize() for database in self._databases]
        )


class Database(_Named):
    def __init__(self, name=''):
        super().__init__(name)
        self._tables = []

    def add_table(self, table):
        self._tables.append(table)

    @property
    def tables(self):
        return self._tables[:]

    def serialize(self):
        return super().serialize(
            tables=[table.serialize() for table in self._tables]
        )


class Table(_Named):
    def __init__(self, name, kind):
        super().__init__(name)
        self._kind = kind
        self._columns = []
        self._relations = []
        self._primary_columns = []

    @property
    def kind(self):
        return self._kind

    @property
    def columns(self):
        return self._columns[:]

    @property
    def relations(self):
        return self._relations[:]

    @property
    def primary_columns(self):
        return [column for column in self._columns if column.is_primary]

    def add_column(self, column):
        self._columns.append(column)

    def add_relations(self, relation):
        self._relations.append(relation)

    def serialize(self):
        return super().serialize(
            keys=[column.name for column in self.primary_columns],
            columns=[column.serialize() for column in self._columns]
            # relations=[relation.serialize() for relation in self._relations]
        )


class Column(_Named):
    def __init__(self, name, type, default_value=None, not_null=False, is_primary=False, length=-1):
        super().__init__(name)
        # print(type)
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

