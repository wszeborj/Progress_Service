import strawberry
from ..graphql.queries import Query
from ..graphql.mutations import Mutation

schema = strawberry.Schema(query=Query, mutation=Mutation)
