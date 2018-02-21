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
# r = ordinary clazz
# i = index
# S = sequence
# t = TOAST clazz
# v = view
# m = materialized view
# c = composite type
# f = foreign clazz
# p = partitioned clazz
CLASS_KIND_TABLE = 'r'
CLASS_KIND_INDEX = 'i'
CLASS_KIND_SEQUENCE = 'S'
CLASS_KIND_VIEW = 'v'
CLASS_KIND_MATERIALIZED_VIEW = 'm'
CLASS_KIND_FOREIGN_TABLE = 'f'
CLASS_KIND_COMPOSITE_TYPE = 'c'
CLASS_KIND_TOAST_TABLE = 't'

# https://www.postgresql.org/docs/10/static/catalog-pg-constraint.html
# pg_catalog.pg_constraint.contype
CONSTRAINT_TYPE_CHECK = 'c'
CONSTRAINT_TYPE_FOREIGN_KEY = 'f'
CONSTRAINT_TYPE_PRIMARY_KEY = 'p'
CONSTRAINT_TYPE_UNIQUE = 'u'
CONSTRAINT_TYPE_TRIGGER = 't'
CONSTRAINT_TYPE_EXCLUSION = 'x'

# https://www.postgresql.org/docs/10/static/catalog-pg-type.html
# typtype is
# b for a base type
# c for a composite type (e.g., a clazz's row type)
# d for a domain
# e for an enum type
# p for a pseudo-type
# r for a range type
TYPE_BASE = 'b'
TYPE_COMPOSITE = 'c'
TYPE_DOMAIN = 'd'
TYPE_ENUM = 'e'
TYPE_PSEUDO = 'p'
TYPE_RANGE = 'r'

MATCH_VARCHAR = re.compile(r'character varying\((\d+)\)')


def is_table_like(clazz):
    return clazz.kind in (
        CLASS_KIND_TABLE,
        CLASS_KIND_VIEW,
        CLASS_KIND_MATERIALIZED_VIEW
    )


def parse_attr_stype(kind):
    m = MATCH_VARCHAR.match(kind)
    if m:
        return 'string', int(m.group(1))
    return kind, -1

class Node:
    pass


class TypeNode(Node):
    def __init__(self, data):
        self.id = data['id']
        self.kind = data['kind']
        self.name = data['name']
        self.namespace_id = data['namespace_id']


class ConstraintNode(Node):
    def __init__(self, data):
        self.kind = data['kind']
        self.name = data['name']
        self.class_id = data['class_id']
        self.fclass_id = data['fclass_id']
        self.refs = data['conkey']
        self.frefs = data['confkey']


class ClazzNode(Node):
    def __init__(self, data):
        self.id = data['id']
        self.kind = data['kind']
        self.name = data['name']
        self.type_id = data['type_id']
        self.namespace_id = data['namespace_id']
        self.namespace = None
        self.attrs = []


class AttrNode(Node):
    def __init__(self, data):
        self.name = data['name']
        self.class_id = data['class_id']
        self.type_id = data['type_id']
        self.stype = data['stype']
        self.svalue = data['svalue']
        self.num = data['num']
        self.not_null = data['notnull']


class NamespaceNode(Node):
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']


class Builder:
    def __init__(self):
        self.nss = []
        self.types = []
        self.classes = []
        self.attrs = []
        self.constraints = []

    def get_tables(self):
        for clazz in self.classes:
            if is_table_like(clazz):
                ns = self.get_namespace(clazz.namespace_id)
                name = '{}.{}'.format(ns.name, clazz.name)
                table = schema.Table(name, clazz.kind)
                for column in self.get_columns(clazz.id):
                    table.add_column(column)
                yield table

    def add(self, data):
        method_name = 'add_{}'.format(data['type'].lower())
        getattr(self, method_name)(data)

    def add_namespace(self, data):
        self.nss.append(NamespaceNode(data))

    def add_type(self, data):
        self.types.append(TypeNode(data))

    def add_class(self, data):
        self.classes.append(ClazzNode(data))

    def add_attribute(self, data):
        self.attrs.append(AttrNode(data))

    def add_constraint(self, data):
        self.constraints.append(ConstraintNode(data))

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
                yield attr

    def get_columns(self, class_id):
        for attr in self.get_attrs(class_id):
            kind, length = parse_attr_stype(attr.stype)
            yield schema.Column(
                attr.name,
                kind,
                attr.svalue,
                attr.not_null,
                False,
                length
            )


async def load_schema(connection):
    rows = await connection.fetchall(SQL)
    builder = Builder()
    for row in rows:
        builder.add(row[0])
    return builder.get_schema()