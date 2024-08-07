"""Main - houses REST API endpoint routers"""

from ariadne import graphql_sync
from fastapi import FastAPI, Request

from gql import schema

from api.routers import (
    adm_router,
    base_router,
    sat_router
)

app = FastAPI()

# initialize routers
routers = [
    adm_router,
    base_router,
    sat_router
]
for router in routers:
    app.include_router(router)


@app.post("/graphql/")
async def graphql_fn(req: Request):
    """GraphQL default endpoint routing"""
    data = await req.json()  # JSON request data

    _, result = graphql_sync(
        schema,
        data,
        context_value=data,
        debug=app.debug
    )

    return result
