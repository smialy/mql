import pytest
from mql.mql import Mql


@pytest.fixture
def mql():
    mql = Mql()
    mql.add_source(TestSource())
    return mql


@pytest.mark.asyncio
async def test_show_tables(mql):
    import ipdb; ipdb.set_trace()
    await mql.execute('SHOW TABLES test');



class TestSource:

    def match(self, name):
        return name == 'test'

    def execute(self, ast_node, params):
        pass