
class _Named:
    def __init__(self, options):
        self._name = options['name']
        self._label = options.get('label', self.name.replace('_', ' '))
        self._description = options.get('description', '')

    @property
    def name(self):
        return self._name

    @property
    def label(self):
        return self._label

    @property
    def description(self):
        return self._description

    def serialize(self, **extra_data):
        data = dict(
            name=self.name,
            label=self.label,
            description=self.description
        )
        data.update(**extra_data)
        return data


class Schema(_Named):
    def __init__(self, options=None):
        if options is None:
            options = dict(name='default')
        super().__init__(options)
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
    def __init__(self, options):
        super().__init__(options)
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
    def __init__(self, options):
        super().__init__(options)
        self._columns = []
        self._relations = []
        self._primary_columns = []

    @property
    def columns(self):
        return self._columns[:]

    @property
    def relations(self):
        return self._relations[:]

    @property
    def primary_columns(self):
        return self._primary_columns[:]

    def add_column(self, column):
        self._columns.append(column)
        if column.is_primary:
            self._primary_columns.append(column)

    def add_relations(self, relation):
        self._relations.append(relation)

    def serialize(self):
        return super().serialize(
            primary_keys=[column.name for column in self._primary_columns],
            columns=[column.serialize() for column in self._columns],
            relations=[relation.serialize() for relation in self._relations]
        )


class Column(_Named):
    def __init__(self, options):
        super().__init__(options);

        self.type = options['type']
        self.is_primary = options.get('is_primary', False)

    def serialize(self):
        return super().serialize(
            type=self.type,
            is_primary=self.is_primary
        )

