"""GraphQL context provider for Strawberry."""
from typing import Any

from .db.session import AsyncSessionLocal

#
# async def get_context() -> dict[str, Any]:
#     """
#     Provides context for GraphQL requests.
#
#     This function is called for each GraphQL request and provides
#     the database session to resolvers. The session is created per request
#     and will be closed when the request completes.
#     """
#     # Create a new session for this request
#     # The session will be managed by the request lifecycle
#     db_session = AsyncSessionLocal()
#     return {"db_session": db_session}


async def get_context() -> dict[str, Any]:
    async with AsyncSessionLocal() as db_session:
        try:
            yield {"db_session": db_session}

            await db_session.commit()
        except:
            await db_session.rollback()

        finally:
            print("Cleanup")

