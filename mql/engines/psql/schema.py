# import os
import re
import collections
from pathlib import Path
from collections import defaultdict
from mql.common import schema


_sql_file = Path(__file__).parent / 'schema.sql'
with open(_sql_file) as f:
    SQL = f.read()

# https://www.postgresql.org/docs/10/static/catalog-pg-class.html
# pg_catalog.pg_class.relkind
CLASS_KIND_TABLE = 'r'
CLASS_KIND_INDEX = 'i'
CLASS_KIND_SEQUENCE = 'S'
CLASS_KIND_VIEW = 'v'
CLASS_KIND_MATERIALIZED_VIEW = 'm'
CLASS_KIND_FOREIGN_CLASS = 'f'
CLASS_KIND_COMPOSITE = 'c'
CLASS_KIND_TOAST_TABLE = 't'
CLASS_KIND_PARTITIONED = 'p'


# https://www.postgresql.org/docs/10/static/catalog-pg-constraint.html
# pg_catalog.pg_constraint.contype
CONSTRAINT_TYPE_CHECK = 'c'
CONSTRAINT_TYPE_FOREIGN_KEY = 'f'
CONSTRAINT_TYPE_PRIMARY_KEY = 'p'
CONSTRAINT_TYPE_UNIQUE = 'u'
CONSTRAINT_TYPE_TRIGGER = 't'
CONSTRAINT_TYPE_EXCLUSION = 'x'

# https://www.postgresql.org/docs/10/static/catalog-pg-type.html
TYPE_BASE = 'b'
TYPE_COMPOSITE = 'c'
TYPE_DOMAIN = 'd'
TYPE_ENUM = 'e'
TYPE_PSEUDO = 'p'
TYPE_RANGE = 'r'

class Node:
    pass

class EnumNode(Node):
    def __init__(self, data):
        self.id = data['type_id']
        self.name = data['name']
        self._labels = [data['label']]

    def add_label(self, label):
        self._labels.append(label)

    @property
    def labels(self):
        return self._labels[:]

    def __repr__(self):
        return 'EnumNode(id={} labels={} name={})'.format(self.id, self._labels, self.name)

class TypeNode(Node):
    def __init__(self, data):
        self.id = data['id']
        self.kind = data['kind']
        self.name = data['name']

    @property
    def is_enum(self):
        return self.kind == TYPE_ENUM

    def __repr__(self):
        return 'TypeNode(id={} kind={} name={})'.format(self.id, self.kind, self.name)

class ConstraintNode(Node):
    def __init__(self, data):
        self.kind = data['kind']
        self.name = data['name']
        self.class_id = data['class_id']
        self.fclass_id = data['fclass_id']
        self.refs = data['conkey']
        self.frefs = data['confkey']

    def __repr__(self):
        return 'ConstraintNode(kind={} name={} class_id={} fclass_id={} refs={} frefs={})'.format(
            self.kind, self.name, self.class_id, self.fclass_id, self.refs, self.frefs)

class ClassNode(Node):
    def __init__(self, data):
        self.id = data['id']
        self.kind = data['kind']
        self.name = data['name']
        self.attrs = []
        self.type = None
        self.namespace = None

    def is_table_like(self):
        return self.kind in (
            CLASS_KIND_TABLE,
            CLASS_KIND_VIEW,
            CLASS_KIND_MATERIALIZED_VIEW
        )

    def __repr__(self):
        return 'ClassNode(id={} kind={} name={} namespace={} type={})'.format(
            self.id, self.kind, self.name, self.namespace, self.type)


class AttrNode(Node):
    def __init__(self, data):
        self.name = data['name']
        self.class_id = data['class_id']
        self.type_id = data['type_id']
        self.stype = data['stype']
        self.svalue = data['svalue']
        self.num = data['num']
        self.not_null = data['notnull']
        self.enum = None
        self.type = None

    def __repr__(self):
        return 'AttrNode(name={} stype={} svalue={} type={})'.format(
            self.name, self.stype, self.svalue, self.type)



class NamespaceNode(Node):
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self._classes = []

    def add_class(self, node):
        self._classes.append(node)

    def __str__(self):
        return 'NamespaceNode(id={} name={})'.format(self.id, self.name)


class Builder:
    def __init__(self):
        self.nss = []
        self.types = []
        self.classes = []
        self.attrs = []
        self.constraints = []
        self.enums = []

    def get_tables(self):
        for clazz in self.classes:
            if clazz.is_table_like():
                name = '{}.{}'.format(clazz.namespace.name, clazz.name)
                table = schema.Table(name, clazz.kind)
                for column in self.get_columns(clazz.id):
                    table.add_column(column)
                yield table

    def add(self, data):
        method_name = 'add_{}'.format(data['type'].lower())
        getattr(self, method_name)(data)

    def add_namespace(self, data):
        self.nss.append(NamespaceNode(data))

    def find_namespace(self, data):
        namespace_id = data['namespace_id']
        for node in self.nss:
            if node.id == namespace_id:
                return node

    def add_type(self, data):
        self.types.append(TypeNode(data))

    def find_type(self, data):
        type_id = data['type_id']
        for node in self.types:
            if node.id == type_id:
                return node

    def find_class(self, data):
        class_id = data['class_id']
        for node in self.classes:
            if node.id == class_id:
                return node

    def get_attr(self, class_id):
        for node in self.attrs:
            if node.class_id == class_id:
                return node

    def add_enum(self, data):
        type_id = data['type_id']
        for node in self.enums:
            if node.id == type_id:
                node.add_label(data['label'])
                return
        self.enums.append(EnumNode(data))

    def add_class(self, data):
        node = ClassNode(data)
        node.type = self.find_type(data)
        node.namespace = self.find_namespace(data)
        print(node)
        self.classes.append(node)

    def add_attribute(self, data):
        node = AttrNode(data)
        # node.clazz = self.find_class(data)
        node.type = self.find_type(data)
        self.attrs.append(node)

    def add_constraint(self, data):
        node = ConstraintNode(data)
        node.attr = self.get_attr(data['class_id'])
        print(node)
        self.constraints.append(node)

    def get_schema(self):
        db = schema.Database()
        for table in self.get_tables():
            db.add_table(table)
        return db

    def get_namespace(self, namespace_id):
        for ns in self.nss:
            if ns.id == namespace_id:
                return ns

    def get_attrs(self, class_id):
        for attr in self.attrs:
            if attr.class_id == class_id:
                node = self.get_type(attr.type_id)
                if node.is_enum:
                    attr.enum = self.get_enum(attr.type_id)
                yield attr

    def get_enum(self, type_id):
        for node in self.enums:
            if node.id == type_id:
                return node

    def get_type(self, type_id):
        for type in self.types:
            if type.id == type_id:
                return type

    def get_columns(self, class_id):
        for attr in self.get_attrs(class_id):
            kind, value, length = parse_attr(attr)
            column = schema.Column(
                attr.name,
                kind,
                value,
                attr.not_null,
                False,
                length
            )
            if attr.enum:
                for label in attr.enum.labels:
                    column.add_enum(label)

            # print('*'*100)
            # print(attr)
            # print(column.serialize())
            yield column

async def load_schema(connection):
    rows = await connection.fetchall(SQL)
    builder = Builder()
    for row in rows:
        builder.add(row[0])
    return builder.get_schema()


MATCH_VARCHAR = re.compile(r'character varying\((\d+)\)', re.I)
MATCH_TEXT = re.compile(r'\'([a-z0-9_-]+)\'::[a-z_]+', re.I)


def parse_attr(node):
    # print(node)
    if node.type.name == 'int4':
        if node.svalue:
            try:
                return 'integer', int(node.svalue), -1
            except (TypeError, ValueError) as ex:
                print(ex)
        return 'integer', None, -1

    if node.type.name == 'varchar':
        m = MATCH_VARCHAR.match(node.stype)
        if m:
            return 'string', node.svalue, int(m.group(1))
        return 'string', '', -1
    if node.type.name == 'timestamp':
        return 'timestamp', None, -1
    if node.type.name == 'text' and node.svalue:
        m = MATCH_TEXT.match(node.svalue)
        if m:
            return 'string', m.group(1), -1
    if node.type.is_enum:
        print('')
        print(node)
        m = MATCH_TEXT.match(node.svalue)
        if m:
            return 'enum', m.group(1), -1
    return node.stype, node.svalue, -1
