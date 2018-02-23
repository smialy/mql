from mql.common import schema

def test_simple_schema():
    sch = schema.Schema(dict(
        name='schema_name',
        label='Schema label',
        description='Schema description'
    ))
    assert sch.sources == []

    assert sch.name ==  'schema_name'
    assert sch.label == 'Schema label'
    assert sch.description == 'Schema description'

    data = sch.serialize()

    assert data['sources'] == []

    assert data['name'] ==  'schema_name'
    assert data['label'] == 'Schema label'
    assert data['description'] == 'Schema description'

def test_default_schema():
    sch = schema.Schema()
    assert sch.sources == []

    assert sch.name ==  'default'
    assert sch.label == 'default'
    assert sch.description == ''

    data = sch.serialize()

    assert data['sources'] == []

    assert data['name'] ==  'default'
    assert data['label'] == 'default'
    assert data['description'] == ''


def test_simple_source():
    db = schema.Source(dict(
        name='source_name',
        label='Source label',
        description='Description'
    ))
    assert db.tables == []

    assert db.name ==  'source_name'
    assert db.label == 'Source label'
    assert db.description == 'Description'

    data = db.serialize()

    assert data['tables'] == []

    assert data['name'] ==  'source_name'
    assert data['label'] == 'Source label'
    assert data['description'] == 'Description'

def test_default_source():
    db = schema.Source(dict(
        name='source_name'
    ))
    assert db.name ==  'source_name'
    assert db.label == 'source name'
    assert db.description == ''


def test_add_table_to_source():
    db = schema.Source(dict(
        name='source_name'
    ))
    db.add_table(schema.Table(dict(
        name='table_name'
    )))
    assert len(db.tables) == 1
    assert db.tables[0].name == 'table_name'


def test_simple_table():
    table = schema.Table(dict(
        name='table_name',
        label='Table label',
        description='Table description'
    ))
    assert table.columns == []
    assert table.relations == []
    assert len(table.primary_columns) == 0

    assert table.name ==  'table_name'
    assert table.label == 'Table label'
    assert table.description == 'Table description'

    data = table.serialize()

    assert data['columns'] == []
    assert data['relations'] == []
    assert data['primary_keys'] == []

    assert data['name'] ==  'table_name'
    assert data['label'] == 'Table label'
    assert data['description'] == 'Table description'


def test_default_table():
    table = schema.Table(dict(
        name='table_name',
    ))
    assert table.name ==  'table_name'
    assert table.label == 'table name'
    assert table.description == ''
    assert len(table.primary_columns) == 0


def test_add_column_to_table():
    table = schema.Table(dict(
        name='table_name',
    ))
    table.add_column(schema.Column(dict(
        type='type1',
        name='column1',
        is_primary=True
    )))
    table.add_column(schema.Column(dict(
        type='type2',
        name='column2'
    )))
    columns = table.columns
    assert len(columns) == 2
    assert columns[0].name == 'column1'
    assert columns[1].name == 'column2'
    assert len(table.primary_columns) == 1
    assert table.primary_columns[0].name == 'column1'


def test_simple_column():
    column = schema.Column(dict(
        type='column type',
        name='column_name',
        label='Column label',
        description='Column description'
    ))
    assert column.type ==  'column type'
    assert column.is_primary ==  False

    assert column.name ==  'column_name'
    assert column.label == 'Column label'
    assert column.description == 'Column description'

    data = column.serialize()

    assert data['type'] ==  'column type'
    assert data['is_primary'] ==  False

    assert data['name'] ==  'column_name'
    assert data['label'] == 'Column label'
    assert data['description'] == 'Column description'


def test_default_column():
    column = schema.Column(dict(
        type='column type',
        name='column_name'
    ))
    assert column.type ==  'column type'
    assert column.is_primary ==  False

    assert column.name ==  'column_name'
    assert column.label == 'column name'
    assert column.description == ''
