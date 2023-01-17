from hamcrest import *


def test_sum():
    assert 1 == 1


async def test_sum_async(anyio_backend):
    assert_that(1, is_(1))
