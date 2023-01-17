import strawberry
from typing import TypeAlias

from pyvaru import ValidationException

from contexts.auth.infrastructure.graphql.context import IsAuthenticated
from contexts.sample.core.commands.sample import CreateSample
from contexts.shared.command_bus import CommandBus


@strawberry.type
class MutationResult:
    ok: bool
    error: str | None


@strawberry.type
class SampleCreatedSuccess:
    id: str


@strawberry.type
class AddGuessSuccess:
    ok: bool


@strawberry.type
class ErrorMessage:
    label: str
    error_messages: list[str]


@strawberry.type
class ValidationError:
    message: str
    errors: list[ErrorMessage]

    @staticmethod
    def from_exception(e: ValidationException) -> "ValidationError":
        return ValidationError(
            message=e.message,
            errors=[
                ErrorMessage(label=label, error_messages=error_messages)
                for label, error_messages in e.validation_result.errors.items()
            ],
        )


@strawberry.type
class Error:
    reason: str


CreateSampleResponse: TypeAlias = strawberry.union(  # type: ignore
    "CreateSampleResponse", [SampleCreatedSuccess, ValidationError, Error]  # type: ignore
)

AddGuessResponse: TypeAlias = strawberry.union(  # type: ignore
    "AddGuessResponse", [AddGuessSuccess, ValidationError, Error]
)


@strawberry.input
class CreateSampleInput:
    attribute: str | None


@strawberry.type
class SampleMutations:
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def create_sample(self, input: CreateSampleInput) -> CreateSampleResponse:
        try:
            command = CreateSample(attribute=input.attribute)
            sample = await CommandBus().asend(command)

            return SampleCreatedSuccess(id=sample.id)
        except Exception as e:
            return Error(reason=str(e))
