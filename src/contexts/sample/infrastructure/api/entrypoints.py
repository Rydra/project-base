from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from starlette.responses import JSONResponse

from contexts.auth.core.domain import User
from contexts.auth.infrastructure.api.endpoints import get_current_user
from contexts.sample.core.commands.sample import CreateSample
from contexts.sample.core.queries.sample import (
    ListSamplesHandler,
    ListSamples,
    GetSampleHandler,
    GetSample,
)
from contexts.sample.infrastructure.api.dtos import (
    SampleDto,
    ListSamplesResponse,
)
from contexts.shared.command_bus import CommandBus
from contexts.shared.message import Message
from composite_root.container import provide

router = APIRouter(tags=["Sample"], prefix="")


@cbv(router)
class SampleController:
    @router.get(
        "/api/samples/",
        summary="Get all the samples",
        responses={
            400: {
                "model": Message,
                "description": "Bad request. There are any error in parameters",
            },
            500: {"model": Message, "description": "Internal server error."},
        },
    )
    async def list_samples(
        self, user: User = Depends(get_current_user)
    ) -> ListSamplesResponse:
        try:
            samples = await provide(ListSamplesHandler).run(ListSamples())
            results = ListSamplesResponse(
                results=[SampleDto.from_domain(sample) for sample in samples.results]
            )
            return results
        except Exception as e:
            return JSONResponse(content={"message": str(e)}, status_code=500)

    @router.get(
        "/api/samples/{sample_id}/",
        summary="Get a sample by ID",
        responses={
            400: {
                "model": Message,
                "description": "Bad request. There are any error in parameters",
            },
            500: {"model": Message, "description": "Internal server error."},
        },
    )
    async def get_sample(
        self, sample_id: str, user: User = Depends(get_current_user)
    ) -> SampleDto:
        try:
            sample = await provide(GetSampleHandler).run(GetSample(id=sample_id))
            return SampleDto.from_domain(sample)
        except Exception as e:
            return JSONResponse(content={"message": str(e)}, status_code=500)

    @router.post(
        "/api/samples/",
        summary="Create a new sample",
        status_code=201,
        responses={
            400: {
                "model": Message,
                "description": "Bad request. There are any error in parameters",
            },
            500: {"model": Message, "description": "Internal server error."},
        },
    )
    async def create_sample(self, user: User = Depends(get_current_user)) -> SampleDto:
        try:
            command = CreateSample(attribute="value")
            sample = await CommandBus().asend(command)

            return SampleDto.from_domain(sample)
        except Exception as e:
            return JSONResponse(content={"message": str(e)}, status_code=500)
