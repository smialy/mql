import pytest
from mql.mql import Mql


@pytest.fixture
def mql():
    mql = Mql()
    mql.add_source(TestSource())
    return mql


@pytest.mark.asyncio
async def test_show_tables(mql):
    await mql.execute('SHOW SOURCE test');



class TestSource:

    @property
    def name(self):
        return 'test'

    @property
    def schema(self):
        return TestSchema()

    def match(self, ast_document):
        return name == 'test'

    def execute(self, ast_document, params):
        pass

class TestSchema:
    def describe(self):
        return None