"""Main FastAPI application for Progress Service."""
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter

from .core.config import settings
from .db.session import engine
from .db.base import Base
from .graphql.queries import Query
from .graphql.mutations import Mutation
from .graphql_context import get_context


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print("Starting...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    print("Stopping...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Progress tracking service for online learning platform with GraphQL API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)


graphql_app = GraphQLRouter(
    schema, 
    graphiql=settings.graphql_playground,
    context_getter=get_context
)

app.include_router(graphql_app, prefix=settings.graphql_path)


@app.get("/", tags=["Root"])
def health_check() -> dict[str, str]:
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
        "graphql_endpoint": f"{settings.graphql_path}",
        "graphql_playground": f"{settings.graphql_path}" if settings.graphql_playground else None,
    }

