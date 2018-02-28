from mql.common import schema


def test_simple_source():
    db = schema.SourceSchema(name='source_name')
    assert db.tables == []
    assert db.name == 'source_name'
    data = db.serialize()
    assert data['tables'] == []
    assert data['name'] ==  'source_name'


def test_add_table_to_source():
    db = schema.SourceSchema('source_name')
    db.add_table(schema.Table('table_name'))
    assert len(db.tables) == 1
    assert db.tables[0].name == 'table_name'


def test_simple_table():
    table = schema.Table(name='table_name')
    assert table.columns == []
    data = table.serialize()

    assert data['name'] ==  'table_name'
    assert data['columns'] == []
    assert data['constraints'] == []



def test_add_column_to_table():
    table = schema.Table('table_name')
    table.add_column(schema.Column('column1', 'type1'))
    table.add_column(schema.Column('column2', 'type2'))
    columns = table.columns
    assert len(columns) == 2
    assert columns[0].name == 'column1'
    assert columns[0].type == 'type1'
    assert columns[1].name == 'column2'
    assert columns[1].type == 'type2'

    data = columns[0].serialize()

    assert data['name'] ==  'column1'
    assert data['type'] ==  'type1'
    assert data['not_null'] ==  False
    assert data['default_value'] == None
    assert data['length'] == -1
    assert data['enum'] == []
    assert data['is_primary'] == False
