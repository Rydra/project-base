from hamcrest import *

from contexts.sample.core.domain.domain import Sample


def test_sum():
    assert 1 == 1


async def test_sum_async(anyio_backend):
    assert_that(1, is_(1))


def test_create_aggregate():
    sample = Sample.new()
    assert_that(sample, is_not(none()))
