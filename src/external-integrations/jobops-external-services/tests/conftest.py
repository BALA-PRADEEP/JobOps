import pytest

from source.dal import ApplicationModels as _application_models  # noqa: F401
from source.dal import JobModels as _job_models  # noqa: F401
from source.dal.db_session import Base, engine


@pytest.fixture(scope="session", autouse=True)
def test_schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
