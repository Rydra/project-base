import pytest
from hamcrest import *
from pymongo import MongoClient
from starlette import status
from starlette.testclient import TestClient

from config.settings import settings
from main import app
from tests.integration.stubs import SampleMother


@pytest.fixture
def api_client():
    client = TestClient(app)
    with client:
        # We need to use yield instead of return in order to trigger
        # startup events in the test.
        # ref: https://fastapi.tiangolo.com/advanced/testing-events/
        yield client


@pytest.fixture(autouse=True)
def setup() -> None:
    settings.mongo_dbname = "test_db"
    yield
    client = MongoClient(settings.mongodb_dsm)
    client.drop_database("test_db")


class TestSampleApi:
    async def test_get_samples(self, api_client, anyio_backend):
        """Check if retrieve all samples correctly"""
        settings.use_cache = False
        await SampleMother().a_sample(reference="MYREF")

        response = api_client.get("/api/samples/")

        expected_response = {
            "results": contains_exactly(
                has_entries(
                    {
                        "reference": "MYREF",
                    }
                )
            )
        }

        assert_that(
            response.status_code, is_(status.HTTP_200_OK), reason=response.json()
        )
        assert_that(response.json(), expected_response)

    async def test_get_sample(self, api_client, anyio_backend):
        """Check if retrieve a sample correctly"""
        sample = await SampleMother().a_sample(
            reference="MYREF",
        )

        response = api_client.get(f"/api/samples/{sample.id}/")

        expected_response = has_entries(
            {
                "reference": "MYREF",
            }
        )

        assert_that(response.status_code, is_(status.HTTP_200_OK))
        assert_that(response.json(), expected_response)

    async def test_create_sample(self, api_client, anyio_backend):
        """Check if a sample is created correctly"""
        response = api_client.post("/api/samples/")

        assert_that(response.status_code, is_(status.HTTP_201_CREATED))
