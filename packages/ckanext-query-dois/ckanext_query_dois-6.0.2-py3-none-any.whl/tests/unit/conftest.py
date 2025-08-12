import pytest
from ckan import model

from ckanext.query_dois.model import query_doi_stat_table, query_doi_table


@pytest.fixture
def setup_db():
    for table in (query_doi_table, query_doi_stat_table):
        if not table.exists(model.meta.engine):
            table.create(model.meta.engine)
