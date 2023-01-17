import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.tools import merge_types

from contexts.auth.infrastructure.graphql.context import Context
from contexts.auth.infrastructure.graphql.mutations import AuthMutations
from contexts.sample.infrastructure.graphql.mutations import SampleMutations
from contexts.sample.infrastructure.graphql.queries import SampleQueries


Query = merge_types("Query", (SampleQueries,))

Mutation = merge_types("Mutation", (SampleMutations, AuthMutations))

schema = strawberry.Schema(query=Query, mutation=Mutation)


async def get_context() -> Context:
    return Context()


graphql_app = GraphQLRouter(schema, context_getter=get_context, path="/")
